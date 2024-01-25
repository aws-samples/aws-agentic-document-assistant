from typing import Optional, Union

from langchain.chains.sql_database.query import (SQLInput, SQLInputWithTables,
                                                 _strip)
from langchain.schema.language_model import BaseLanguageModel
from langchain.schema.output_parser import NoOpOutputParser
from langchain.schema.prompt_template import BasePromptTemplate
from langchain.schema.runnable import RunnableMap, RunnableSequence
from langchain.sql_database import SQLDatabase


def create_sql_query_generation_chain(
    llm: BaseLanguageModel,
    db: SQLDatabase,
    prompt: Optional[BasePromptTemplate] = None,
    k: int = 5,
) -> RunnableSequence[Union[SQLInput, SQLInputWithTables], str]:
    """Create a chain that generates SQL queries.

    Args:
        llm: The language model to use
        db: The SQLDatabase to generate the query for
        prompt: The prompt to use. If none is provided, will choose one
            based on dialect. Defaults to None.
        k: The number of results per select statement to return. Defaults to 5.

    Returns:
        A chain that takes in a question and generates a SQL query that answers
        that question.
    """
    if prompt is not None:
        prompt_to_use = prompt
    else:
        raise ValueError(
            "A valid SQL query generation prompt must be provided."
            f" Current prompt is {prompt}"
        )

    inputs = {
        "input": lambda x: x["question"],
        "initial_context": lambda x: x["initial_context"],
        "tables_content_description": lambda x: x["tables_content_description"],
        "top_k": lambda _: k,
        "table_info": lambda x: db.get_table_info(
            table_names=x.get("table_names_to_use")
        ),
    }
    if "dialect" in prompt_to_use.input_variables:
        inputs["dialect"] = lambda _: db.dialect
    return (
        RunnableMap(inputs)
        | prompt_to_use
        | llm.bind(stop=["\nSQLQuery:"])
        | NoOpOutputParser()
        | _strip
    )
