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

from typing import List, Tuple

__all__ = ["Model"]


class Model(object):
    """A dummy resource class."""

    @staticmethod
    def list() -> List[Tuple[str, str]]:
        """Lists the available models."""
        return [
            ("ernie-3.5", "文心大模型（ernie-3.5）"),
            ("ernie-turbo", "文心大模型（ernie-turbo）"),
            ("ernie-4.0", "文心大模型（ernie-4.0）"),
            ("ernie-3.5-8k", "文心大模型（ernie-3.5-8k）"),
            ("ernie-speed", " 文心大模型（ernie-speed）"),
            ("ernie-speed-128k", " 文心大模型（ernie-speed-128k）"),
            ("ernie-tiny-8k", " 文心大模型（ernie-tiny-8k）"),
            ("ernie-char-8k", " 文心大模型（ernie-char-8k）"),
            ("ernie-text-embedding", "文心百中语义模型"),
            ("ernie-vilg-v2", "文心一格模型"),
        ]
