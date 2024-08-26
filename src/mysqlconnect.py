import mysql.connector
from mysql.connector import errorcode

from utils import appendLog


class MySQLConnection:
    connection: mysql.connector.connection.MySQLConnection
    used_kwargs_for_mysql: dict
    data_from_db: list

    def __new__(self):
        if not hasattr(self, 'instance'):
            self.instance = super(MySQLConnection, self).__new__(self)
            self.__clearFields(self)
        return self.instance

    def connect(self, **kwargs_for_mysql) -> bool:
        if not kwargs_for_mysql:
            raise ValueError('Keyword parameters for MySQL'
                             ' connection is empty.')

        if kwargs_for_mysql == self.used_kwargs_for_mysql \
           and self.isConnected():
            return True

        self.used_kwargs_for_mysql = kwargs_for_mysql

        self.connection = None
        try:
            self.connection = mysql.connector.connect(**kwargs_for_mysql)
        except mysql.connector.Error as err:
            self.__clearFields()

            if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                appendLog((err.errno,
                           ': Connection to MySQL server failed, check'
                           ' your username or password.'))

                return False
            elif err.errno == errorcode.ER_BAD_DB_ERROR:
                appendLog((err.errno,
                           ': Connection to database failed, no access'
                           ' or database don\'t exist.'))

                return False
            else:
                appendLog(f'{err.errno}: {err}')
                return False

        if not self.isConnected():
            self.__clearFields()
            appendLog('Connection to MySQL server failed, unknow error.'
                      ' Try again.')

            return False

        return True

    def isConnected(self) -> bool:
        if isinstance(self.connection,
                      mysql.connector.connection_cext.CMySQLConnection) \
           and self.connection.is_connected():

            return True
        else:
            return False

    def executeQuery(self, query: str, commit: bool = False) -> tuple:
        if not self.isConnected():
            appendLog('Failed to execute query.'
                      ' No connection to MySQL server.')

            return None

        if not query or not isinstance(query, str):
            return None

        cursor: mysql.connector.connection.MySQLCursor = None
        try:
            cursor = self.connection.cursor()
            cursor.execute(query)
            self.data_from_db = cursor.fetchall()
            column_names = cursor.column_names

            if commit:
                cursor.commit()
        except mysql.connector.Error as err:
            appendLog(err)
            column_names = None
        finally:
            if isinstance(cursor,
                          mysql.connector.connection.MySQLCursor):

                cursor.close()

        return column_names

    def close(self):
        if self.isConnected(self):
            self.connection.close()
            self.__clearFields()

    def __clearFields(self):
        self.used_kwargs_for_mysql = dict()
        self.data_from_db = list()
