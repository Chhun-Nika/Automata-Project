import mysql.connector;

def get_connection():
    try:
        conn = mysql.connector.connect(
            host='localhost',
            user='root',
            password='nika@Ax99',
            database='automata_db'
        )
        return conn
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return None
    

conn = get_connection();
# Check if the database connection was successful
if conn.is_connected():
    print("Connected to the database successfully.");
else:
    print("Failed to connect to the database.");
    exit(1);
        