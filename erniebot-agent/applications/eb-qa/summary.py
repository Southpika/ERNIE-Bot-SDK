from typing import Union
from tqdm import tqdm
from pathlib import Path

import erniebot
import os
from openai import OpenAI

erniebot.api_type = "aistudio"
erniebot.access_token = os.getenv("EB_AGENT_ACCESS_TOKEN")
client = OpenAI(api_key='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')

md_file_path = [
    "./docs/modules/file.md",
    "./docs/modules/agents.md",
    "docs/modules/memory.md",
    "./docs/modules/message.md",
    "./docs/modules/chat_models.md",
    "./docs/modules/tools.md",
    "./docs/quickstart/agent.md",
    "./docs/quickstart/use-tool.md",
]

def read_md_file(file_path: str) -> Union[str, None]:
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            md_content = file.read()
        return md_content
    except FileNotFoundError:
        print(f"文件 '{file_path}' 不存在。")
        return None
    except Exception as e:
        print(f"读取文件时出现错误： {e}")
        return None


def write_md_file(file_path: str) -> bool:
    content = read_md_file(file_path)
    if content:
        chat_message = [{"role": "user", "content": f"请帮我给以下markdown文件生成摘要用于用户问文档内容时的检索匹配，不要超过400个字：\n{content}"}]
        # summary = erniebot.ChatCompletion.create(
        #     model = 'ernie-longtext',
        #     messages = chat_message,
        # ).get_result()
        summary = client.chat.completions.create(
            model="gpt-4-1106-preview",
            messages=chat_message,
        ).choices[0].message.content
        path = Path(file_path)
        path = path.with_suffix('.txt')
        current_file_path = os.path.dirname(os.path.abspath(__file__))
        new_file_path = os.path.join(current_file_path, 'summary_' + path.name)
        with open(new_file_path, "w", encoding="utf-8") as f:
            f.write(summary)

def get_summary(content: str) -> Union[str, None]:
    chat_message = [{"role": "user", "content": f"请帮我给以下markdown文件生成摘要用于用户问文档内容时的检索匹配，不要超过400个字：\n{content}"}]
    summary = client.chat.completions.create(
        model="gpt-4-1106-preview",
        messages=chat_message,
    ).choices[0].message.content
    return summary

if __name__ == "__main__":
    for file in tqdm(md_file_path):
        write_md_file(file)