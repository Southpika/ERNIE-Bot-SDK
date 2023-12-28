import json
from typing import List

from erniebot_agent.tools.base import Tool

INSTRUCTION = """# 工具

## 你拥有如下工具：

<tool_list>

## 当你需要调用工具时，请在你的回复中穿插如下的工具调用命令，可以根据需求调用零次或多次：

工具调用
Action: 工具的名称，必须是<tool_name_list>之一
Action Input: 工具的输入
Observation: <result>工具返回的结果</result>
Answer: 根据Observation总结本次工具调用返回的结果，如果结果中出现url，请不要展示出。

```
[链接](url)
```

# 指令
"""

TOOL_DESC = "{name_for_model}: {name_for_human} API。 {description_for_model} 输入参数: {parameters}"


def get_tool_str(tool_list):
    tool_texts = []
    for tool in tool_list:
        tool_schema = tool.function_call_schema()
        tool_texts.append(
            TOOL_DESC.format(
                name_for_model=tool_schema.name,
                name_for_human=tool_schema.name,
                description_for_model=tool_schema.description,
                parameters=json.dumps(tool_schema.parameters, ensure_ascii=False),
            )
        )
    tool_str = "\n\n".join(tool_texts)
    return tool_str


def get_tool_name_str(tool_list):
    tool_name = []
    for tool in tool_list:
        tool_schema = tool.function_call_schema()
        tool_name.append(tool_schema.name)

    tool_name_str = json.dumps(tool_name, ensure_ascii=False)
    return tool_name_str


class PromptManualAgent:
    def __init__(self, tools: List[Tool]):
        self.tools = tools

    def construct_prompt(self):
        tool_str = get_tool_str(self.tools)
        self.prompt = INSTRUCTION.replace("<tool_list>", tool_str)

        tool_name_str = get_tool_name_str(self.tools)
        self.prompt = self.prompt.replace("<tool_name_list>", tool_name_str)
