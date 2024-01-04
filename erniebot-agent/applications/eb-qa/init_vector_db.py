
from typing import List, Optional, Union

import nbformat
from langchain.document_loaders.base import BaseLoader
from langchain.document_loaders.helpers import detect_file_encodings
from langchain.embeddings import AzureOpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain_core.documents import Document

from langchain.text_splitter import (
    MarkdownHeaderTextSplitter,
    RecursiveCharacterTextSplitter,
)
from tqdm import tqdm
from openai import OpenAI

headers_to_split_on = [
    ("#", "Header 1"),
    # ("##", "Header 2"),
    # ("###", "Header 3"),
    # ("####", "Header 4"),
]

def get_summary(content: str) -> Union[str, None]:
    client = OpenAI(api_key='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')
    chat_message = [{"role": "user", "content": f"请帮我给以下markdown文件生成摘要用于用户问文档内容时的检索匹配，不要超过400个字：\n{content}"}]
    summary = client.chat.completions.create(
        model="gpt-4-1106-preview",
        messages=chat_message,
    ).choices[0].message.content
    return summary

def open_and_concatenate_ipynb(ipynb_path, encoding):
    # 读取.ipynb文件
    with open(ipynb_path, "r", encoding=encoding) as f:
        notebook_content = nbformat.read(f, as_version=4)

    # 按顺序拼接Markdown文本和code单元
    concatenated_content = ""
    for cell in notebook_content["cells"]:
        if cell["cell_type"] == "code":
            concatenated_content += "```python\n" + cell["source"] + "```\n\n"

    # 返回拼接后的内容
    return concatenated_content

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


def load_md_files_to_doc(
        file_paths: List[str],
        chunk_size: int = 1000,
        chunk_overlap: int = 30,
    ) -> List[Document]:
    markdown_splitter = MarkdownHeaderTextSplitter(headers_to_split_on=headers_to_split_on)
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    output_document = []
    for file in tqdm(file_paths):
        content = read_md_file(file)
        if content is None:
            continue
        md_header_splits = markdown_splitter.split_text(content)
        splits = text_splitter.split_documents(md_header_splits)
        for i in range(len(splits)):
            splits[i].metadata["raw_text"] = splits[i].page_content
            splits[i].page_content = get_summary(splits[i].page_content)
        output_document.extend(splits)
    return output_document

def init_db(faiss_name, faiss_name_module, embeddings):
    md_file_path = [
        "./docs/modules/file.md",
        "./docs/modules/agents.md",
        "./docs/modules/memory.md",
        "./docs/modules/message.md",
        "./docs/modules/chat_models.md",
        "./docs/modules/tools.md",
        "./docs/quickstart/agent.md",
        "./docs/quickstart/use-tool.md",
    ]
    chunk_size = 1000
    chunk_overlap = 30
    content_doc = load_md_files_to_doc(md_file_path, chunk_size, chunk_overlap)

    db = FAISS.from_documents(content_doc, embeddings)
    db.save_local(faiss_name)

    ipynb_path = [
        "./docs/cookbooks/agent/function_agent.ipynb",
        "./docs/cookbooks/agent/chat_models.ipynb",
        "./docs/cookbooks/agent/memory.ipynb",
        "./docs/cookbooks/agent/message.ipynb",
        "./docs/cookbooks/agent/local_tool.ipynb",
        "./docs/cookbooks/agent/tools_intro.ipynb",
        "./docs/cookbooks/agent/remote-tool/remote_tool.ipynb",
    ]
    modules = [item[item.rfind("/") + 1 : item.rfind(".ipynb")] for item in ipynb_path]
    module_doc = []

    for i in range(len(modules)):
        module_doc.append(
            Document(
                page_content=modules[i],
                metadata={"ipynb": open_and_concatenate_ipynb(ipynb_path[i], "utf-8")},
            )
        )

    module_db = FAISS.from_documents(module_doc, embeddings)
    module_db.save_local(faiss_name_module)