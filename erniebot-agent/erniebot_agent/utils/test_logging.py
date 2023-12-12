import unittest

import pytest


class FileFormatter(unittest.TestCase):
    def extract_content(self, message, *args):
        if len(args) < 2:
            raise ValueError("At least two patterns are required.")
        return message[message.find(args[0]) + len(args[0]) : message.find(args[1])].strip()

    def test_extract_content(self):
        formatter = FileFormatter()

        formatter.extract_content("Test log message", "pattern1", "pattern2")
        log_message = """INFO - [Run][Start] FunctionalAgent is about to start running with input:
 1+4等于几？
[LLM][Start] ERNIEBot is about to start running with input:"""
        result = formatter.extract_content(log_message, "start running with input:\n", "[LLM][Start]")
        assert result == "1+4等于几？"
