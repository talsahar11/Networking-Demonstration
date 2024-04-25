import random
import socket
import struct
from system_utils import get_details, change_ip, set_dns_server

"""---------------------------------------------------------------------------
  |                                                                           |
  |               The client methods to use dhcp protocol,                    |
  |              to create different dhcp requests, and to                    |
  |                send the requests to the dhcp server.                      |
  |                                                                           |
  |___________________________________________________________________________|"""

# Create a dhcp-discover message - returns a dhcp-discover packet
def create_discover_msg():
    details = get_details()
    op = 1
    htype = 1
    h_len = 6
    hops = 0
    xid = random.getrandbits(32)
    sec = 0
    flags = 0x8000
    ciaddr = '0.0.0.0'
    yiaddr = '0.0.0.0'
    siaddr = '0.0.0.0'
    giaddr = '0.0.0.0'
    mac_addr = bytes.fromhex(details[1].replace(':', ''))
    packet = struct.pack("!B", op)              # Operation
    packet += struct.pack("!B", htype)          # Hardware type
    packet += struct.pack("!B", h_len)          # Mac address length
    packet += struct.pack("!B", hops)           # Hops made
    packet += struct.pack("!I", xid)            # Transaction ID
    packet += struct.pack("!H", sec)            # Seconds from the start of the dhcp connection
    packet += struct.pack("!H", flags)          # Flags - broadcast
    packet += struct.pack("!4s", socket.inet_aton(ciaddr))  # Current address
    packet += struct.pack("!4s", socket.inet_aton(yiaddr))  # Suggested address
    packet += struct.pack("!4s", socket.inet_aton(siaddr))  # Server address
    packet += struct.pack("!4s", socket.inet_aton(giaddr))  # Gateway address
    packet += struct.pack("!6s10x", mac_addr)   # Mac address
    packet += struct.pack("!64x")               # Name field
    packet += struct.pack("!128x")              # File field

    packet += struct.pack("!B", 99)             # DHCP
    packet += struct.pack("!B", 130)            # MESSAGE
    packet += struct.pack("!B", 83)
    packet += struct.pack("!B", 99)

    packet += struct.pack("!B", 0x35)           # DHCP Message type
    packet += struct.pack("!B", 0x01)           # Length
    packet += struct.pack("!B", 0x01)           # 1 - Discover
    packet += struct.pack("!B", 0xff)           # End flag
    return packet


# Create a dhcp-request message by a provided dhcp-offer from the server, returns a dhcp-request packet
def create_request_message(data):
    byte_list = [byte for byte in bytearray(data)]
    offered = socket.inet_ntoa(bytes(byte_list[16:20]))
    op = 1
    htype = 1
    h_len = 6
    hops = 0
    hex_xid = byte_list[4:8]
    hex_xid_str = "".join([format(x, "02x") for x in hex_xid])
    xid = int(hex_xid_str, 16)
    sec = 0
    flags = 0x8000
    ciaddr = '0.0.0.0'
    yiaddr = '0.0.0.0'
    siaddr = '0.0.0.0'
    giaddr = '0.0.0.0'
    mac_len = byte_list[2]
    mac_address = byte_list[28:28 + mac_len]
    mac_str = ":".join([format(x, "02x") for x in mac_address])
    mac_addr = bytes.fromhex(mac_str.replace(':', ''))
    dhcp_type = byte_list[242]
    packet = struct.pack("!B", op)  # Operation
    packet += struct.pack("!B", htype)  # Hardware type
    packet += struct.pack("!B", h_len)  # Mac address length
    packet += struct.pack("!B", hops)  # Hops made
    packet += struct.pack("!I", xid)  # Transaction ID
    packet += struct.pack("!H", sec)  # Seconds from the start of the dhcp connection
    packet += struct.pack("!H", flags)  # Flags - broadcast
    packet += struct.pack("!4s", socket.inet_aton(ciaddr))  # Current address
    packet += struct.pack("!4s", socket.inet_aton(yiaddr))  # Suggested address
    packet += struct.pack("!4s", socket.inet_aton(siaddr))  # Server address
    packet += struct.pack("!4s", socket.inet_aton(giaddr))  # Gateway address
    packet += struct.pack("!6s10x", mac_addr)  # Mac address
    packet += struct.pack('64x')  # Name field
    packet += struct.pack("!128x")  # File field

    packet += struct.pack("!B", 99)  # DHCP
    packet += struct.pack("!B", 130)  # MESSAGE
    packet += struct.pack("!B", 83)
    packet += struct.pack("!B", 99)

    packet += struct.pack("!B", 0x35)  # DHCP Message type
    packet += struct.pack("!B", 0x01)  # Length - 1
    packet += struct.pack("!B", 0x03)  # 3 - Request
    packet += struct.pack("!B", 0x32)  # IP request
    packet += struct.pack("!B", 0x04)  # Length - 4
    packet += struct.pack("!4s", socket.inet_aton(offered))  # Requested IP

    packet += struct.pack("!B", 0xff)  # End flag
    dhcp_ip = socket.inet_ntoa(bytes(byte_list[245:249]))
    return packet, dhcp_ip, offered


# Sends a dhcp-discover message on broadcast, returns the response
def send_discover_message(message):
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        sock.bind(('0.0.0.0', 68))
        broadcast_address = ('<broadcast>', 67)
        sock.sendto(message, broadcast_address)
        while True:
            data, addr = sock.recvfrom(1024)
            bootp_op = data[0]
            dhcp_type = data[242]
            if bootp_op == 2 and dhcp_type == 2:
                return data


# Sends a dhcp-request message on broadcast, returns the response
def send_request_message(message, dhcp_ip):
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.setsockopt(socket.SOL_SOCKET, socket.SOCK_DGRAM, 1)
        sock.bind(('0.0.0.0', 68))
        address = (dhcp_ip, 67)
        sock.sendto(message, address)
        while(True):
            data, addr = sock.recvfrom(1024)
            boot_op = data[0]
            dhcp_type = data[242]
            if boot_op == 2 and dhcp_type == 5:
                return data


# Parse the options section of a dhcp requests and responses
def get_options(message):
    byte_list = [byte for byte in bytearray(message)]  # Parse the data into a bytes list
    options_section = byte_list[240:]
    i = 0
    option_type = options_section[i]
    options = dict()
    while option_type != 0xFF:
        i += 1
        option_len = options_section[i]
        i += 1
        data = options_section[i:i + option_len]
        options[option_type] = data
        i += option_len
        option_type = options_section[i]
    parsed_options = dict()
    for option in options.keys():
        if option == 53:
            parsed_op = 'type'
            if options[option][0] == 1:
                parsed_options[parsed_op] = 'discover'
            elif options[option][0] == 2:
                parsed_options[parsed_op] = 'offer'
            elif options[option][0] == 3:
                parsed_options[parsed_op] = 'request'
            elif options[option][0] == 5:
                parsed_options[parsed_op] = 'ack'
        if option == 6:
            parsed_op = 'dns'
            parsed_options[parsed_op] = socket.inet_ntoa(bytes(options[option]))
    return parsed_options


# Assign to the dhcp server
def assign_to_dhcp_server():
    dhcp_ops = dict()
    for i in range(4):
        if i == 3:
            print("Failed to assign to the DHCP Server.")
            break
        discover = create_discover_msg()  # Create the Discover message
        offer_packet = send_discover_message(discover)  # Send the Discover message
        dhcp_ops = get_options(offer_packet)
        if dhcp_ops['type'] == 'offer':
            request, dhcp_ip, offered_ip = create_request_message(offer_packet)  # Create the Request message
            ack = send_request_message(request, dhcp_ip)  # Send the Request message
            dhcp_ops = get_options(ack)
            if dhcp_ops['type'] == 'ack':
                change_ip(offered_ip)  # Change the ip to the offered one
                set_dns_server(dhcp_ops['dns'])  # Set the dns server in use to ours
                break


"""---------------------------------------------------------------------------
  |                                                                           |
  |             The server methods to implement dhcp protocol,                |
  |              to create different dhcp responses, and to                   |
  |               send the responses back to the client.                      |
  |                                                                           |
  |___________________________________________________________________________|"""


# Create a dhcp-offer message - returns the offer packet
def create_offer(mac_address, xid, offer, dhcp_ip, gateway_ip):
    op = 2
    htype = 1
    h_len = 6
    hops = 0
    xid = xid
    sec = 0
    flags = 0x8000
    ciaddr = '0.0.0.0'
    yiaddr = offer
    siaddr = dhcp_ip
    giaddr = gateway_ip
    mac_addr = bytes.fromhex(mac_address.replace(':', ''))

    name = bytes('server.example.com', 'ascii')
    name_len = len(name)
    packet = struct.pack("!B", op)  # Operation
    packet += struct.pack("!B", htype)  # Hardware type
    packet += struct.pack("!B", h_len)  # Mac address length
    packet += struct.pack("!B", hops)  # Hops made
    packet += struct.pack("!I", xid)  # Transaction ID
    packet += struct.pack("!H", sec)  # Seconds from the start of the dhcp connection
    packet += struct.pack("!H", flags)  # Flags - broadcast
    packet += struct.pack("!4s", socket.inet_aton(ciaddr))  # Current address
    packet += struct.pack("!4s", socket.inet_aton(yiaddr))  # Suggested address
    packet += struct.pack("!4s", socket.inet_aton(siaddr))  # Server address
    packet += struct.pack("!4s", socket.inet_aton(giaddr))  # Gateway address
    packet += struct.pack("!6s10x", mac_addr)  # Mac address
    packet += struct.pack(f'!{name_len}s{64-name_len}x', name)  # Name field
    packet += struct.pack("!128x")  # File field

    packet += struct.pack("!B", 99)  # DHCP
    packet += struct.pack("!B", 130)  # MESSAGE
    packet += struct.pack("!B", 83)
    packet += struct.pack("!B", 99)

    packet += struct.pack("!B", 0x35)  # DHCP Message type
    packet += struct.pack("!B", 0x01)  # Length - 1
    packet += struct.pack("!B", 0x02)  # 2 - Offer
    packet += struct.pack("!B", 0x36)  # DHCP Server identifier
    packet += struct.pack("!B", 0x04)  # Length - 4
    packet += struct.pack("!4s", socket.inet_aton(siaddr))  # DHCP Server address
    packet += struct.pack("!B", 0xff)  # End flag
    return packet


# Create a dhcp-ack message - returns the ack packet and a client name
def create_ack(mac_address, xid, offer, dhcp_ip, gateway_ip, dns_ip):
    op = 2
    htype = 1
    h_len = 6
    hops = 0
    xid = xid
    sec = 0
    flags = 0x8000
    ciaddr = '0.0.0.0'
    yiaddr = offer
    siaddr = dhcp_ip
    giaddr = gateway_ip
    mac_addr = bytes.fromhex(mac_address.replace(':', ''))

    name = bytes('server.example.com', 'ascii')
    name_len = len(name)
    packet = struct.pack("!B", op)  # Operation
    packet += struct.pack("!B", htype)  # Hardware type
    packet += struct.pack("!B", h_len)  # Mac address length
    packet += struct.pack("!B", hops)  # Hops made
    packet += struct.pack("!I", xid)  # Transaction ID
    packet += struct.pack("!H", sec)  # Seconds from the start of the dhcp connection
    packet += struct.pack("!H", flags)  # Flags - broadcast
    packet += struct.pack("!4s", socket.inet_aton(ciaddr))  # Current address
    packet += struct.pack("!4s", socket.inet_aton(yiaddr))  # Suggested address
    packet += struct.pack("!4s", socket.inet_aton(siaddr))  # Server address
    packet += struct.pack("!4s", socket.inet_aton(giaddr))  # Gateway address
    packet += struct.pack("!6s10x", mac_addr)  # Mac address
    packet += struct.pack(f'!{name_len}s{64 - name_len}x', name)  # Name field
    packet += struct.pack("!128x")  # File field

    packet += struct.pack("!B", 99)  # DHCP
    packet += struct.pack("!B", 130)  # MESSAGE
    packet += struct.pack("!B", 83)
    packet += struct.pack("!B", 99)

    packet += struct.pack("!B", 0x35)  # DHCP Message type
    packet += struct.pack("!B", 0x01)  # Length - 1
    packet += struct.pack("!B", 0x05)  # Ack - 5

    packet += struct.pack("!B", 6)     # DNS Option
    packet += struct.pack("!B", 4)     # DNS Length
    packet += struct.pack("!4s", socket.inet_aton(dns_ip))
    packet += struct.pack("!B", 0xff)  # End flag
    return packet