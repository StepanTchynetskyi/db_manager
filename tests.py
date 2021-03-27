import unittest

import psycopg2
import threading
import db_pooling as db
from password import PASSWORD

def create_user():
    with db.db_pool as conn:
        cursor = conn.cursor()
        query = "INSERT INTO todolist_todolist (name, description) VALUES ('List1', 'About');"
        cursor.execute(query)
        conn.commit()


def create_without_pool():
    connection = psycopg2.connect(dbname="ToDoDatabase", user="postgres", password=PASSWORD, host='localhost')
    cursor = connection.cursor()
    query = "INSERT INTO todolist_todolist (name, description) VALUES ('List1', 'About');"
    cursor.execute(query)
    connection.commit()
    cursor.close()
    connection.close()


class UserTest(unittest.TestCase):
    # def test1(self):
    #     for _ in range(100):
    #         create_user()

    # def test2(self):
    #     for _ in range(100):
    #         create_without_pool()
    def test3(self):
        processes = [threading.Thread(target=create_user) for _ in range(1000)]
        for process in processes:
            process.start()
        for process in processes:
            process.join()

    # def test4(self):
    #     processes = [threading.Thread(target=create_without_pool) for _ in range(1000)]
    #     for process in processes:
    #         process.start()
    #     for process in processes:
    #         process.join()

if __name__ == "__main__":
    unittest.main()
