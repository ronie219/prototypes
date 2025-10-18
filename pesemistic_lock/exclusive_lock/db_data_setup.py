from mysql.connector import connect, MySQLConnection
import logging
from faker import Faker

HOST = '127.0.0.1'
PORT = 3306
USER = 'dev_user'
PASSWORD = 'Test123!'
DATABASE = 'dev_db'

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s"
)
logger = logging.getLogger("db_setup")
fake = Faker()


class DatabaseOperations:

    def __init__(self):
        self.conn = None

    def __enter__(self):
        self.conn = connect(
            host=HOST,
            port=PORT,
            user=USER,
            password=PASSWORD,
            database=DATABASE
        )
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.conn:
            self.conn.close()

    def create_table(self):
        if not self.conn:
            raise Exception("Database connection not established")
        create_user_table_query = """
                                CREATE TABLE IF NOT EXISTS users (
                                    id INT AUTO_INCREMENT PRIMARY KEY,
                                    name VARCHAR(100) NOT NULL,
                                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                                    );
                                """
        create_slot_table_query = """ 
                                CREATE TABLE IF NOT EXISTS slots (
                                    id INT AUTO_INCREMENT  PRIMARY KEY,
                                    seat_number VARCHAR(10) NOT NULL,
                                    user_id INT,
                                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                                    FOREIGN KEY (user_id) REFERENCES users(id)
                                        ON DELETE SET NULL
                                    )
                                """
        cursor = self.conn.cursor()
        try:
            cursor.execute(create_user_table_query)
            cursor.execute(create_slot_table_query)
            self.conn.commit()
            logger.info("Table created successfully")
        except Exception as error:
            logger.exception(f"Not able to create table. error: {error}")

    def insert_fake_user(self, user_count: int):
        cursor = self.conn.cursor()
        insert_user_query = "INSERT INTO users (name) VALUES (%s);"
        users = [(fake.name(),) for _ in range(user_count)]
        try:
            cursor.executemany(insert_user_query, users)
            self.conn.commit()
            logger.info("users created successfully")
        except Exception as error:
            logger.exception(f"Not able to create users. error", error)

    def create_seats(self, seat_counts: int):
        try:
            cursor = self.conn.cursor()
            insert_user_query = "INSERT INTO slots (seat_number) VALUES (%s);"
            seats = [(f"{num}{chr(char)}",) for num in range(1, seat_counts + 1) for char in range(65, 71)]
            cursor.executemany(insert_user_query, seats)
            self.conn.commit()
            logger.info("seat created successfully")
        except Exception as err:
            logger.exception(f"Not able to create seats", err)


if __name__ == '__main__':
    with DatabaseOperations() as db:
        db.create_table()
        db.insert_fake_user(20)
        db.create_seats(10)
