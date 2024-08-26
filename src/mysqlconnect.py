import mysql.connector
from mysql.connector import errorcode

from utils import appendLog


class NoRecords(Exception):
    pass


class MySQLConnection:
    connection: mysql.connector.connection.MySQLConnection
    used_kwargs_for_mysql: dict
    data_from_db: list

    def __new__(self):
        if not hasattr(self, 'instance'):
            self.instance = super(MySQLConnection, self).__new__(self)
            self.__clearFields(self)
        return self.instance

    def connect(self, **kwargs_for_mysql):
        if not kwargs_for_mysql:
            raise ValueError(
                'Keyword parameters for MySQL connection is empty.'
            )

        if kwargs_for_mysql == self.used_kwargs_for_mysql \
           and self.isConnected():
            return

        self.used_kwargs_for_mysql = kwargs_for_mysql

        try:
            self.connection = mysql.connector.connect(**kwargs_for_mysql)
        except mysql.connector.Error as err:
            self.__clearFields()

            if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                appendLog((
                    err.errno,
                    ': Connection to MySQL server failed, check'
                        ' your username or password.'
                ))
            elif err.errno == errorcode.ER_BAD_DB_ERROR:
                appendLog((
                    err.errno,
                    ': Connection to database failed, no access'
                        ' or database don\'t exist.'
                ))
            else:
                appendLog(f'{err.errno}: {err}')

            raise ConnectionError()
            
        if not self.isConnected():
            self.__clearFields()
            appendLog(
                'Connection to MySQL server failed, unknow error.'
                    ' Try again.'
            )
            raise ConnectionError()

    def isConnected(self) -> bool:
        if self.connection.is_connected():
            return True
        else:
            return False

    def executeQuery(self, query: str=None, commit: bool=False) -> tuple:
        if not query:
            raise ValueError('Passed empty query.')

        if not isinstance(query, str):
            raise TypeError('Wrong query type, only str')

        if not self.isConnected():
            appendLog(
                'Failed to execute query. No connection to MySQL server.'
            )
            raise ConnectionError()

        try:
            cursor = self.connection.cursor()
            cursor.execute(query)
            self.data_from_db = cursor.fetchall()
        except mysql.connector.Error as err:
            appendLog(err)
            raise ConnectionError()
        else:
            column_names = cursor.column_names

            if not column_names:
                raise NoRecords()

            if commit:
                cursor.commit()
        finally:
            if isinstance(
                cursor,
                mysql.connector.connection.MySQLCursor
            ):
                cursor.close()

            return column_names

    def close(self):
        if self.isConnected(self):
            self.connection.close()
            self.__clearFields()

    def __clearFields(self):
        self.used_kwargs_for_mysql = dict()
        self.data_from_db = list()
