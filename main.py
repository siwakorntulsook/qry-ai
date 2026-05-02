
def connect_to_postgresql():
    conn = psycopg2.connect(
        dbname="your_dbname", 
        user="your_user", 
        password="your_password", 
        host="your_host", 
        port="your_port"
    )
    return conn
def fetch_sales_data(conn):
    cur = conn.cursor()
    cur.execute("SELECT * FROM sales LIMIT 10;")  
    rows = cur.fetchall()
    return rows
def main():
    print("Hello from qry-ai!")
    conn = connect_to_postgresql()
    data = fetch_sales_data(conn)

if __name__ == "__main__":
    main()
