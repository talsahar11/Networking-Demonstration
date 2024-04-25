import re
import subprocess
import netifaces


# Get the current user ip address
def get_ip():
    output = subprocess.check_output(['ifconfig']).decode('utf-8')
    # Search for the IP address in the output using a regular expression
    match = re.search(r'inet\s+(\d+\.\d+\.\d+\.\d+)', output)
    # Extract the IP address from the match object
    ip_address = match.group(1)
    return ip_address


# Get the details of the net interface, the mac address and the hardware type length for to be used in the dhcp message
def get_details():
    interfaces = netifaces.interfaces()
    for interface in interfaces:
        if interface != 'lo':
            address = netifaces.ifaddresses(interface)
            if netifaces.AF_LINK in address:
                link_address = address[netifaces.AF_LINK]
                if len(link_address) > 0:
                    h_type = link_address[0].get('addrtype')
                    h_length = link_address[0].get('addr').count(':')
                    mac_address = link_address[0].get('addr')
                    return h_length, mac_address


# After receiving the ack from the dhcp server on an agreed ip address, the client's ip will be changed to
# the offered ip address
def change_ip(offer):
    iface = 'eth0'
    new_ip = offer
    gateway = '10.9.0.1'
    subprocess.run(['ifconfig', iface, new_ip, 'netmask', '255.255.255.0'])
    subprocess.run(['ip', 'route', 'add', 'default', 'via', gateway, 'dev', iface])
    result = subprocess.run(['ifconfig', iface], capture_output=True, text=True)
    output = result.stdout
    if new_ip in output:
        print(f'IP address changed to {new_ip}')
    else:
        print('IP address change failed')


# Change the current dns server in use to another dns server by the ip supplied as an argument
def set_dns_server(dns_ip):
    with open('/etc/resolv.conf', 'w') as f:
        f.write(f'search lan\nnameserver {dns_ip}\noptions edns0 trust-ad ndots:0')  # Replace with your DNS server IP


