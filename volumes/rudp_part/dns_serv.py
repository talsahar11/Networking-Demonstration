import threading
import socket
import dns.resolver
import dns.message
import dhcp_utils


# Handle a given DNS query, in case the answer is within the DNS dictionary, answer directly,
# otherwise send the query to the next level DNS server
def handle_query(data, addr, sock):
    query = dns.message.from_wire(data)
    domain = query.question[0].name.to_text().strip('.')

    # If the wanted domain is already in the DNS dict return the answer.
    if domain in domain_address_dict.keys():

        # Create the DNS response
        address = domain_address_dict[domain][0]
        qname = dns.name.from_text(domain)
        qtype = dns.rdatatype.A
        qclass = dns.rdataclass.IN
        rdata = dns.rdata.from_text(dns.rdataclass.IN, dns.rdatatype.A, address)
        rrset = dns.rrset.RRset(qname, qclass, qtype)
        rrset.add(rdata)
        response = dns.message.make_response(query, recursion_available=True)
        response.answer.append(rrset)

        # Send the response back to the client
        sock.sendto(response.to_wire(), addr)

    # If the wanted domain is not in the DNS dict, pass it to the next level DNS server
    else:
        # Create a DNS resolver object
        resolver = dns.resolver.Resolver()

        # Send a DNS query for the A record of example.com
        answer = resolver.resolve(domain, 'A')
        response = answer.response.to_wire()
        sock.sendto(response, addr)


# Wait for incoming DNS queries
def listen_for_queries():
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.bind(('0.0.0.0', 53))
        while True:
            data, addr = sock.recvfrom(512)
            handle_query(data, addr, sock)


# Extract and insert the new domain and IP into the DNS dict
def handle_update(update):
    pairs = update.split(',')
    hostname = ''
    address = ''
    for pair in pairs:
        key, value = pair.split(':')
        key = key.strip()
        value = value.strip()

        if key == 'hostname':
            hostname = value
        if key == 'address':
            address = value
        domain_address_dict[hostname] = (address, 500000)


# Wait for incoming DNS updates from the DHCP server
def listen_for_updates():
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.bind(('0.0.0.0', 9999))
        while True:
            update, addr = sock.recvfrom(512)
            handle_update(update.decode('ascii'))





"""------------------------ Main program -------------------------"""

# A dictionary maps a domain to a address
domain_address_dict = dict()

# Listen for DNS requests
print("Listening for DNS queries...")

# Define the DNS server address and port
dns_server_address = '0.0.0.0'
dns_server_port = 53

dhcp_utils.assign_to_dhcp_server()
updates_thread = threading.Thread(target=listen_for_updates)
queries_thread = threading.Thread(target=listen_for_queries)
updates_thread.start()
queries_thread.start()
