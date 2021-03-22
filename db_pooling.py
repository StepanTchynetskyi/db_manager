import psycopg2
import time
from threading import Lock
from contextlib import contextmanager

class DBPool:
    def __init__(self, min_conn, max_conn, user, passwd, db_name, host, port, ttl):
        self.min_conn = min_conn
        self.max_conn = max_conn
        self.user = user
        self.passwd = passwd
        self.db_name = db_name,
        self.host = host
        self.port = port
        self.ttl = ttl
        self.pool = []
        self.active_conns = 0
        self._lock = Lock()
        for i in range(self.min_conn):
            self._connect()

    def _connect(self):
        connection = psycopg2.connect(dbname=self.db_name, user=self.user, password=self.passwd, host=self.host,
                                      port=self.port)
        connection ={"connection": connection, "created_at": time.time()}
        self.pool.append(connection)
        self.active_conns += 1
        return connection

    def _get_conn(self):
        self._lock.acquire()
        connection = None
        while not connection:
            if self.pool:

                connection = self.pool.pop()
            elif self.active_conns < self.max_conn:
                connection = self._connect()
            time.sleep(1)
        self._lock.release()
        return connection

    def _close(self, connection):
        self.active_conns -= 1
        connection['connection'].close()

    def _close_all(self):
        self._lock.acquire()
        for conn in self.pool:
            self._close(conn)
        self._lock.release()

    def _release_conn(self, connection):
        self.pool.append(connection)

    @contextmanager
    def manager(self):
        with self._lock:
            connection = self._get_conn()

        try:
            yield connection["connection"]
        except:
            self._close(connection)

        if connection['created_at'] + self.ttl < time.time():
            self._release_conn(connection)
        else:
            self._close(connection)
