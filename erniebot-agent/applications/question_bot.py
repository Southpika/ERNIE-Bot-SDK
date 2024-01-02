import asyncio
import argparse
import os

os.environ["EB_AGENT_LOGGING_LEVEL"] = "INFO"
os.environ["EB_AGENT_ACCESS_TOKEN"] = "4ce50e3378f418d271c480c8ddfa818537071dbe"

from erniebot_agent.agents.function_agent_with_retrieval import FunctionAgentWithRetrieval
from erniebot_agent.memory.whole_memory import WholeMemory
from erniebot_agent.chat_models.erniebot import ERNIEBot
from langchain.text_splitter import MarkdownHeaderTextSplitter
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import FAISS
from erniebot_agent.extensions.langchain.embeddings import ErnieEmbeddings
from sklearn.metrics.pairwise import cosine_similarity
from typing import Union, List

embeddings = ErnieEmbeddings(aistudio_access_token=os.environ["EB_AGENT_ACCESS_TOKEN"] , chunk_size=16)
headers_to_split_on = [
    ("#", "Header 1"),
    ("##", "Header 2"),
    ("###", "Header 3"),
    ("####", "Header 4"),
]




parser = argparse.ArgumentParser()
parser.add_argument("--init", type=bool, default=False)
args = parser.parse_args()

def read_md_file(file_path: str) -> Union[str, None]:
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            md_content = file.read()
        return md_content
    except FileNotFoundError:
        print(f"文件 '{file_path}' 不存在。")
        return None
    except Exception as e:
        print(f"读取文件时出现错误： {e}")
        return None

def read_md_files(file_paths: Union[str, List[str]]) -> Union[List[str], str]:
    if isinstance(file_paths, str):
        return read_md_file(file_paths)
    elif isinstance(file_paths, list):
        md_contents = ''
        for file_path in file_paths:
            content = read_md_file(file_path)
            if content is not None:
                md_contents += content
        return md_contents

class FaissSearch:
    def __init__(self, db, embeddings):
        self.db = db
        self.embeddings = embeddings

    def search(self, query: str, top_k: int = 10, **kwargs):
        docs = self.db.similarity_search(query, top_k)
        para_result = self.embeddings.embed_documents([i.page_content for i in docs])
        query_result = self.embeddings.embed_query(query)
        similarities = cosine_similarity([query_result], para_result).reshape((-1,))
        retrieval_results = []
        for index, doc in enumerate(docs):
            retrieval_results.append(
                {"content": doc.page_content, "score": similarities[index], "title": doc.metadata["Header 1"]}
            )
        return retrieval_results

faiss_name = "faiss_index"
if not args.init:
    db = FAISS.load_local(faiss_name, embeddings)
else:
    md_file_path = ['./docs/modules/file.md','./docs/modules/agents.md']
    content = read_md_files(md_file_path)
    markdown_splitter = MarkdownHeaderTextSplitter(headers_to_split_on=headers_to_split_on)
    md_header_splits = markdown_splitter.split_text(content)
    chunk_size = 500
    chunk_overlap = 30
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size, chunk_overlap=chunk_overlap
    )
    splits = text_splitter.split_documents(md_header_splits)
    db = FAISS.from_documents(splits, embeddings)
    db.save_local(faiss_name)

llm = ERNIEBot(model="ernie-3.5")
faiss_search = FaissSearch(db=db, embeddings=embeddings)
agent = FunctionAgentWithRetrieval(
    llm=llm, tools=[], knowledge_base=faiss_search, threshold=0.5
)

async def main():
    response = await agent.run('怎么创建EB-Agent？')
    messages = response.chat_history
    for item in messages:
        print(item.to_dict())

if __name__ == "__main__":
    asyncio.run(main())
