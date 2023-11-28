#!/usr/bin/env python

# Copyright (c) 2023 PaddlePaddle Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import argparse
import os
import platform
import queue
import re
import sys
import threading
import time
from typing import List

import erniebot_agent
import gradio as gr
from erniebot_agent.tools.img_main import ImageGenerateTool
from IPython.display import clear_output as clear

import erniebot

INSTRUCTION = """你的指令是为我提供一个基于《{SCRIPT}》剧情的在线RPG游戏体验。\
在这个游戏中，玩家将扮演《{SCRIPT}》剧情关键角色，你可以自行决定玩家的角色。\
游戏情景将基于《{SCRIPT}》剧情。这个游戏的玩法是互动式的，并遵循以下特定格式：

<场景描述>：根据玩家的选择，故事情节将按照《{SCRIPT}》剧情的线索发展。你将描述角色所处的环境和情况。剧情发展请尽量快，场景描述不少于30字。

<场景图片>：对于每个场景，你将创造一个概括该情况的图像。在这个步骤你需要调用画图工具ImageGenerateTool。\
generatetool的入参为根据场景描述总结的图片内容，请按generatetool('query')输出。

<选择>：在每次互动中，你将为玩家提供三个行动选项，分别标为1、2、3，以及第四个选项“输入玩家自定义的选择”。故事情节将根据玩家选择的行动进展。\
如果一个选择不是直接来自《{SCRIPT}》剧情，你将创造性地适应故事，最终引导它回归原始情节。

整个故事将围绕《{SCRIPT}》丰富而复杂的世界展开。每次互动必须包括<场景描述>、<场景图片>和<选择>。所有内容将以中文呈现。\
你的重点将仅仅放在提供场景描述，场景图片和选择上，不包含其他游戏指导。场景尽量不要重复，要丰富一些。

当我说游戏开始的时候，开始游戏。每次只要输出一组互动，【不要自己生成互动】。"""

# 创建消息队列用于传递文件地址
FILE_QUEUE = queue.Queue()


def parse_args():
    parser = argparse.ArgumentParser(prog="erniebot-RPG")
    parser.add_argument("--access-token", type=str, default=None, help="Access token to use.")
    parser.add_argument("--game", type=str, default="射雕英雄传", help="story name")
    parser.add_argument("--model", type=str, default="ernie-bot-4", help="Model name")
    parser.add_argument(
        "--db-dir",
        type=str,
        default="/Users/tanzhehao/Documents/ERINE/ERNIE-Bot-SDK/examples/douluo_index_hf",
    )
    return parser.parse_args()


def get_img(tool) -> None:
    # TODO：如果不符合规范格式的报错
    global FILE_QUEUE

    FILE_QUEUE.put(eval(tool))

    # import webuiapi

    # api = webuiapi.WebUIApi(host="10.21.226.177", port=8544)

    # result1 = api.txt2img(
    #     prompt=prompt,
    #     negative_prompt="ugly, out of frame",
    #     seed=1003,
    #     styles=["anime"],
    #     cfg_scale=7,
    # )
    # # result1.images
    # # image is shorthand for images[0]
    # result1.image.save("squirrel.png")


def _clear_screen():
    os.system("cls" if platform.system() == "Windows" else "clear")
    if "ipykernel" in sys.modules:
        clear()


generatetool = ImageGenerateTool()


class RPGGame:
    def __init__(
        self,
        model: str,
        script: str,
        db: str = None,
        access_token: str = None,
        max_round: int = 2,
    ) -> None:
        self.model = model
        self.script = script
        self.chat_history = [
            {"role": "user", "content": INSTRUCTION.format(SCRIPT=self.script)},
            {"role": "assistant", "content": f"好的，我将为你提供《{self.script}》沉浸式图文RPG场景体验。"},
        ]
        self.db = db
        self.max_round = max_round
        erniebot.api_type = "aistudio"
        erniebot.access_token = os.getenv("EB_ACCESS_TOKEN") if not access_token else access_token

    def chat(self, query: str) -> str:
        "Use this function to chat with ERNIE BOT"
        # if self.db:
        #     if '开始游戏' in query:
        #         actual_query = query + '\n\n你可以参考以下剧情片段:\n' \
        #             + self.db.docstore.search(db.index_to_docstore_id[0]).page_content.replace('\n','')

        #     else:
        #         search_query = self._extract_scene(query)
        # erniebot_agent.logger.debug('search query:'+search_query)

        # actual_query = \
        #     query + '\n\n根据我的选择继续生成一轮仅含包括<场景描述>、<场景图片>和<选择>的互动，你可以根据以下剧情片段:\n'\
        #     + self.db.similarity_search(search_query)[0].page_content.replace('\n','') \
        # + '\n\n片段2:\n' \
        # + self.db.similarity_search('开始游戏')[1].page_content.replace('\n','')

        # erniebot_agent.logger.info('actual_query'+actual_query)
        actual_query = query + "根据我的选择继续生成一轮仅含包括<场景描述>、<场景图片>和<选择>的互动。"
        self.chat_history.append({"role": "user", "content": actual_query})
        response = erniebot.ChatCompletion.create(
            model=self.model,
            messages=self.chat_history,
            system=f"你是《{self.script}》沉浸式图文RPG场景助手，能够生成图文剧情，并给出玩家选项，整个故事将围绕《{self.script}》丰富而复杂的世界展开。\
                每次互动必须包括<场景描述>、<场景图片>和<选择>。每次仅生成一轮互动，不要自己生成玩家的选择",
        )

        # 修改回原来的query
        # self.chat_history[-1] = ({"role": "user", "content": query})

        if len(self.chat_history) >= (self.max_round + 1) * 2:
            for _ in range(2):
                self.chat_history.pop(2)

        self.chat_history.append({"role": "assistant", "content": response.get_result()})
        return response.get_result()

    def chat_stream(self, query: str) -> None:
        "Use this function to chat with ERNIE BOT"
        self.chat_history.append({"role": "user", "content": query})
        response = erniebot.ChatCompletion.create(model=self.model, messages=self.chat_history, stream=True)
        result = ""

        for resp in response:
            result += resp.get_result()
            # _clear_screen()
            for s in resp.get_result():
                # 用缓冲区来达成一个字一个字输出的流式
                # print(s,end='',flush=True)
                yield s
                time.sleep(0.005)
            # yield resp.get_result()

        self.chat_history.append({"role": "assistant", "content": result})

    def clear(self) -> None:
        self.chat_history = [
            {"role": "user", "content": INSTRUCTION.format(SCRIPT=self.script)},
            {"role": "assistant", "content": f"好的，我将为你提供《{self.script}》沉浸式图文RPG场景体验。"},
        ]

    def lauch_gradio(self) -> None:
        with gr.Blocks() as demo:
            context_chatbot = gr.Chatbot(label=self.script, height=750)
            input_text = gr.Textbox(label="消息内容", placeholder="请输入...")

            with gr.Row():
                start_buttton = gr.Button("开始游戏")
                remake_buttton = gr.Button("重新开始")

            remake_buttton.click(self.clear)
            start_buttton.click(self._gradio_chat, start_buttton, [input_text, context_chatbot])
            input_text.submit(self._gradio_chat, input_text, [input_text, context_chatbot])

        demo.launch()

    def lauch_gradio_stream(self) -> None:
        with gr.Blocks() as demo:
            context_chatbot = gr.Chatbot(label=self.script, height=750)
            input_text = gr.Textbox(label="消息内容", placeholder="请输入...")

            with gr.Row():
                start_buttton = gr.Button("开始游戏")
                remake_buttton = gr.Button("重新开始")

            remake_buttton.click(self.clear)
            start_buttton.click(
                self._handle_gradio_chat,
                [start_buttton, context_chatbot],
                [input_text, context_chatbot],
                queue=False,
            ).then(self._handle_gradio_stream, context_chatbot, context_chatbot)
            input_text.submit(
                self._handle_gradio_chat,
                [input_text, context_chatbot],
                [input_text, context_chatbot],
                queue=False,
            ).then(self._handle_gradio_stream, context_chatbot, context_chatbot)
        demo.launch()

    def _handle_gradio_chat(self, user_message, history) -> tuple[str, List[tuple[str, str]]]:
        # 用于处理gradio的chatbot返回
        return "", history + [[user_message, None]]

    def _handle_gradio_stream(self, history) -> None:
        # 用于处理gradio的流式
        global FILE_QUEUE
        bot_message = self.chat_stream(history[-1][0])
        history[-1][1] = ""
        generate = True
        for temp_mes in bot_message:
            history[-1][1] += temp_mes
            if "选择" in history[-1][1] and "generatetool" in history[-1][1] and generate:
                gr.Info("图片生成中...")
                pattern = r"generatetool\([^)]*\)"
                tool = re.findall(pattern, history[-1][1])

                erniebot_agent.logger.info(tool)
                try:
                    thread = threading.Thread(target=get_img, args=(tool[0],))
                    thread.start()
                    generate = False
                except IndexError as e:
                    erniebot_agent.logger.error(e)
                    pass

            yield history

        else:
            thread.join()
            # TODO: gradio图片替换
            img_path = FILE_QUEUE.get()
            history[-1][1] = history[-1][1].replace(
                "generatetool",
                f"<img src='file={img_path}' alt='Example Image' style='display:block; max-width:50%; height:auto;'>",
            )
            yield history

    def _gradio_chat(self, query: str) -> tuple[str, List[tuple[str, str]]]:
        self.chat(query)
        history = []

        for i in range(2, len(self.chat_history), 2):
            history.append((self.chat_history[i]["content"], self.chat_history[i + 1]["content"]))

        return "", history

    def _extract_scene(self, query) -> str:
        "Extract scene from the chat history"
        bot_message = self.chat_history[-1]["content"]
        human_message = query

        if len(human_message) < 3:  # 输入的是数字
            human_message = bot_message[bot_message.rfind(human_message[0]) :]
            human_message = human_message[: human_message.find("。")]

        scene = bot_message[bot_message.find("场景描述") : bot_message.find("场景图片")]
        return scene + human_message


if __name__ == "__main__":
    from erniebot_agent.extensions.langchain.embeddings import ErnieEmbeddings
    from erniebot_agent.tools.SearchTool import SearchTool
    from langchain.vectorstores import FAISS

    # embeddings = ErnieEmbeddings(
    #     aistudio_access_token=os.environ.get('EB_ACCESS_TOKEN'),
    #     chunk_size=16,
    #     )
    # from langchain.embeddings import HuggingFaceEmbeddings
    # model_kwargs = {'device': 'mps'}
    # encode_kwargs = {'normalize_embeddings': True}
    # embeddings = HuggingFaceEmbeddings(
    #     model_name="shibing624/text2vec-base-chinese",
    #     model_kwargs=model_kwargs,
    #     # encode_kwargs=encode_kwargs,
    # )

    args = parse_args()
    # db = FAISS.load_local(args.db_dir, embeddings)
    # searchtool = SearchTool(db)

    game_system = RPGGame(db=None, model=args.model, script=args.game)
    game_system.lauch_gradio_stream()
