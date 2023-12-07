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

from __future__ import annotations

import base64
import json
import os
import tempfile
from abc import ABC, abstractmethod
from copy import deepcopy
from dataclasses import asdict, dataclass, field
from functools import wraps
from typing import Any, Dict, List, Optional, Type

import requests
from erniebot_agent.file_io.file_manager import FileManager
from erniebot_agent.messages import AIMessage, FunctionCall, HumanMessage, Message
from erniebot_agent.tools.schema import (
    Endpoint,
    EndpointInfo,
    RemoteToolView,
    ToolParameterView,
    scrub_dict,
)
from erniebot_agent.utils.http import url_file_exists
from erniebot_agent.utils.logging import logger
from openapi_spec_validator import validate
from openapi_spec_validator.readers import read_from_filename
from yaml import safe_dump

import erniebot


def validate_openapi_yaml(yaml_file: str) -> bool:
    """do validation on the yaml file

    Args:
        yaml_file (str): the path of yaml file

    Returns:
        bool: whether yaml file is valid
    """
    yaml_dict = read_from_filename(yaml_file)[0]
    try:
        validate(yaml_dict)
        return True
    except Exception as e:  # type: ignore
        logger.error(e)
        return False


class BaseTool(ABC):
    @abstractmethod
    async def __call__(self, *args: Any, **kwds: Any) -> Any:
        raise NotImplementedError

    @abstractmethod
    def function_call_schema(self) -> dict:
        raise NotImplementedError


class Tool(BaseTool, ABC):
    description: str
    name: Optional[str] = None
    input_type: Optional[Type[ToolParameterView]] = None
    ouptut_type: Optional[Type[ToolParameterView]] = None

    def __str__(self) -> str:
        name = self.name if self.name else self.tool_name
        return "<name: {0}, description: {1}>".format(name, self.description)

    def __repr__(self):
        return self.__str__()

    @property
    def tool_name(self):
        return self.name or self.__class__.__name__

    @abstractmethod
    async def __call__(self, *args: Any, **kwds: Any) -> Dict[str, Any]:
        """the body of tools

        Returns:
            Any:
        """
        raise NotImplementedError

    def function_call_schema(self) -> dict:
        inputs = {
            "name": self.tool_name,
            "description": self.description,
            "examples": [example.to_dict() for example in self.examples],
        }
        if self.input_type is not None:
            inputs["parameters"] = self.input_type.function_call_schema()
        if self.ouptut_type is not None:
            inputs["responses"] = self.ouptut_type.function_call_schema()

        return scrub_dict(inputs) or {}

    @property
    def examples(self) -> List[Message]:
        return []


def wrap_tool_with_files(func):
    @wraps(func)
    async def wrapper_func(object: RemoteTool, **tool_arguments):
        async def fileid_to_byte(file_id, file_manager):
            file = file_manager.look_up_file_by_id(file_id)
            byte_str = await file.read_contents()
            return byte_str

        file_manager = object.file_manager
        # 1. replace fileid with byte string
        for key in tool_arguments.keys():
            if (
                object.tool_view.parameters
                and object.tool_view.parameters.model_fields[key].json_schema_extra
            ):
                json_schema_extra = object.tool_view.parameters.model_fields[key].json_schema_extra
                if json_schema_extra.get("format", None) in ["byte", "binary"]:
                    byte_str = await fileid_to_byte(tool_arguments[key], file_manager)
                    tool_arguments[key] = base64.b64encode(byte_str).decode()

        # 2. call tool get response
        json_response = await func(object, **tool_arguments)
        return json_response

    return wrapper_func


class RemoteTool(BaseTool):
    def __init__(
        self,
        tool_view: RemoteToolView,
        server_url: str,
        headers: dict,
        version: str,
        examples: Optional[List[Message]] = None,
        tool_name_prefix: Optional[str] = None,
    ) -> None:
        self.tool_view = tool_view
        self.server_url = server_url
        self.headers = headers
        self.version = version
        self.examples = examples
        self.tool_name_prefix = tool_name_prefix
        # If `tool_name_prefix`` is provided, we prepend `tool_name_prefix`` to the `name` field of all tools
        if tool_name_prefix is not None:
            self.tool_view.name = f"{self.tool_name_prefix}/{self.tool_view.name}"

        self.file_manager = FileManager()

    def __str__(self) -> str:
        return "<name: {0}, server_url: {1}, description: {2}>".format(
            self.tool_name, self.server_url, self.tool_view.description
        )

    def __repr__(self):
        return self.__str__()

    @property
    def tool_name(self):
        return self.tool_view.name

    @wrap_tool_with_files
    async def __call__(self, **tool_arguments: Dict[str, Any]) -> Any:
        url = self.server_url + self.tool_view.uri + "?version=" + self.version

        headers = deepcopy(self.headers)
        headers["Content-Type"] = self.tool_view.parameters_content_type

        requests_inputs = {
            "headers": headers,
        }
        if self.tool_view.method == "get":
            requests_inputs["params"] = tool_arguments
        elif self.tool_view.parameters_content_type == "application/json":
            requests_inputs["json"] = tool_arguments
        elif self.tool_view.parameters_content_type == "application/x-www-form-urlencoded":
            requests_inputs["data"] = tool_arguments
        else:
            raise ValueError(f"Unsupported content type: {self.tool_view.parameters_content_type}")

        if self.tool_view.method == "get":
            response = requests.get(url, **requests_inputs)  # type: ignore
        elif self.tool_view.method == "post":
            response = requests.post(url, **requests_inputs)  # type: ignore
        elif self.tool_view.method == "put":
            response = requests.put(url, **requests_inputs)  # type: ignore
        elif self.tool_view.method == "delete":
            response = requests.delete(url, **requests_inputs)  # type: ignore
        else:
            raise ValueError(f"method<{self.tool_view.method}> is invalid")

        if response.status_code != 200:
            raise ValueError(
                f"The resource requested by `{self.tool_name}` returned"
                f"{response.status_code}: {response.text}"
            )

        # parse the file from response
        file_names = []
        if self.tool_view.returns:
            for key in self.tool_view.returns.model_fields.keys():
                if self.tool_view.returns.model_fields[
                    key
                ].json_schema_extra and self.tool_view.returns.model_fields[key].json_schema_extra.get(
                    "format", None
                ) in [
                    "byte",
                    "binary",
                ]:
                    file_names.append(key)

        if len(file_names) == 0:
            return response.json()
        elif len(file_names) != 1:
            raise RuntimeError("The tool returns multiple files, which is not supported for now")

        result = {}
        # create file from bytes
        file_name = response.headers["Content-Disposition"].split("filename=")[1]
        local_file = await self.file_manager.create_file_from_bytes(response.content, file_name)

        result[file_names[0]] = local_file.id

        return result

    def _decode_file(self):
        pass

    def function_call_schema(self) -> dict:
        schema = self.tool_view.function_call_schema()
        if self.examples is not None:
            schema["examples"] = [example.to_dict() for example in self.examples]

        return schema or {}


@dataclass
class RemoteToolkit:
    """RemoteToolkit can be converted by openapi.yaml and endpoint"""

    openapi: str
    info: EndpointInfo
    servers: List[Endpoint]
    paths: List[RemoteToolView]

    component_schemas: dict[str, Type[ToolParameterView]]
    headers: dict
    examples: List[Message] = field(default_factory=list)

    @property
    def tool_name_prefix(self) -> str:
        return f"{self.info.title}/{self.info.version}"

    def __getitem__(self, tool_name: str) -> RemoteTool:
        return self.get_tool(tool_name)

    def get_tools(self) -> List[RemoteTool]:
        return [
            RemoteTool(
                path,
                self.servers[0].url,
                self.headers,
                self.info.version,
                examples=self.get_examples_by_name(path.name),
                tool_name_prefix=self.tool_name_prefix,
            )
            for path in self.paths
        ]

    def get_examples_by_name(self, tool_name: str) -> List[Message]:
        """get examples by tool-name

        Args:
            tool_name (str): the name of the tool

        Returns:
            List[Message]: the messages
        """
        # 1. split messages
        tool_examples: List[List[Message]] = []
        examples: List[Message] = []
        for example in self.examples:
            if isinstance(example, HumanMessage):
                if len(examples) == 0:
                    examples.append(example)
                else:
                    tool_examples.append(examples)
                    examples = [example]
            else:
                examples.append(example)

        if len(examples) > 0:
            tool_examples.append(examples)

        final_exampels: List[Message] = []
        # 2. find the target tool examples or empty messages
        for examples in tool_examples:
            tool_names = [
                example.function_call.get("name", None)
                for example in examples
                if isinstance(example, AIMessage) and example.function_call is not None
            ]
            tool_names = [name for name in tool_names if name]

            if tool_name in tool_names:
                # 3. prepend `tool_name_prefix` to all tool names in examples
                for example in examples:
                    if isinstance(example, AIMessage) and example.function_call is not None:
                        original_tool_name = example.function_call["name"]
                        example.function_call["name"] = f"{self.tool_name_prefix}/{original_tool_name}"
                final_exampels.extend(examples)

        return final_exampels

    def get_tool(self, tool_name: str) -> RemoteTool:
        paths = [path for path in self.paths if path.name == tool_name]
        assert len(paths) == 1, f"tool<{tool_name}> not found in paths"
        return RemoteTool(
            paths[0],
            self.servers[0].url,
            self.headers,
            self.info.version,
            examples=self.get_examples_by_name(tool_name),
            tool_name_prefix=self.tool_name_prefix,
        )

    def to_openapi_dict(self) -> dict:
        """convert plugin schema to openapi spec dict"""
        spec_dict = {
            "openapi": self.openapi,
            "info": asdict(self.info),
            "servers": [asdict(server) for server in self.servers],
            "paths": {tool_view.uri: tool_view.to_openapi_dict() for tool_view in self.paths},
            "components": {
                "schemas": {
                    uri: parameters_view.to_openapi_dict()
                    for uri, parameters_view in self.component_schemas.items()
                }
            },
        }
        return scrub_dict(spec_dict, remove_empty_dict=True) or {}

    def to_openapi_file(self, file: str):
        """generate openapi configuration file

        Args:
            file (str): the path of the openapi yaml file
        """
        spec_dict = self.to_openapi_dict()
        with open(file, "w+", encoding="utf-8") as f:
            safe_dump(spec_dict, f, indent=4)

    @classmethod
    def from_openapi_dict(
        cls, openapi_dict: Dict[str, Any], access_token: Optional[str] = None
    ) -> RemoteToolkit:
        info = EndpointInfo(**openapi_dict["info"])
        servers = [Endpoint(**server) for server in openapi_dict.get("servers", [])]

        # components
        component_schemas = openapi_dict["components"]["schemas"]
        fields = {}
        for schema_name, schema in component_schemas.items():
            parameter_view = ToolParameterView.from_openapi_dict(schema)
            fields[schema_name] = parameter_view

        # paths
        paths = []
        for path, path_info in openapi_dict.get("paths", {}).items():
            for method, path_method_info in path_info.items():
                paths.append(
                    RemoteToolView.from_openapi_dict(
                        uri=path,
                        method=method,
                        version=info.version,
                        path_info=path_method_info,
                        parameters_views=fields,
                    )
                )

        return RemoteToolkit(
            openapi=openapi_dict["openapi"],
            info=info,
            servers=servers,
            paths=paths,
            component_schemas=fields,
            headers=cls._get_authorization_headers(access_token),
        )  # type: ignore

    @classmethod
    def from_openapi_file(cls, file: str, access_token: Optional[str] = None) -> RemoteToolkit:
        """only support openapi v3.0.1

        Args:
            file (str): the path of openapi yaml file
            access_token (Optional[str]): the path of openapi yaml file
        """
        if not validate_openapi_yaml(file):
            raise ValueError(f"invalid openapi yaml file: {file}")

        spec_dict, _ = read_from_filename(file)
        return cls.from_openapi_dict(spec_dict, access_token=access_token)

    @classmethod
    def _get_authorization_headers(cls, access_token: Optional[str]) -> dict:
        if access_token is None:
            access_token = erniebot.access_token

        headers = {"Content-Type": "application/json"}
        if access_token is None:
            logger.warning("access_token is NOT provided, this may cause 403 HTTP error..")
        else:
            headers["Authorization"] = f"token {access_token}"
        return headers

    @classmethod
    def from_url(
        cls, url: str, version: Optional[str] = None, access_token: Optional[str] = None
    ) -> RemoteToolkit:
        # 1. download openapy.yaml file to temp directory
        if not url.endswith("/"):
            url += "/"
        openapi_yaml_url = url + ".well-known/openapi.yaml"

        if version:
            openapi_yaml_url = openapi_yaml_url + "?version=" + version

        with tempfile.TemporaryDirectory() as temp_dir:
            response = requests.get(openapi_yaml_url, headers=cls._get_authorization_headers(access_token))
            if response.status_code != 200:
                raise ValueError(f"the resource is invalid, the error message is: {response.text}")

            file_content = response.content.decode("utf-8")
            if not file_content.strip():
                raise ValueError(f"the content is empty from: {openapi_yaml_url}")

            file_path = os.path.join(temp_dir, "openapi.yaml")
            with open(file_path, "w+", encoding="utf-8") as f:
                f.write(file_content)

            toolkit = RemoteToolkit.from_openapi_file(file_path, access_token=access_token)
            for server in toolkit.servers:
                server.url = url

            toolkit.examples = cls.load_remote_examples_yaml(url, access_token)

        return toolkit

    @classmethod
    def load_remote_examples_yaml(cls, url: str, access_token: Optional[str] = None) -> List[Message]:
        """load remote examples by url: url/.well-known/examples.yaml

        Args:
            url (str): the base url of the remote toolkit
        """
        if not url.endswith("/"):
            url += "/"
        examples_yaml_url = url + ".well-known/examples.yaml"
        if not url_file_exists(examples_yaml_url, cls._get_authorization_headers(access_token)):
            return []

        examples = []
        with tempfile.TemporaryDirectory() as temp_dir:
            response = requests.get(examples_yaml_url, headers=cls._get_authorization_headers(access_token))
            if response.status_code != 200:
                raise ValueError(
                    f"Invalid resource, status_code: {response.status_code}, error message: {response.text}"
                )

            file_content = response.content.decode("utf-8")
            if not file_content.strip():
                raise ValueError(f"the content is empty from: {examples_yaml_url}")

            file_path = os.path.join(temp_dir, "examples.yaml")
            with open(file_path, "w+", encoding="utf-8") as f:
                f.write(file_content)

            examples = cls.load_examples_yaml(file_path)

        return examples

    @classmethod
    def load_examples_dict(cls, examples_dict: Dict[str, Any]) -> List[Message]:
        messages: List[Message] = []
        for examples in examples_dict["examples"]:
            examples = examples["context"]
            for example in examples:
                if "user" == example["role"]:
                    messages.append(HumanMessage(example["content"]))
                elif "bot" in example["role"]:
                    plugin = example["plugin"]
                    if "operationId" in plugin:
                        function_call: FunctionCall = {
                            "name": plugin["operationId"],
                            "thoughts": plugin["thoughts"],
                            "arguments": json.dumps(plugin["requestArguments"], ensure_ascii=False),
                        }
                    else:
                        function_call = {
                            "name": "",
                            "thoughts": plugin["thoughts"],
                            "arguments": "{}",
                        }  # type: ignore
                    messages.append(AIMessage("", function_call=function_call))
                else:
                    raise ValueError(f"invald role: <{example['role']}>")
        return messages

    @classmethod
    def load_examples_yaml(cls, file: str) -> List[Message]:
        """load examples from yaml file

        Args:
            file (str): the path of examples file

        Returns:
            List[Message]: the list of messages
        """
        content: dict = read_from_filename(file)[0]
        if len(content) == 0 or "examples" not in content:
            raise ValueError("invalid examples configuration file")
        return cls.load_examples_dict(content)

    def function_call_schemas(self) -> List[dict]:
        return [tool.function_call_schema() for tool in self.get_tools()]
