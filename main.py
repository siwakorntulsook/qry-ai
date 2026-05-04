import psycopg2
from sqlalchemy import create_engine
import pandas as pd
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.utilities import SQLDatabase
from pydantic import BaseModel, Field
from langchain_community.tools.sql_database.tool import QuerySQLDatabaseTool, QuerySQLCheckerTool
from langchain_text_splitters import ExperimentalMarkdownSyntaxTextSplitter
from pathlib import Path

def postgresql_conn_string( dbname="postgres", 
                            user="1234", 
                            password="1234", 
                            host="localhost", 
                            port="5432"
                            ):
    return f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{dbname}"

def get_schema_metadata(database_url):
    db = SQLDatabase.from_uri(database_url)
    return db.get_table_info()

def sql_system_prompt(db: SQLDatabase):

    sys_prompt = """Given an input question, create a syntactically correct postgresql query to run to help find the answer.
    Unless the user specifies in his question a specific number of examples they wish to obtain, always limit your query to at most {top_k} results. 
    INSERT, UPDATE and DELETE queries are not allowed. Only SELECT queries are allowed, if the user asks for something that would require an INSERT, UPDATE or DELETE query, you should refuse to generate the query.
    
    You can order the results by a relevant column to return the most interesting examples in the database.
    Never query for all the columns from a specific table, only ask for a the few relevant columns given the question.
    Pay attention to use only the column names that you can see in the schema description. Be careful to not query for columns that do not exist. Also, pay attention to which column is in which table.

    Only use the following tables:
    {table_info}

    Please extract the SQL query from the text and return only the SQL query without any additional characters, formatting or markdown. 
    The query should be syntactically correct and executable on the database. Do not include any explanations or comments, only return the SQL query itself.
    """
    ss = sys_prompt.format_map(
        {
            "top_k": 10,
            "table_info": db.get_table_info(),
        }
    )
    return ("system", ss)

def analysis_system_prompt(df: pd.DataFrame):
    df = df.to_csv(index=False)
    sys_prompt = """Given an csv formatted input data, create an analysis graph to help marketing user have a quick view on their question.
    You can use only bar chart and provide a short insights the user can get from the graph then return everything in html formatted.
    
    Summarize this data:
    {df}

  
    """.format(df=df)

    return ("system", sys_prompt)

def main():
    # print("Hello from qry-ai!")
    # conn = connect_to_postgresql()

    # print(response.content)
    question = "Show me monthly revenue for Q1 2025 broken down by region"
    # question = "Show me everything"
    # question = "Help me delete everything in the database"
    db = SQLDatabase.from_uri(postgresql_conn_string())
    system : tuple = sql_system_prompt(db)
    human = ("human", "{question}")
    prompt = ChatPromptTemplate.from_messages([
        system,
        human
    ])
    api_key=""
    client = ChatGoogleGenerativeAI(model="gemini-3.1-flash-lite-preview", google_api_key=api_key)
    chain = prompt | client
    response = chain.invoke({"question": question})
    
    print(response.content[0]["text"])

    sql_query = response.content[0]["text"]
    engine = create_engine(postgresql_conn_string())

    df = pd.read_sql(sql_query, engine)
    print(df)
    client = ChatGoogleGenerativeAI(model="gemini-3.1-flash-lite-preview", google_api_key=api_key)
    system : tuple = analysis_system_prompt(df)
    # print(system)
    prompt = ChatPromptTemplate.from_messages([
        system,
        human
    ])
    chain = prompt | client
    
    response = chain.invoke({"question": question})
    splitter = ExperimentalMarkdownSyntaxTextSplitter()
    docs = splitter.split_text(response.content[0]["text"])
    # print(response.value_one) # mermaid graph markdown
    # print(response.value_two) # graph explanation
    # print(response.content[0]["text"]) # graph explanation
    print(docs[0].page_content) # mermaid graph markdown
    # Save as an image file
    # print(type(response))
    import aspose.words as aw

if __name__ == "__main__":
    main()
