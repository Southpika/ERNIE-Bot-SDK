
import unittest
import os

from erniebot_agent.extensions.langchain.embeddings import ErnieEmbeddings
from langchain.document_loaders import TextLoader
from langchain.text_splitter import SpacyTextSplitter
from langchain.vectorstores import FAISS


class TestEmbedding(unittest.TestCase):
    def test_retry(self):
        embeddings = ErnieEmbeddings(aistudio_access_token=os.getenv('EB_ACCESS_TOKEN'), 
                                    chunk_size=16)        

        loader = TextLoader("/Users/tanzhehao/Downloads/douluo.txt")
        documents = loader.load()
        text_splitter = SpacyTextSplitter(pipeline='zh_core_web_sm', chunk_size=400, chunk_overlap=200)
        docs = text_splitter.split_documents(documents)
        db = FAISS.from_documents(docs, embeddings)