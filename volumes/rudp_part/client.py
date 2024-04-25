import json
import socket

import dns

import dhcp_utils, clients_factory, mysql_adapter
from connection import Connection
from system_utils import get_ip


# Establish connection with the server by our rudp protocol
def establish_connection(serv_addr, my_addr):
    # Open new socket and bind it to the current clients address
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(my_addr)

    # Create new connection class and call the connect function to connect and apply the Three Way Handshake
    connection = Connection(serv_addr[0], serv_addr[1], sock)
    connection.connect()

    if connection.is_connected:
        print("Connection established\n")
    else:
        print("Failed to connect to the server\n")
        return None
    return sock, connection


# Sends a given query to the MySQL server and return the response
def send_query(query):
    # Send the query to the server
    connection.send(query.encode())

    response = connection.recv()

    # The response is a result set
    result_set = response.strip()
    return result_set


# Send a given query, and convert the result into a readable dictionary
def send_query_and_get_result_dict(query):
    result = send_query(query)
    if isinstance(result, str):
        data = json.loads(result)
    else:
        print("Failed to execute the query.\n Error code: ", result[1], " \nError: ", result[2])
        return None
    return data


# Assign to the DHCP server and receive an IP address
dhcp_utils.assign_to_dhcp_server()

# Create a DNS resolver object
resolver = dns.resolver.Resolver()

# Send the dns query to allocate the IP address of the Database server
answer = resolver.resolve('db.finalProject.com', 'A')

# Extract the Database IP from the DNS response
db_ip = answer[0].address

# Get the client ip
my_ip = get_ip()

# Establish connection with the server
sock, connection = establish_connection((db_ip, 30006), (my_ip, 20452))

# The while loop is a user interface to choose which query to send to the server, when 'z' is inserted by the client,
# the loop will break.
while True:
    choice = input("Please enter the query: \n1 - Insert \n2 - Remove\n3 - Get by ID \n4 - Get by age\n5 - Get all\n"
                   "6 - Update \n7 - Get avarge age \n8 - Get number of clients \n9 - Get most common city \n10 - Delete all clients \nz - exit ")

    if choice == '1':
        client = clients_factory.scan_client()
        query = mysql_adapter.insert(client)
        result = send_query_and_get_result_dict(query)
        print("Client inserted successfully\n")

    elif choice == '2':
        cid = input("Please enter the client's ID number you wish to remove:\n")
        query = mysql_adapter.remove_by_cid(cid)
        result = send_query_and_get_result_dict(query)
        print("Client removed successfully\n")

    elif choice == '3':
        cid = int(input("Please enter the client's ID number you wish to find:\n"))
        query = mysql_adapter.get_client_by_cid(cid)
        result = send_query_and_get_result_dict(query)
        if 'result' in result and result['result'] is None:
            print("Got no results")
        else:
            client = clients_factory.struct_client_from_data(result)
            print(client)

    elif choice == '4':
        age = int(input("Please enter the age of the clients to pull:\n"))
        query = mysql_adapter.get_clients_by_age(age)
        result = send_query_and_get_result_dict(query)
        if 'result' in result and result['result'] is None:
            print("Got no results")
        else:
            if isinstance(result, dict):
                client = clients_factory.struct_client_from_data(result)
                print(client)
            else:
                clients_list = list()
                for client_data in result:
                    clients_list.append(clients_factory.struct_client_from_data(client_data))
                for client in clients_list:
                    print(client)

    elif choice == '5':
        query = mysql_adapter.get_all()
        result = send_query_and_get_result_dict(query)
        print(len(result))
        if 'result' in result and result['result'] is None:
            print("There are no clients in the table.")
        else:
            if isinstance(result, dict):
                client = clients_factory.struct_client_from_data(result)
                print(client)
            else:
                clients_list = list()
                for client_data in result:
                    clients_list.append(clients_factory.struct_client_from_data(client_data))
                for client in clients_list:
                    print(client)

    elif choice == '6':
        id = int(input("Please enter the ID of the client to update: \n"))
        query = mysql_adapter.get_client_by_cid(id)
        result = send_query_and_get_result_dict(query)
        client = clients_factory.struct_client_from_data(result)
        clients_factory.update_client(client)
        query = mysql_adapter.update(client)
        result = send_query_and_get_result_dict(query)
        print("Client updated successfully\n")

    elif choice == '7':
        query = mysql_adapter.get_average_age()
        result = send_query_and_get_result_dict(query)
        if result['avg_age'] is None:
            print("Got no results")
        else:
            avg_age = float(result['avg_age'])
            print(avg_age)

    elif choice == '8':
        query = mysql_adapter.get_number_of_clients()
        result = send_query_and_get_result_dict(query)
        if 'result' in result and result['result'] is None:
            print("Got no results")
        else:
            number_of_clients = int(result['COUNT(*)'])
            print(number_of_clients)

    elif choice == '9':
        query = mysql_adapter.get_most_common_city()
        result = send_query_and_get_result_dict(query)
        if 'result' in result and result['result'] is None:
            print("Got no results")
        else:
            most_common_city = result['City']
            print(most_common_city)

    elif choice == '10':
        query = mysql_adapter.delete_all_clients()
        result = send_query_and_get_result_dict(query)
        print("All clients was deleted successfully\n")

    elif choice == 'z':
        break

    else:
        print("Unsupported option, please try again\n")




