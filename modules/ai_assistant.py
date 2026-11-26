import anthropic


MODEL_NAME = "claude-sonnet-4-5-20250929"


def generate_sql(df, question, api_key):

    client = anthropic.Anthropic(
        api_key=api_key
    )

    schema = "\n".join(
        f"- {column}: {dtype}"
        for column, dtype in df.dtypes.items()
    )

    prompt = f"""
You are an expert data analyst.

The user has uploaded a Pandas dataset.
The SQL table name is uploaded_data.

COLUMN SCHEMA:
{schema}

SAMPLE DATA:
{df.head(5).to_csv(index=False)}

USER QUESTION:
{question}

INSTRUCTIONS:
1. Generate one valid DuckDB SELECT query.
2. Use only the uploaded_data table.
3. Never generate INSERT, UPDATE, DELETE,
   DROP, ALTER, CREATE or other write operations.
4. Do not access external files or databases.
5. Do not invent column names.
6. Use LIMIT 100 where appropriate.
7. Return ONLY the SQL query.
8. Do not use Markdown code fences.
"""

    response = client.messages.create(
        model=MODEL_NAME,
        max_tokens=1200,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    sql = "".join(
        block.text
        for block in response.content
        if block.type == "text"
    ).strip()

    # Remove accidental Markdown code fences
    if sql.startswith("```"):
        sql = sql.split("\n", 1)[-1]
        sql = sql.rsplit("```", 1)[0].strip()

    return sql


def explain_query_result(
    question,
    sql,
    result,
    api_key
):

    client = anthropic.Anthropic(
        api_key=api_key
    )

    result_data = result.head(50).to_csv(
        index=False
    )

    prompt = f"""
You are DataMind AI, an intelligent data analyst.

USER QUESTION:
{question}

SQL QUERY EXECUTED:
{sql}

ACTUAL QUERY RESULTS:
{result_data}

INSTRUCTIONS:
1. Answer the user's question clearly.
2. Use only the supplied query results.
3. Do not invent numbers or observations.
4. Mention important findings.
5. If the result is empty, explain that.
6. Keep the answer professional and understandable.
"""

    response = client.messages.create(
        model=MODEL_NAME,
        max_tokens=1200,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    return "\n".join(
        block.text
        for block in response.content
        if block.type == "text"
    )
