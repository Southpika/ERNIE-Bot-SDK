import argparse
import asyncio
import os

os.environ["EB_AGENT_LOGGING_LEVEL"] = "INFO"
# os.environ["EB_AGENT_ACCESS_TOKEN"] = "4ce50e3378f418d271c480c8ddfa818537071dbe"

from langchain.vectorstores import FAISS
from sklearn.metrics.pairwise import cosine_similarity

from erniebot_agent.agents.function_agent_with_retrieval import (
    FunctionAgentWithRetrieval,
)
from erniebot_agent.chat_models import ERNIEBot
from erniebot_agent.extensions.langchain.embeddings import ErnieEmbeddings
from erniebot_agent.memory import SystemMessage
from init_vector_db import init_db

parser = argparse.ArgumentParser()
parser.add_argument("--init", type=bool, default=False)
args = parser.parse_args()

embeddings = ErnieEmbeddings(aistudio_access_token=os.environ["EB_AGENT_ACCESS_TOKEN"], chunk_size=16)

# embeddings = AzureOpenAIEmbeddings(deployment="text-embedding-ada")

class FaissSearch:
    def __init__(self, db, embeddings, module_db):
        self.db = db
        self.module_db = module_db
        self.embeddings = embeddings

    def search(self, query: str, top_k: int = 2, **kwargs):
        docs = self.db.similarity_search(query, top_k)
        para_result = self.embeddings.embed_documents([i.page_content for i in docs])
        query_result = self.embeddings.embed_query(query)
        similarities = cosine_similarity([query_result], para_result).reshape((-1,))
        retrieval_results = []
        for index, doc in enumerate(docs):
            if "Header 1" in doc.metadata:
                retrieval_results.append(
                    {
                        "content": doc.metadata['raw_text'],
                        "score": similarities[index],
                        "title": doc.metadata["Header 1"],
                    }
                )
            else:
                retrieval_results.append(
                    {"content": doc.metadata['raw_text'], "score": similarities[index], "title": ""}
                )
        code = self.module_db.similarity_search(query, 1)[0]
        retrieval_results.append({"content": code.metadata["ipynb"], "score": 1, "title": code.page_content})

        return retrieval_results


def load_agent():
    faiss_name = "faiss_index"
    faiss_name_module = "faiss_index_module"
    if args.init:
        init_db(faiss_name, faiss_name_module, embeddings)
    db = FAISS.load_local(faiss_name, embeddings)
    module_db = FAISS.load_local(faiss_name_module, embeddings)
    llm = ERNIEBot(model="ernie-3.5")
    faiss_search = FaissSearch(db=db, embeddings=embeddings, module_db=module_db)
    agent = FunctionAgentWithRetrieval(
        llm=llm,
        tools=[],
        knowledge_base=faiss_search,
        threshold=0,
        system_message=SystemMessage(
            "你是ERNIEBot Agent的小助手，用于解决用户关于EB-Agent的问题，涉及File, Memory, Message, Agent, ChatModels等模块。"
            "请你严格按照搜索到的内容回答，不要自己生成相关代码。如果询问与ERNIEBot Agent无关的问题，请直接回答“我只能回答EB—Agent相关问题”"
        ),
        top_k=2,
        token_limit=5000,
    )
    return agent


async def main(agent):
    # response = await agent.run('怎么使用File模块？')
    # response = await agent.run('怎么获取我的File的内容？')
    response = await agent.run("怎么创建一个EB-Agent，给出具体的代码？")
    print(response.text)


if __name__ == "__main__":
    agent = load_agent()
    # asyncio.run(main(agent))
    agent.launch_gradio_demo()
