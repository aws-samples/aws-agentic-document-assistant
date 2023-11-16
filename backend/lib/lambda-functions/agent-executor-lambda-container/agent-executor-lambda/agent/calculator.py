# The custom calculator is built to avoid the issue
# https://github.com/langchain-ai/langchain/issues/3071
# Inspiration sources:
# https://python.langchain.com/docs/modules/agents/tools/custom_tools
# and (https://github.com/langchain-ai/langchain/blob/master/libs/
#      langchain/langchain/chains/llm_math/base.py#L82)

import math
from typing import Optional, Type

from langchain.callbacks.manager import (
    AsyncCallbackManagerForToolRun,
    CallbackManagerForToolRun,
)
from langchain.tools import BaseTool
from pydantic import BaseModel, Field


class CalculatorInput(BaseModel):
    question: str = Field()


def _evaluate_expression(expression: str) -> str:
    import numexpr  # noqa: F401

    try:
        local_dict = {"pi": math.pi, "e": math.e}
        output = str(
            numexpr.evaluate(
                expression.strip(),
                global_dict={},  # restrict access to globals
                local_dict=local_dict,  # add common mathematical functions
            )
        )
    except Exception as e:
        raise ValueError(
            f'LLMMathChain._evaluate("{expression}") raised error: {e}.'
            " Please try again with a valid numerical expression"
        )

    return output.strip()


class CustomCalculatorTool(BaseTool):
    name = "Calculator"
    description = "useful for when you need to answer questions about math"
    args_schema: Type[BaseModel] = CalculatorInput

    def _run(
        self, query: str, run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> str:
        """Use the tool."""
        try:
            return _evaluate_expression(query.strip())
        except Exception as e:
            return (
                f"Failed to evaluate the expression with error {e}."
                " Please only provide a valid math expression."
            )

    async def _arun(
        self, query: str, run_manager: Optional[AsyncCallbackManagerForToolRun] = None
    ) -> str:
        """Use the tool asynchronously."""
        raise NotImplementedError("Calculator does not support async")
