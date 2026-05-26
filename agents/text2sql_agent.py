from sqlalchemy import create_engine, text

from langchain_community.utilities import SQLDatabase

from agents.llm_adapter import LLMAdapter

import re


class Text2SQLAgent:

    def __init__(self, db_path):

        # ==================================
        # DATABASE
        # ==================================

        self.engine = create_engine(
            f"sqlite:///{db_path}"
        )

        self.db = SQLDatabase(
            self.engine
        )

        # ==================================
        # LLM ADAPTER
        # ==================================

        self.llm = LLMAdapter()

    # ======================================
    # DATABASE SCHEMA
    # ======================================

    def get_schema(self):

        return self.db.get_table_info()

    # ======================================
    # GENERATE SQL
    # ======================================

    def generate_sql(self, question):

        schema = self.get_schema()

        prompt = f"""
You are a SQL expert.

Convert the following natural language
question into a valid SQLite SQL query.

DATABASE SCHEMA:
{schema}

QUESTION:
{question}

IMPORTANT:
- Return ONLY SQL
- No markdown
- No explanations
- SQLite syntax only
"""

        response = self.llm.generate(
            prompt=prompt,
            max_tokens=200
        )

        sql_query = response["text"]

        # ==================================
        # CLEAN SQL OUTPUT
        # ==================================

        sql_query = sql_query.replace(
            "```sql",
            ""
        )

        sql_query = sql_query.replace(
            "```",
            ""
        )

        sql_query = sql_query.strip()

        return sql_query

    # ======================================
    # EXECUTE SQL
    # ======================================

    def execute_sql(self, sql_query):

        try:

            with self.engine.connect() as conn:

                result = conn.execute(
                    text(sql_query)
                )

                return result.fetchall()

        except Exception as e:

            return f"SQL Execution Error: {str(e)}"

    # ======================================
    # FULL QUERY PROCESS
    # ======================================

    def process_query(self, question):

        sql_query = self.generate_sql(
            question
        )

        result = self.execute_sql(
            sql_query
        )

        return {

            "generated_sql":
                sql_query,

            "result":
                str(result)
        }