import socket
from dhcp_utils import create_offer, create_ack

# DHCP variables initiation
dhcp_ip = '10.9.0.127'
client_num = 0
subnet_mask = 0xffffffff
addr_dict = dict()
addr_queue = list()
gateway_ip = '10.9.0.1'
def_lease_time = 1000000

# DNS variables initiation
reservedAddresses = dict()
reservedAddresses['db'] = ('2a:5c:01:3b:1b:02', '10.9.0.126', 'db.finalProject.com', 'database')   # Database mac
reservedAddresses['dns'] = ('2a:5c:01:3b:15:02', '10.9.0.53', None, 'dns')    # DNS mac


# Initiate the addresses' dictionary - insert all the ip addresses available by the subnet mask
# and mark the predefined addresses (Gateway and the dhcp server ip addresses)
def init_addr_dict():
    global addr_dict
    for i in range(1,256):
        addr_dict[f'10.9.0.{i}'] = (False, 0)
    addr_dict[dhcp_ip] = (True, 0)
    addr_dict[gateway_ip] = (True, 0)
    addr_dict[reservedAddresses['dns'][1]] = (True, 0)
    addr_dict[reservedAddresses['db'][1]] = (True, 0)


# Initiate the addresses queue, for an incoming dhcp-discover message, the first element
# of the queue will be offered to the client
def init_addr_queue():
    global addr_queue
    for i in addr_dict.keys():
        if not addr_dict[i][0]:
            addr_queue.append(i)


# Create a dns update message that will update the dns server on a new address assignment
def create_dns_update(hostname, addr):
    message = f'hostname : {hostname} , address : {addr}'
    packet = bytes(message, 'ascii')
    return packet


# Update the dns server on a new address assignment
def update_dns(hostname, addr):
    packet = create_dns_update(hostname, addr)
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        dns_addr = (reservedAddresses['dns'][1], 9999)
        sock.bind(('0.0.0.0', 9999))
        sent = sock.sendto(packet, dns_addr)
        print("Bytes sent: ", sent)

# Get the first element in the addresses queue
def draw_offer():
    return addr_queue[0]


# If the client has requested an address and the server accepts it, pop the first element from the
# addresses queue and update the lease-time and that the address is in use in the addresses dictionary
def verify_offer(offer):
    addr_dict[offer] = (True, def_lease_time)
    addr_queue.pop(0)


# The main loop of the dhcp server, wait for incoming requests and handling them when receiving
def listen_for_requests():
    hostname = socket.gethostname()
    ip = socket.gethostbyname(hostname)

    # Create a socket on a broadcast and port 67
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.bind(('0.0.0.0', 67))
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        broadcast_address = ('<broadcast>', 68)

        # Main loop
        while True:
            data, addr = sock.recvfrom(1024)                                # Receive data from the client
            byte_list = [byte for byte in bytearray(data)]                  # Parse the data into a bytes list
            mac_len = byte_list[2]                                          # Get the mac address length from the data
            mac_address = byte_list[28:28+mac_len]                          # Get the mac address from the data
            mac_str = ":".join([format(x, "02x") for x in mac_address])     # create a mac address string
            dhcp_type = byte_list[242]                                      # Get the dhcp message type
            hex_xid = byte_list[4:8]                                        # Get the transaction ID from the data
            hex_xid_str = "".join([format(x, "02x") for x in hex_xid])      # create a transaction ID string
            xid = int(hex_xid_str, 16)                                      # convert the transaction ID into integer

            # if the message is a dhcp-discover message
            if dhcp_type == 1:
                for value in reservedAddresses.values():
                    if mac_str in value[0]:
                        offer = value[1]
                        if value[3] == 'database':
                            update_dns(value[2], value[1])
                            print("Shit", offer, ", ", value)
                        print(f"Found matched mac address: {value[1]}")
                        break
                    else:
                        offer = draw_offer()
                print(f'Offer: {offer}')
                response = create_offer(mac_str, xid, offer, dhcp_ip, gateway_ip)   # Create the offer message
                sock.sendto(response, broadcast_address)                    # Send the offer message

            # if the message is a dhcp-request message
            if dhcp_type == 3:
                verify_offer(offer)                                         # Mark the offer as in use, and pop it out
                response = create_ack(mac_str, xid, offer, dhcp_ip, gateway_ip, reservedAddresses['dns'][1])   # Create the ack message
                global client_num
                sock.sendto(response, broadcast_address)                    # Send the ack message


# Main program
init_addr_dict()
init_addr_queue()
listen_for_requests()

