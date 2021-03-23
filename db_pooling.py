import logging
import time
from threading import RLock
import psycopg2
from dbsetup import database

logging.basicConfig(level=logging.INFO)
GET_DELAY = 0.1

class DBPool:
    def __init__(self, user, passwd, dbname, host, port, max_conn):
        self.user = user
        self.passwd = passwd
        self.db_name = dbname
        self.host = host
        self.port = port
        self.max_conn = max_conn
        self.log = logging.getLogger("DBPool")
        self.lock = RLock()
        self.toRelease = None
        self._pool = [self._connect() for _ in range(max_conn)]

    def __del__(self):
        self.log.info("Close all conections")
        for connection in self._pool:
            self._close_connection(connection)

    def __enter__(self):
        connection = next(self.manager())
        # with self.lock:
        #     connection = self._get_connection()
        self.toRelease = connection
        return connection

    def __exit__(self, exc_type, exc_value, tb):
        try:
            self._release_connection(self.toRelease)
        except exc_type:
            self._close_connection(self.toRelease)
            connection = self._connect()
            self._pool.append(connection)

    def _close_connection(self, connection):
        self.log.info("Close %s connection", connection)
        connection.close()

    def _connect(self):
        connection = psycopg2.connect(dbname=self.db_name, user=self.user, password=self.passwd, host=self.host,
                                      port=self.port)
        self.log.info('Created connection object: %s.', connection)
        return connection

    def _get_connection(self):
        while True:
            try:
                connection = self._pool.pop()
                self.log.info("Get %s connection", connection)
                return connection
            except IndexError:
                time.sleep(GET_DELAY)

    def _release_connection(self, connection):
        self.log.info("Release %s connection", connection)
        self._pool.append(connection)

    def manager(self):
        with self.lock:
            connection = self._get_connection()

        yield connection


db_pool = DBPool(**database, max_conn=10)
