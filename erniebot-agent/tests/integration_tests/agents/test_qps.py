import asyncio
import argparse
import aiohttp
import base64
import logging
import time
import os
from tqdm import tqdm
from typing import List


_to_test = [
    # "https://j2e1u4rasbxau7pe.aistudio-hub.baidu.com/image_matting",  # pp matting
    # "https://g0h2o0nbv5m3nctf.aistudio-hub.baidu.com/image_strcture_ocr",  # pp sturcture
    # "https://83xelcf2o1c0yao0.aistudio-hub.baidu.com/analyze-vehicles",  # pp vehicle
    # "https://94b448z5hbe3y1v7.aistudio-hub.baidu.com/image_shitu",  # pp shitu
    # "https://t0h87bf7za23m365.aistudio-hub.baidu.com/ocr",  # pp ocr4
    # "https://ifmbccj2g0sfq17a.aistudio-hub.baidu.com/pp_tinypose",  # pp tinypose
    # "https://vfj9j0u1bb81l4g7.aistudio-hub.baidu.com/pp_humanseg_v2",  # pp humanseg
    # "https://b8t0j4p6ady2v9n6.aistudio-hub.baidu.com/segment_human_image",  # pp human
    # "https://ias6x032h309ibwc.aistudio-hub.baidu.com/image_strcture_ocr", # strurcture 多并发
    # "https://zbxd57k7nasbd1g0.aistudio-hub.baidu.com/segment_human_image", # pp human多并发
    "https://y7ecr3j7e5qbm2q4.aistudio-hub.baidu.com/image_matting", # pp matting多并发
    # "https://f1leiai9h1u5desa.aistudio-hub.baidu.com/pp_humanseg_v2",  # pp humanseg 多并发,
    # "https://za71n9gbx3nfa6je.aistudio-hub.baidu.com/analyze-vehicles", # pp vehicle 多并发
    # "https://mao38cjfu7z3n1cd.aistudio-hub.baidu.com/ocr", # pp ocr 多并发
    # "https://19w7x1nerbx4fco2.aistudio-hub.baidu.com/pp_tinypose", # pp tinypose 多并发
]

_test_file = [
    # "trans.png",
    # "ocr_table.png",
    # "vehicle.jpg",
    # "pp_shituv2_input_img.png",
    # "ocr_example_input.png",
    # "pp_tinypose_input_img.jpg",
    # "humanseg_input_img.jpg",
    # "human_attr.jpg",
    # "ocr_table.png",
    # "human_attr.jpg",
    "trans.png",
    # "humanseg_input_img.jpg",
    # "vehicle.jpg",
    # "ocr_example_input.png",
    # "pp_tinypose_input_img.jpg",
]

headers = {
    # 请前往 https://aistudio.baidu.com/index/accessToken 查看 访问令牌 并替换
    "Authorization": "token 4ce50e3378f418d271c480c8ddfa818537071dbe",
    "Content-Type": "application/json",
}


def parse_args():
    parser = argparse.ArgumentParser(prog="test qps of pp models")
    parser.add_argument("--download-file", type=bool, default=False, help="Whether to download test file.")
    parser.add_argument("--test-times", type=int, default=100, help="Test times.")
    return parser.parse_args()


def get_logger() -> logging.Logger:
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    file_handler = logging.FileHandler(
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "qps_bingfa.log")
    )
    file_handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter("%(asctime)s - %(message)s")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    return logger


logger = get_logger()


def image_to_base64(file_path):
    with open(file_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read())
        return encoded_string.decode("utf-8")


async def download_file(file_name) -> str:
    print(f"Begin to download file {file_name}")
    url = f"https://paddlenlp.bj.bcebos.com/ebagent/ci/fixtures/remote-tools/{file_name}"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            file_content = await response.read()

    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "test_img", file_name)
    with open(path, "wb") as f:
        f.write(file_content)
    return path


async def download_files(file_name_list) -> List[str]:
    tasks = [download_file(file_name) for file_name in file_name_list]
    results = await asyncio.gather(*tasks)
    return results


async def send_post_request(url, data) -> str:
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=data, headers=headers) as response:
            try:
                await response.read()
            except:
                logger.error(str(response))
                pass
            if response.status != 200:
                info = await response.text()
                return info
            return response.status


async def test_qps(test_fimes: int = 5):
    imgs = [
        image_to_base64(os.path.join(os.path.dirname(__file__), "test_img", test_file))
        for test_file in _test_file
    ]
    for i in tqdm(range(len(_to_test))):
        url = _to_test[i]
        test_module = url.split("/")[-1]
        if test_module in ["segment_human_image", "image_strcture_ocr"]:
            data = {"image_base64_str": imgs[i]}
        elif test_module in ["analyze-vehicles", "ocr"]:
            data = {"image": imgs[i]}
        elif test_module in ["image_shitu", "image_matting", "pp_tinypose", "pp_humanseg_v2"]:
            data = {"image_byte_str": imgs[i]}

        start_time = time.time()
        tasks = [send_post_request(url, data) for _ in range(test_fimes)]
        results = await asyncio.gather(*tasks)
        duration = time.time() - start_time
        success = 0
        print(results)
        for res in results:
            if res == 200:
                success += 1
            else:
                print('fail:', res)
        logger.info(f"{test_module}: {duration}, success instances:{success}")


if __name__ == "__main__":
    args = parse_args()
    if args.download_file:
        asyncio.run(download_files(_test_file))

    asyncio.run(test_qps(args.test_times))
