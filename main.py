import psycopg2

def connect_to_postgresql():
    conn = psycopg2.connect(
        dbname="postgres", 
        user="1234", 
        password="1234", 
        host="localhost", 
        port="5432"
    )
    return conn
def fetch_sales_data(conn):
    cur = conn.cursor()
    cur.execute("SELECT * FROM users LIMIT 10;")  
    rows = cur.fetchall()
    return rows
def main():
    print("Hello from qry-ai!")
    conn = connect_to_postgresql()
    data = fetch_sales_data(conn)
    print(data)

if __name__ == "__main__":
    main()
