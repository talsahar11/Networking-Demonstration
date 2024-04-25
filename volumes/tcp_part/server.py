import decimal
import json
import socket

import clients_factory
import dhcp_utils
import mysql_adapter
from system_utils import get_ip


# Define a custom JSON encoder class that can handle Decimal objects
class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            return float(o)
        return super(DecimalEncoder, self).default(o)


# Create on the MYSQL server a table of clients and fill it with 1000 randomly generated clients
def simulate_clients_table():

    # Get the cnx and cursor of the connection
    cnx, cursor = mysql_adapter.MySQLSingleton.get_connection(mysql_instance)

    # Create the table 'Clients', only if not exists
    query = (
        "CREATE TABLE IF NOT EXISTS Clients (Identifier int NOT NULL AUTO_INCREMENT , FirstName varchar(255), LastName varchar(255), ID BIGINT, PhoneNumber "
        "varchar(255), Age int, City varchar(255), PRIMARY KEY (Identifier))")

    # Execute the 'CREATE TABLE' query
    cursor.execute(query)

    # Generate 1000 random clients
    clients = clients_factory.generate_clients(1000)

    # Fill the 'Clients' table with random generated clients.
    for client in clients:

        # Create the 'INSERT' query
        query = (f"INSERT INTO Clients (FirstName, LastName, ID, PhoneNumber, Age, City) "
                 f"VALUES ('{client.first_name}', '{client.last_name}', "
                 f"'{client.cid}', '{client.phone_number}', '{client.age}', "
                 f"'{client.city}')")

        # Execute the 'INSERT' query
        cursor.execute(query)

    # Commit the new data into the 'Clients' table
    cnx.commit()
    # Close the connection with the MYSQL server





def handle_client(data):
    cnx, cursor = mysql_adapter.MySQLSingleton.get_connection(mysql_instance)
    query = data.decode()
    # Parse the data into fields
    # Parse the data into fields
    cursor.execute(query)
    result = cursor.fetchall()
    cnx.commit()
    # Serialize the data into a JSON string
    if result is None or len(result) == 0:
        data = {'result': None}
    elif isinstance(result[0], (int, float, str)):
        data = {'result': result[0]}
    else:
        columns = [col[0] for col in cursor.description]
        if len(result) == 1:
            data = dict(zip(columns, result[0]))
        else:
            data = [dict(zip(columns, row)) for row in result]

    return json.dumps(data, cls=DecimalEncoder).encode()


"""------------------------ Main program -------------------------"""
# Assign to the DHCP server and receive an IP address
dhcp_utils.assign_to_dhcp_server()

# Get the instance of the MYSQL singleton class
mysql_instance = mysql_adapter.MySQLSingleton.get_instance()

myip = get_ip()
# Connect to the MYSQL server on localhost
mysql_adapter.MySQLSingleton.connect(mysql_instance, myip, (myip, 9999))

# Initiate and fill the clients table
simulate_clients_table()

# Open a listening socket for incoming queries from clients
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
sock.bind((myip, 30006))
sock.listen()

# Receiving queries, handling them and send the responses from the database back to the client
while True:
    connection, client_addr = sock.accept()
    try:
        print("Connection established")
        data = connection.recv(1024)
        response = handle_client(data)
        connection.send(response)
    finally:
        connection.close()

