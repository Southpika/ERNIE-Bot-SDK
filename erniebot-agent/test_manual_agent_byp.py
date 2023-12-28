import json
from unittest.mock import MagicMock


def get_tool_name_str(tool_list):
    tool_name = []
    for tool in tool_list:
        tool_name.append(tool.name)
    tool_name_str = json.dumps(tool_name, ensure_ascii=False)
    return tool_name_str


def test_get_tool_name_str():
    tool1 = MagicMock()
    tool1.name = "tool1"
    tool2 = MagicMock()
    tool2.name = "tool2"

    result = get_tool_name_str([tool1, tool2])
    assert result == '["tool1", "tool2"]'

    tool3 = MagicMock()
    tool3.name = 123
    tool4 = MagicMock()
    tool4.name = "tool4"
    result = get_tool_name_str([tool3, tool4])
    assert result == '[123, "tool4"]'

    tool5 = MagicMock()
    tool5.name = "tool5"
    result = get_tool_name_str([tool5])
    assert result == '["tool5"]'

    result = get_tool_name_str([])
    assert result == "[]"
