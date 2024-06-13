# Networking Demonstration Project

## Project Overview

This project demonstrates a networking setup using Docker containers to simulate a network environment. The setup includes:

A DHCP server container
A client container
A server container with a MySQL database
The system supports both TCP communication and a custom Reliable UDP (RUDP) protocol, which adds reliability features to the standard UDP protocol.

## Features

**DHCP Server**: Assigns IP addresses to client containers.
**Client**: Connects to the server and demonstrates communication.
**Server**: Hosts a MySQL database and handles client requests.
**TCP Communication**: Standard reliable communication using TCP.
**RUDP Protocol**: Custom protocol built on top of UDP to ensure reliability.
## Project Structure

```
Networking-Demonstration-main/
│
├── Dockerfile
├── docker-compose.yml
├── volumes/
│ ├── my.cnf
│ ├── rudp_part/
│ │ ├── client.py
│ │ ├── clients_factory.py
│ │ ├── connection.py
│ │ ├── dhcp_serv.py
│ │ ├── dhcp_utils.py
│ │ └── ...
│ ├── tcp_part/
│ │ ├── client.py
│ │ ├── clients_factory.py
│ │ ├── dhcp_serv.py
│ │ ├── dhcp_utils.py
│ │ ├── server.py
│ │ └── ...
│ └── ...
├── הקלטות/ # Network captures in .pcapng format
│ ├── client_rudp.pcapng
│ ├── client_tcp.pcapng
│ ├── database_server_rudp.pcapng
│ ├── database_server_tcp.pcapng
│ └── ...
└── README.md # You're reading this file
```

## Setup Instructions

### Prerequisites

Docker
Docker Compose
### Steps

**Clone the Repository**

```sh
git clone <repository-url>
cd Networking-Demonstration-main
```

**Build and Start the Containers**

Use Docker Compose to build and start the containers:

```sh
docker-compose up --build
```

This command will set up the DHCP server, client, and MySQL server containers.

**Verify the Setup**

The DHCP server should be assigning IPs to the client.
The client should be able to communicate with the server via TCP and RUDP.
## Usage

### TCP Communication

The TCP communication can be tested by running the relevant scripts located in the volumes/tcp_part directory.

### RUDP Communication

For RUDP communication, use the scripts in the volumes/rudp_part directory. This custom protocol ensures reliability over UDP.

### Capturing Network Traffic

Network traffic captures are stored in the הקלטות directory. These .pcapng files can be analyzed using Wireshark or similar tools to inspect the communication between containers.

## Components

### DHCP Server

Handles IP address assignment to client containers. Configuration and scripts are located in the volumes/rudp_part and volumes/tcp_part directories.

### Client

Initiates communication with the server. Scripts for both TCP and RUDP communication are provided.

### Server

Hosts a MySQL database and responds to client requests. Configuration files are in the volumes directory.

## Custom RUDP Protocol

The RUDP protocol implemented in this project adds reliability to UDP communication. It ensures that packets are delivered in order and retransmits lost packets.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any improvements or bug fixes.

## License

This project is licensed under the MIT License. See the LICENSE file for details.
