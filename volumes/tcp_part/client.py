import json
import socket
import struct

import dns
import clients_factory
import dhcp_utils
import mysql_adapter
from system_utils import get_ip


def send_query(query):
    # Establish a TCP connection to the MySQL server
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((my_ip, 20452))
    sock.connect((db_ip, 30006))

    # Send the query to the server
    sock.sendall(query.encode())

    # Receive the response from the server
    data = b''

    # Loop to receive the data in chunks
    while True:
        # Receive a chunk of data from the socket
        buffer = sock.recv(1024)

        # If no more data is received, break out of the loop
        if not buffer:
            break

        # Append the received data to the buffer
        data += buffer

    # Close the connection
    sock.close()
    # Parse the response
    if data.startswith(struct.pack('<B', 0xff)):
        # The response is an error
        error_code = struct.unpack('<H', data[1:3])[0]
        error_msg = data[3:].decode('utf-8')
        return error_code, error_msg
    else:
        # The response is a result set
        result_set = data.decode('utf-8').strip()
        return result_set


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
            clients_list = list()
            for client_data in result:
                clients_list.append(clients_factory.struct_client_from_data(client_data))
            for client in clients_list:
                print(client)
    elif choice == '5':
        query = mysql_adapter.get_all()
        result = send_query_and_get_result_dict(query)
        clients_list = list()
        print(len(result))
        if 'result' in result and result['result'] is None:
            print("There are no clients in the table.")
        else:
            if isinstance(result, dict):
                client = clients_factory.struct_client_from_data(result)
                print(client)
            else:
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
        pass
    else:
        print("Unsupported option, please try again\n")


