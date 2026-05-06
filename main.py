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
    Also make sure to address special characters such as %% instead of % in the query.
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
    Choose the appropriate graphic representation from the following: bar, line, table or KPI card.
    Always prioritized graph over table or KPI card and Always provide data and axis accordingly. 
    Also provide a short insights the user can get from the graph then return everything in html formatted.
    
    Summarize this data:
    {df}

  
    """.format(df=df)

    return ("system", sys_prompt)
def calling_ai(system, question):

    api_key=""
    human = ("human", "{question}")
    prompt = ChatPromptTemplate.from_messages([
        system,
        human
    ])
    client = ChatGoogleGenerativeAI(model="gemini-3.1-flash-lite-preview", google_api_key=api_key)
    chain = prompt | client
    response = chain.invoke({"question": question})
    return  response.content[0]["text"]

def main():
    ### input question from the user ###
    question = "Show me monthly revenue for Q1 2025 broken down by region"
    # question = "Show me everything"
    # question = "Help me delete everything in the database"
    # question = "What are the top 5 most popular products based on the number of orders?"
    # question = "What plan tier has the highest average order amount in Q2 2025? broken down by region"
    # question = "show me Revenue for Narnia region in 2025"

    ### Create connection to the database and get the schema metadata ###
    db = SQLDatabase.from_uri(postgresql_conn_string())

    ### Create the system prompt for the LLM to generate the SQL query based on the question and the database schema ###
    system_prompt = sql_system_prompt(db)
    sql_query = calling_ai(system_prompt, question)
    print(sql_query)

    ### Query the database and get the results in a dataframe ###
    engine = create_engine(postgresql_conn_string())
    df = pd.read_sql(sql_query, engine)
    print(df)

    ### Create the system prompt for the LLM to generate the analysis graph based on the question and the dataframe results ###
    system_prompt = analysis_system_prompt(df)
    response = calling_ai(system_prompt, question)
    splitter = ExperimentalMarkdownSyntaxTextSplitter()
    docs = splitter.split_text(response)
    print(docs[0]) # html content
    
if __name__ == "__main__":
    main()
