import psycopg

user_db_config = {
        'dbname': 'publishing_house',
        'user': 'admin',
        'password': 'admin',
        'host': 'localhost',
        'port': '5432'
        }

username = 'director'
connection = psycopg.connect(**user_db_config)
cursor = connection.cursor()
query = "SELECT position FROM worker WHERE login = %s";
cursor.execute(query, (username,))
connection.commit()
role = cursor.fetchone()[0]
print(role)
