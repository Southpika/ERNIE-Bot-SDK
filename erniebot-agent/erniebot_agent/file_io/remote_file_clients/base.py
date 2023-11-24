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

import abc
from typing import BinaryIO, List

from erniebot_agent.file_io.remote_file_clients.schema import FileContent, FileInfo


class RemoteFileClient(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    async def upload_file(self, file: BinaryIO) -> FileInfo:
        raise NotImplementedError

    @abc.abstractmethod
    async def retrieve_file(self, file_id: str) -> FileInfo:
        raise NotImplementedError

    @abc.abstractmethod
    async def retrieve_file_content(self, file_id: str) -> FileContent:
        raise NotImplementedError

    @abc.abstractmethod
    async def list_files(self) -> List[FileInfo]:
        raise NotImplementedError

    @abc.abstractmethod
    async def delete_file(self, file_id: str) -> None:
        raise NotImplementedError
