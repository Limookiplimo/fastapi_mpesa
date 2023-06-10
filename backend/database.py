import psycopg2
from configs import host, database, port, user, password

# Establish db connection and create table
def create_table(table_name, columns):
    with psycopg2.connect(host=host, port=port, database=database, user=user, password=password) as conn:
        with conn.cursor() as cur:
            cur.execute(f"""
                create table if not exists {table_name}(
                {','.join(columns)})""")

# Insert data into db
def populate_table(table_name, data):
    with psycopg2.connect(host=host, port=port, database=database, user=user, password=password) as conn:
        with conn.cursor() as cur:
            cur.executemany(f"""
                insert into {table_name} values(
                    {', '.join(['%s'] * len(data[0]))})""", data)
            conn.commit()