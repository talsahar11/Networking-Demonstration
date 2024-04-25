import decimal
import json
import socket
import threading

import mysql_adapter, dhcp_utils, clients_factory
from connection import create_connection, MAX_PACKET_SIZE
from protocol_handler import *
from system_utils import get_ip

connections_data = dict()
handler_threads = list()


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


def pass_query_to_database(query):
    cnx, cursor = mysql_adapter.MySQLSingleton.get_connection(mysql_instance)
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


def handle_queries(connection):
    while connection.is_connected:
        if len(connection.whole_messages) > 0:
            query = connection.whole_messages.pop(0)
            print("Got full msg: ", query)
            response = pass_query_to_database(query)
            connection.send(response)


def create_handler_thread(connection):
    thread = threading.Thread(target=handle_queries, args=(connection,))
    return thread

def answer_with_synack(addr, sock):
    synack = create_syn_ack_message()
    sock.sendto(synack, addr)


def handle_data(data, connection):
    connection.incoming_queue.append(data)


def listen(my_address):

    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        sock.bind(my_address)
        print("Listening for connections...")
        while True:
            data, addr = sock.recvfrom(MAX_PACKET_SIZE + HEADER_SIZE)
            header = extract_header(data)
            if addr not in connections_data.keys():
                if header[SYN]:
                    answer_with_synack(addr, sock)
                elif data == create_ack_message():
                    new_connection = create_connection(addr[0], addr[1], sock, True)
                    connections_data[addr] = new_connection
                    new_connection.set_connected(True)
                    handler_thread = create_handler_thread(new_connection)
                    handler_thread.start()
                    print("New connection established: address - ", addr)

            else:
                handle_data(data, connections_data[addr])


def start_server(address):
    connections_thread = threading.Thread(target=listen, args=(address,))
    connections_thread.start()


"""------------------------ Main program -------------------------"""

# Get the instance of the MYSQL singleton class
mysql_instance = mysql_adapter.MySQLSingleton.get_instance()

# Assign to the DHCP server and receive an IP address
dhcp_utils.assign_to_dhcp_server()

myip = get_ip()
# Connect to the MYSQL server on localhost
mysql_adapter.MySQLSingleton.connect(mysql_instance, myip, (myip, 9999))

# Initiate and fill the clients table
simulate_clients_table()

start_server((myip, 30006))




