from faker import Faker
from sqlalchemy import create_engine
import pandas as pd

def postgresql_conn_string( dbname="postgres", 
                            user="1234", 
                            password="1234", 
                            host="localhost", 
                            port="5432"
                            ):
    return f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{dbname}"

def main():
    
    fake = Faker()

    conn = postgresql_conn_string()
    order_list = []
    for _ in range(100000):
        data = {'order_id': _, 'customer_id': fake.random_int(min=10, max=100), 'amount': fake.pydecimal(left_digits=3, right_digits=2, positive=True), 'region': fake.random_element(elements=("North", "South", "East", "West")), 'created_at': fake.date_time_between(start_date='-2y', end_date='-1y').strftime("%Y-%m-%d %H:%M:%S")}
        order_list.append(data)
    df = pd.DataFrame(order_list)
    df.to_sql("orders", con=conn, if_exists="replace", index=False)
    print(df)

    customer_list = []
    for _ in range(25000):
        data = {'customer_id': _, 'name': fake.name(), "email": fake.email(), "plan_tier": fake.random_element(elements=("basic", "pro", "enterprise")), "signup_date": fake.date_time_between(start_date='-2y', end_date='-1y').strftime("%Y-%m-%d %H:%M:%S")}
        customer_list.append(data)
    df = pd.DataFrame(customer_list)
    df.to_sql("customers", con=conn, if_exists="replace", index=False)
    print(df)

    products_list = []
    for _ in range(250):
        data = {'product_id': _, 'name': fake.word(), "category": fake.random_element(elements=("electronics", "clothing", "home", "sports")), "price": fake.pydecimal(left_digits=3, right_digits=2, positive=True)}
        products_list.append(data)
    df = pd.DataFrame(products_list)
    df.to_sql("products", con=conn, if_exists="replace", index=False)
    print(df)

    order_items_list = []
    for _ in range(400):
        data = {'order_items_id': _, "product_id": fake.random_int(min=0, max=49), "quantity": fake.random_int(min=1, max=5), "unit_price": fake.pydecimal(left_digits=3, right_digits=2, positive=True)}
        order_items_list.append(data)
    df = pd.DataFrame(order_items_list)
    df.to_sql("order_items", con=conn, if_exists="replace", index=False)
    print(df)

if __name__ == "__main__":
    main()
