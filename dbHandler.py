import sqlite3
from user import User


class SqliteDB:
    """A class that handles SQLITE work"""

    def __init__(self, path):
        self.path = path

    def connect(self):
        conn = sqlite3.connect(self.path)
        c = conn.cursor()
        return conn, c

    def create_userTable(self):
        conn, c = self.connect()
        # todo change key to first_last
        c.execute("""CREATE TABLE users (
                        id unique,
                        first text,
                        last text,
                        birthday timestamp
                        )""")

    def insert_user(self, first, last, birthday, _connect=None):
        """
        adds the user to the users table

        :param _connect:
        :param first:
        :param last:
        :param birthday:
        :return:
        """
        first = first.lower()
        last = last.lower()

        if _connect:
            conn, c = _connect
        else:
            conn, c = self.connect()

        if self.search(first, last, _connect=(conn, c)):
            self.update(first, last, birthday, (conn, c))
            return True

        c.execute("INSERT into users VALUES (?,?,?,?)", (f'{first}_{last}', first, last, birthday))
        conn.commit()
        return True

    def likeSearch(self, first = "", last = "%", connect=None):
        """
        searches user in the users table with partial search

        :param connect:
        :param first:
        :param last:
        :return:
        """
        if connect:
            conn, c = connect
        else:
            conn, c = self.connect()

        c.execute("select * from users where first LIKE ? and last LIKE ?", (first, last))
        return c.fetchall()

    def search(self, first, last, birthday="", _connect=None):
        """
        searches user in the users table with identical search

        :param _connect:
        :param first:
        :param last:
        :return:
        """
        if _connect:
            conn, c = _connect
        else:
            conn, c = self.connect()

        c.execute("select 1 from users where id=? and birthday like ?", (f"{first}_{last}", f"{birthday}%"))
        return c.fetchone()

    def update(self, first, last, birthday, _connect=None):

        if _connect:
            conn, c = _connect
        else:
            conn, c = self.connect()

        c.execute("UPDATE users set birthday=? where id=?", (birthday, f"{first}_{last}"))
        conn.commit()

    def delete(self, first, last, _connect=None):

        if _connect:
            conn, c = _connect
        else:
            conn, c = self.connect()

        if self.search(first, last, _connect=(conn, c)):
            c.execute("Delete from users where id=? ", (f"{first}_{last}",))
            conn.commit()
            return True

        return False
