import psycopg2
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.utilities import SQLDatabase
from langchain_community.tools.sql_database.tool import QuerySQLDatabaseTool, QuerySQLCheckerTool


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

def system_prompt(db: SQLDatabase):

    sys_prompt = """Given an input question, create a syntactically correct postgresql query to run to help find the answer. Unless the user specifies in his question a specific number of examples they wish to obtain, always limit your query to at most {top_k} results. You can order the results by a relevant column to return the most interesting examples in the database.

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
    
def main():
    # print("Hello from qry-ai!")
    # conn = connect_to_postgresql()

    # print(response.content)
    question = "Show me monthly revenue for Q1 2025 broken down by region"
    db = SQLDatabase.from_uri(postgresql_conn_string())
    system : tuple = system_prompt(db)
    human = ("human", "{question}")
    prompt = ChatPromptTemplate.from_messages([
        system,
        human
    ])
    client = ChatGoogleGenerativeAI(model="gemini-3-flash-preview", google_api_key='')
    chain = prompt | client
    response = chain.invoke({"question": question})
    
    print(response.content[0]["text"])

    data = QuerySQLDatabaseTool(db=db).invoke(response.content[0]["text"])
    print(data)
    # print(type(response.content))
    # print(type(response))


if __name__ == "__main__":
    main()
