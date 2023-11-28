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

COLORS = {
    "Purple": "\033[95m",  # Purple
    "Green": "\033[92m",  # Green
    "Yellow": "\033[93m",  # Yellow
    "Red": "\033[91m",  # Red
    "Bold Red": "\033[91m" + "\033[1m",  # Bold Red
    "RESET": "\033[0m",
    "Blue": "\033[94m",
}


def color_text(text: str, color: str) -> str:
    if color not in COLORS:
        raise ValueError("Only support colors: " + ", ".join(COLORS.keys()))

    return COLORS[color] + str(text) + COLORS["RESET"]
