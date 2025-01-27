除了支持FunctionAgent以外，同时我们也支持通过ToolFormat以手动编排的方式通过Prompt激活Agent：通过事先定义Agent想要操作的步骤，然后通过指定的tool识别范式来运行tool。

步骤

1. Planning：通过Prompt事先指定相应的指令作为Plan，在Plan中具体指定哪一步要做什么以及工具调用。

```python
   INSTRUCTION = """你的指令是为我提供一个基于《{SCRIPT}》剧情的在线RPG游戏体验。\
   在这个游戏中，玩家将扮演《{SCRIPT}》剧情关键角色，你可以自行决定玩家的角色。\
   游戏情景将基于《{SCRIPT}》剧情。这个游戏的玩法是互动式的，并遵循以下特定格式：

   <场景描述>：根据玩家的选择，故事情节将按照《{SCRIPT}》剧情的线索发展。你将描述角色所处的环境和情况。场景描述不少于50字。

   <场景图片>：对于每个场景，你将创造一个概括该情况的图像。在这个步骤你需要调用画图工具ImageGenerationTool并按json格式输出相应调用详情。\
   ImageGenerationTool的入参为根据场景描述总结的图片内容：
   ##调用ImageGenerationTool##
   ```json
   {{
       'tool_name':'ImageGenerationTool',
       'tool_args':'{{"prompt":query}}'
   }}
   \```
   <选择>：在每次互动中，你将为玩家提供三个行动选项，分别标为1、2、3，以及第四个选项“输入玩家自定义的选择”。故事情节将根据玩家选择的行动进展。
   如果一个选择不是直接来自《{SCRIPT}》剧情，你将创造性地适应故事，最终引导它回归原始情节。

   整个故事将围绕《{SCRIPT}》丰富而复杂的世界展开。每次互动必须包括<场景描述>、<场景图片>和<选择>。所有内容将以中文呈现。
   你的重点将仅仅放在提供场景描述，场景图片和选择上，不包含其他游戏指导。场景尽量不要重复，要丰富一些。

   当我说游戏开始的时候，开始游戏。每次只要输出【一组】互动，【不要自己生成互动】。"""
```
