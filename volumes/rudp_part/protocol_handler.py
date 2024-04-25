import struct


SYN = 0
ACK = 1
FIN = 2
ACK_VAL = 3
SEQ_NUM = 4
CKSUM = 5
HEADER_SIZE = 13


def create_packet(ack=False, ack_value=0, seq_number=0, checksum=0, data=b''):
    header = create_rudp_header(ack=ack, ack_value=ack_value, seq_number=seq_number, checksum=checksum)
    return header + data


def create_rudp_header(syn=False, ack=False, fin=False, reserved=0, ack_value=0, seq_number=0, checksum=0):
    # Pack the flags bits into a single byte
    flags = (syn << 7) | (ack << 6) | (fin << 5) | reserved

    # Pack the ack value and sequence number as unsigned long integers (4 bytes each)
    ack_bytes = struct.pack("!L", ack_value)
    seq_bytes = struct.pack("!L", seq_number)
    checksum = struct.pack("!L", checksum)
    # Concatenate the flags byte, ack value bytes, and sequence number bytes
    header_bytes = bytes([flags]) + ack_bytes + seq_bytes + checksum
    return header_bytes


def decode_rudp_header(header_bytes):
    # Unpack the flags byte, ack value bytes, and sequence number bytes
    flags = header_bytes[0]
    ack_bytes = header_bytes[1:5]
    seq_bytes = header_bytes[5:9]
    checksum = header_bytes[9:13]
    header = dict()
    # Extract the flag bits from the flags byte
    header[SYN] = bool(flags & 0b10000000)
    header[ACK] = bool(flags & 0b01000000)
    header[FIN] = bool(flags & 0b00100000)
    reserved = flags & 0b00011111

    # Unpack the ack value and sequence number as unsigned long integers
    header[ACK_VAL] = struct.unpack("!L", ack_bytes)[0]
    header[SEQ_NUM] = struct.unpack("!L", seq_bytes)[0]
    header[CKSUM] = struct.unpack("!L", checksum)[0]
    return header


def extract_header(packet):
    return decode_rudp_header(packet[0:13])


def is_only_header(packet):
    if len(packet) == HEADER_SIZE:
        return True
    return False


def extract_body(packet):
    return packet[HEADER_SIZE:]


def create_syn_message():
    return create_rudp_header(syn=True, seq_number=0, ack_value=0)


def create_syn_ack_message():
    return create_rudp_header(syn=True, ack=True, seq_number=0, ack_value=1)


def create_ack_message():
    return create_rudp_header(ack=True, seq_number=1, ack_value=1)


def is_data_closed(packet):
    packet_size = len(packet)
    if packet[packet_size-1] == 0:
        return True
    return False


def checksum(data):
    # Convert input data to bytes if necessary
    # Calculate the sum of all bytes in the input data
    checksum = sum(data)
    return checksum