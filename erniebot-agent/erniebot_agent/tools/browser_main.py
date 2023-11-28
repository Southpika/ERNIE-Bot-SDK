import math
import os
import re
import time
from typing import List
from urllib.parse import quote

import erniebot_agent
import numpy as np
import requests
from bs4 import BeautifulSoup
from erniebot_agent.tools.web_serach_tool import web_searcher
from tqdm import tqdm

import erniebot as eb

headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Safari/605.1.15"
}
# eb.api_type = 'aistudio'
# eb.access_token = os.getenv("EB_ACCESS_TOKEN")


def _get_embedding(word: List[str]) -> List[float]:
    """
    Get the embedding of a list of words.

    Args:
        word (List[str]): Words to get embedding.

    Returns:
        List[float]: Embedding List of the words.
    """

    embedding: List[float]
    if len(word) <= 16:
        resp = eb.Embedding.create(model="ernie-text-embedding", input=word)
        embedding = resp.get_result()
    else:
        size = len(word)
        embedding = []
        for i in tqdm(range(math.ceil(size / 16))):
            temp_result = eb.Embedding.create(
                model="ernie-text-embedding", input=word[i * 16 : (i + 1) * 16]
            )

            embedding.extend(temp_result.get_result())
            time.sleep(1)
    return embedding


def _l2_normalization(embedding: np.ndarray) -> np.ndarray:
    if embedding.ndim == 1:
        return embedding / np.linalg.norm(embedding).reshape(-1, 1)
    else:
        return embedding / np.linalg.norm(embedding, axis=1).reshape(-1, 1)


def find_related_doc(
    query: str, origin_chunk: List[str], doc_embedding: np.ndarray, top_k: int = 5
) -> List[int]:
    rank_scores = _l2_normalization(np.array(_get_embedding([query]))) @ doc_embedding.T
    top_k_similar = rank_scores.argsort()[0][-top_k:].tolist()[::-1]
    res = ""
    for i in range(len(top_k_similar)):
        # print(f"Top {i+1}:{origin_chunk[top_k_similar[i]]}")
        # print('-'*50)
        res += f"参考文档 {i+1}:{origin_chunk[top_k_similar[i]]}" + "\n\n"
    return res


def split_by_len(texts: List[str], split_token: int = 384) -> List[str]:
    """
    Split the knowledge base docs into chunks by length.

    Args:
        texts (List[str]): Knowledge Base Texts.
        split_token (int, optional): The max length supported by ernie-text-embedding. Default to 384.

    Returns:
        List[str]: Doc Chunks.
    """
    chunk = []
    for text in texts:
        idx = 0
        while idx + split_token < len(text):
            temp_text = text[idx : idx + split_token]
            next_idx = temp_text.rfind("。") + 1
            if next_idx != 0:  # If this slice doesn't have a period, add the whole sentence.
                chunk.append(temp_text[:next_idx])
                idx = idx + next_idx
            else:
                chunk.append(temp_text)
                idx = idx + split_token

        chunk.append(text[idx:])
    return chunk


class Browser_Manager(web_searcher):
    def search(self, search_type, query):
        if search_type == "news":
            contents = self.search_news()
        elif search_type == "baike":
            contents = [self.search_baike(query)]
            if not contents:
                contents = self.search_main(query)
        elif search_type == "search":
            contents = self.search_main(query)
        else:
            return ""
        contents_chunk = split_by_len(contents[1])
        erniebot_agent.logger.debug("chunk:" + str(contents_chunk))
        try:
            contents_embedding = _get_embedding(contents_chunk)
            time.sleep(1)
            similar_chunk = find_related_doc(query, contents_chunk, np.array(contents_embedding))
            return similar_chunk
        except eb.errors.APIError as e:
            erniebot_agent.logger.error(e)
            return "未搜索到相关内容"


if __name__ == "__main__":
    browser = Browser_Manager(web_num=5)
    print(browser.search(search_type="search", query="孤注一掷电影内容"))
