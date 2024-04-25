import mysql.connector
from clients_factory import Client


# MYSQLSingleton class represents a singleton connection to the MYSQL database and used to:
#   * Establish and close the connection
#   * Get the connection objects
class MySQLSingleton:

    __instance = None

    def __init__(self):
        if MySQLSingleton.__instance is not None:
            raise Exception("MySQLSingleton is a singleton class, use MySQLSingleton.get_instance() to get an instance.")
        else:
            MySQLSingleton.__instance = self

    # Connect to the mysql server located on a address provided as an argument
    def connect(self, server_address, clients_address):
        global cnx
        global cursor
        config = {
            'user': 'root',
            'password': 'examplepassword',
            'host': f'{server_address}',
            'port': 30452,
            'database': 'exampledb',
        }
        cnx = mysql.connector.connect(**config)
        cnx.config()
        cursor = cnx.cursor()
    # Return the singleton instance
    @staticmethod
    def get_instance():
        if MySQLSingleton.__instance is None:
            MySQLSingleton()
        return MySQLSingleton.__instance

    # Close the connection
    def close_connection(self):
        cursor.close()
        cnx.close()

    # Get the connection objects
    def get_connection(self):
        print("Im Here")
        return cnx, cursor





"""----------------------------MYSQL Queries----------------------------------"""


def insert(client: Client):
    query = (f"INSERT INTO Clients (FirstName, LastName, ID, PhoneNumber, Age, City) VALUES ('{client.first_name}'"
             f", '{client.last_name}', {client.cid}, '{client.phone_number}', {client.age}, "
             f"'{client.city}')")
    return query

def remove_by_cid(cid):
    query = (f"DELETE FROM Clients WHERE ID = {cid}")
    return query


def get_client_by_cid(cid):
    query = (f"SELECT * FROM Clients WHERE ID = {cid}")
    return query

def get_clients_by_age(age):
    query = (f"SELECT * FROM Clients WHERE Age = {age}")
    return query


def update(client):
    query = (f"UPDATE Clients SET FirstName = '{client.first_name}', LastName = '{client.last_name}', PhoneNumber = '{client.phone_number}',"
             f" Age = {client.age}, City = '{client.city}' WHERE ID = {client.cid}")
    return query


def get_all():
    query = ("SELECT * FROM Clients")
    return query


def get_average_age():
    query = ("SELECT AVG(age) AS avg_age from Clients")
    return query


def get_number_of_clients():
    query = "SELECT COUNT(*) FROM Clients"
    return query


def get_most_common_city():
    query = ("SELECT City, COUNT(*) as count FROM Clients GROUP BY City ORDER BY count DESC LIMIT 1")
    return query


def delete_all_clients():
    query = ("DELETE FROM Clients")
    return query

# Global vars init
cnx = None
cursor = None
