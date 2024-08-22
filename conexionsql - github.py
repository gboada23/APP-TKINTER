# mysql_manager.py
import pandas as pd
import urllib.parse
from sqlalchemy import create_engine
from mysql.connector import Error
from sqlalchemy.exc import SQLAlchemyError
class MYSQL:
    def __init__(self):
        self.user = 'tu usuario'
        self.password = 'tu contraseña'
        self.host = 'tu IP o URL'
        self.database = 'Tu base de datos'
        # Inicializa la conexión al crear la instancia
        self.engine = self.create_connection()

    def create_connection(self):
        # Método para crear y retornar la conexión
        password_encoded = urllib.parse.quote(self.password)
        connection_string = f'mysql+mysqlconnector://{self.user}:{password_encoded}@{self.host}/{self.database}'
        engine = create_engine(connection_string)
        return engine

    def tabla_inventario(self):
        query = '''
            SELECT i1.FECHA, i1.unidad, i1.CODIGO, i1.alterno, i1.PRODUCTO, i1.FISICO
            FROM inventario_dat i1
            INNER JOIN (
                SELECT CODIGO, unidad, MAX(FECHA) AS MaxFecha
                FROM inventario_dat
                GROUP BY CODIGO
            ) i2
            ON i1.CODIGO = i2.CODIGO AND i1.FECHA = i2.MaxFecha;
        '''
        return self.fetch_data(query)

    def tabla_baremos(self):
        query = '''SELECT * FROM v_baremos;'''
        return self.fetch_data(query)

    def fetch_data(self, query):
        try:
            df = pd.read_sql(query, self.engine)
            return df
        except Error as e:
            print(f"Error al conectar a MySQL: {e}")
            return None
class SQLSERVER:
    def __init__(self):
        self.username = 'tu usuario'
        self.password = 'tu contraseña'
        self.server = 'tu IP o URL'
        self.database = 'Tu base de datos'
        self.engine = self.create_connection()

    def create_connection(self):
        conn_str = f"mssql+pymssql://{self.username}:{self.password}@{self.server}/{self.database}"
        engine = create_engine(conn_str)
        return engine

    def fetch_data(self, query):
        try:
            df = pd.read_sql(query, self.engine)
            return df
        except SQLAlchemyError as e:
            print(f"Error al conectar a SQL Server: {e}")
            return None

    def add_data(self, table_name, df):
        try:
            with self.engine.begin() as connection:
                df.to_sql(table_name, connection, if_exists='append', index=False)
                return f"{len(df)} datos agregados exitosamente"
        except SQLAlchemyError as e:
            return f"Error al agregar datos a SQL Server: {str(e)}"

    def delete_records_with_null_date(self, table_name, date_column):
        try:
            with self.engine.connect() as connection:
                delete_query = f"DELETE FROM {table_name} WHERE {date_column} IS NULL"
                connection.execute(delete_query)
                print("Registros eliminados exitosamente")
        except SQLAlchemyError as e:
            print(f"Error al eliminar registros de SQL Server: {e}")

    def filtro_codclie(self, codclie):
        query = f"SELECT * FROM dbo.NEGOCIACIONDAT WHERE codclie = '{codclie}'"
        return self.fetch_data(query)


    def tabla_negociaciondat(self):
        """SELECT
        codclie,
        fechaneg,
        comedor,
        familiainicial,
        codinicial,
        nominicial,
        undinicial,
        solicitadoinicial,
        costodolarinicial,
        costototaldolarinicial,
        preciodolarinicial,
        preciototaldolarinicial,
        rentabilidadinicial,
        utilidadinicial
                FROM dbo.NEGOCIACIONDAT"""
        query = '''SELECT * FROM dbo.NEGOCIACIONDAT'''
        return self.fetch_data(query)

