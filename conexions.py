import pyodbc
import mysql.connector
from decouple import config


class systemRRHH:
    def __init__(self):
        self.conn_str = (
            f'DRIVER={{ODBC Driver 17 for SQL Server}};'
            f'SERVER={config("DB_HOST")};'
            f'DATABASE={config("DB_DATABASE")};'
            f'UID={config("DB_USERNAME")};'
            f'PWD={config("DB_PASSWORD")};'
        )
        self.conn = None
        self.cursor = None

    def connect(self):
        self.conn = pyodbc.connect(self.conn_str)
        self.cursor = self.conn.cursor()

    def execute_query(self, query):
        if not self.cursor:
            raise Exception("You must connect to the database first")
        self.cursor.execute(query)

    def print_results(self):
        if not self.cursor:
            raise Exception("You must execute a query first")
        for row in self.cursor:
            print(row)

class systemArchivoApp:
    def __init__(self):
        self.host = config('DB_HOST_AR')
        self.user = config('DB_USERNAME_AR')
        self.password = config('DB_PASSWORD_AR')
        self.database = config('DB_DATABASE_AR')
        self.connection = None
        self.cursor = None

    def connect(self):
        try:
            self.connection = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database
            )
            if self.connection.is_connected():
                self.cursor = self.connection.cursor()
                # print("Conexión a MySQL establecida.")
        except mysql.connector.Error as err:
            print(f"Error al conectar a MySQL: {err}")

    def disconnect(self):
        if self.connection:
            self.connection.close()
            # print("Conexión a MySQL cerrada.")

    # Puedes agregar más métodos según tus necesidades, como ejecutar consultas, insertar datos, etc.
    def execute_query(self, query):
        try:
            if self.cursor:
                self.cursor.execute(query)
                self.connection.commit()
                # print("Consulta ejecutada con éxito.")
            else:
                print("El cursor no está inicializado.")
        except mysql.connector.Error as err:
            print(f"Error al ejecutar la consulta Query: {err}")
