import psycopg

# connect to DB
with psycopg.connect("dbname=py_test_db user=postgres") as conn:
    # Open a cursor to perform DB operation
    with conn.cursor() as cur:
        # Execute a command: create new table
            cur.execute("""
                CREATE TABLE test (
                    id serial PRIMARY KEY,
                    num integer,
                    data text )
            """)

            # Pass data to fill query placeholders and let Psycopg
            # perform the correct conversion (no SQL injections!)
            cur.execute (
                    "INSERT INTO test (num, data) VALUES (%s, %s)",
                    (100, "abc'def"))

            # Query the DB and obtain data as Python objects
            cur.execute("SELECT * FROM TEST")
            cur.fetchone()
            # will return text 100, "abc'def"

            # the fetchmany will return several records

            for record in cur:
                print(record)

            # Make the changes to the database persistent
            conn.commit()
