import json
from typing import List

from erniebot_agent.agents import FunctionalAgent
from erniebot_agent.agents.schema import AgentAction, AgentFile, AgentResponse
from erniebot_agent.messages import HumanMessage, Message
from erniebot_agent.prompt import PromptTemplate
from erniebot_agent.retrieval import BaizhongSearch
from erniebot_agent.utils.logging import logger

INTENT_PROMPT = """检索结果:
{% for doc in documents %}
    第{{loop.index}}个段落: {{doc['content_se']}}
{% endfor %}
检索语句: {{query}}
请判断以上的检索结果和检索语句是否相关，并且有助于回答检索语句的问题。
请严格按照【JSON格式】输出。如果相关，则回复：{"is_relevant":true}，如果不相关，则回复：{"is_relevant":false}"""

RAG_PROMPT = """检索结果:
{% for doc in documents %}
    第{{loop.index}}个段落: {{doc['content_se']}}
{% endfor %}
检索语句: {{query}}
请根据以上检索结果回答检索语句的问题"""


class FunctionalAgentWithRetrieval(FunctionalAgent):
    def __init__(self, knowledge_base: BaizhongSearch, top_k: int = 3, **kwargs):
        super().__init__(**kwargs)
        self.knowledge_base = knowledge_base
        self.top_k = top_k
        self.intent_prompt = PromptTemplate(INTENT_PROMPT, input_variables=["documents", "query"])
        self.rag_prompt = PromptTemplate(RAG_PROMPT, input_variables=["documents", "query"])

    async def _async_run(self, prompt: str) -> AgentResponse:
        results = await self._maybe_retrieval(prompt)
        if results["is_relevant"] is True:
            # RAG
            step_input = HumanMessage(
                content=self.rag_prompt.format(query=prompt, documents=results["documents"])
            )
            chat_history: List[Message] = []
            actions_taken: List[AgentAction] = []
            files_involved: List[AgentFile] = []

            chat_history.append(step_input)
            llm_resp = await self._async_run_llm(
                messages=chat_history,
                functions=None,
                system=self.system_message.content if self.system_message is not None else None,
            )
            output_message = llm_resp.message
            chat_history.append(output_message)
            response = self._create_finished_response(chat_history, actions_taken, files_involved)
            self.memory.add_message(chat_history[0])
            self.memory.add_message(chat_history[-1])
            return response
        else:
            logger.info(
                f"Irrelevant retrieval results. Fallbacking to FunctionalAgent for the query: {prompt}"
            )
            return await super()._async_run(prompt)

    async def _maybe_retrieval(
        self,
        step_input,
    ):
        documents = self.knowledge_base.search(step_input, top_k=self.top_k, filters=None)
        messages = [HumanMessage(content=self.intent_prompt.format(documents=documents, query=step_input))]
        response = await self._async_run_llm(messages)
        results = self._parse_results(response.message.content)
        results["documents"] = documents
        return results

    def _parse_results(self, results):
        left_index = results.find("{")
        right_index = results.rfind("}")
        if left_index == -1 or right_index == -1:
            # if invalid json, use Functional Agent
            return {"is_relevant": False}
        try:
            return json.loads(results[left_index : right_index + 1])
        except Exception:
            # if invalid json, use Functional Agent
            return {"is_relevant": False}
