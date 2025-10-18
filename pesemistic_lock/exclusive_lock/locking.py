import logging
import threading
import time

from mysql.connector import connect

HOST = '127.0.0.1'
PORT = 3306
USER = 'dev_user'
PASSWORD = 'Test123!'
DATABASE = 'dev_db'

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s"
)
logger = logging.getLogger("book_without_lock")


class BookTicketWithoutLock:

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

    def clean_up(self):
        cursor = self.conn.cursor()
        cursor.execute("UPDATE slots SET user_id = NULL;")
        self.conn.commit()

    @staticmethod
    def book_tickets_without_lock(user_id: int):
        # CREATE A NEW CONNECTION FOR EACH THREAD
        thread_conn = connect(
            host=HOST,
            port=PORT,
            user=USER,
            password=PASSWORD,
            database=DATABASE
        )
        try:
            # UNSAFE — demonstrates race
            with thread_conn.cursor() as cursor:
                cursor.execute("SELECT id, seat_number FROM slots WHERE user_id IS NULL ORDER BY seat_number LIMIT 1;")
                row = cursor.fetchone()
                if not row:
                    return
                slot_id = row[0]
                time.sleep(1)
                cursor.execute("UPDATE slots SET user_id = %s WHERE id = %s;", (user_id, slot_id))
                thread_conn.commit()
        except Exception as error:
            thread_conn.rollback()
            logger.exception(f"failed to book slots for {user_id}", error)
        finally:
            thread_conn.close()

    @staticmethod
    def book_tickets_with_lock(user_id: int):
        # CREATE A NEW CONNECTION FOR EACH THREAD
        thread_conn = connect(
            host=HOST,
            port=PORT,
            user=USER,
            password=PASSWORD,
            database=DATABASE
        )
        try:
            # UNSAFE — demonstrates race
            with thread_conn.cursor() as cursor:
                cursor.execute("SELECT id, seat_number FROM slots "
                               "WHERE user_id IS NULL "
                               "ORDER BY seat_number LIMIT 1 "
                               "FOR UPDATE;")
                row = cursor.fetchone()
                if not row:
                    return
                slot_id = row[0]
                time.sleep(1)
                cursor.execute("UPDATE slots SET user_id = %s WHERE id = %s;", (user_id, slot_id))
                thread_conn.commit()
        except Exception as error:
            thread_conn.rollback()
            logger.exception(f"failed to book slots for {user_id}", error)
        finally:
            thread_conn.close()

    def get_all_user_id(self):
        try:
            with self.conn.cursor() as cursor:
                query = "SELECT id FROM users;"
                cursor.execute(query)
                result = cursor.fetchall()
                return [user_id[0] for user_id in result]  # Unpack tuples
        except Exception as error:
            logger.exception("failed to fetch users", error)
            return []

    def get_all_bookings(self):
        try:
            self.conn.commit()
            with self.conn.cursor() as cursor:
                query = "SELECT seat_number, user_id FROM slots ORDER BY seat_number;"
                cursor.execute(query)
                result = cursor.fetchall()
                for seat, user in result:
                    print(f"{seat} -- {'x' if user is None else user}")
        except Exception as error:
            logger.exception("failed to fetch slots", error)


if __name__ == '__main__':
    with BookTicketWithoutLock() as db:
        db.clean_up()
        users = db.get_all_user_id()
        threads = []
        for user_id in users:
            thread = threading.Thread(target=db.book_tickets_with_lock, args=(user_id,))
            threads.append(thread)
            thread.start()

        # Wait for all threads to complete
        for thread in threads:
            thread.join()

        print("\n=== Final Bookings ===")
        db.get_all_bookings()
