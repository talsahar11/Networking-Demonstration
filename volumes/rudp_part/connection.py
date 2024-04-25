import socket
import threading
import time

from protocol_handler import *


"""                          RUDP Format
     Syn - 1 bit, Ack - 1 bit, Fin - 1 bit, Reserved - 5 bits
     Ack value - 4 Bytes
     Sequence number - 4 Bytes
     Checksum - 4 Bytes                                        """

MAX_PACKET_SIZE = 8192


# The class Connection maintain all the relevant processes used during a connection between two entities.
class Connection:

    # Constructor
    def __init__(self, address, port, sock: socket.socket, is_server=False):
        self.endpoint_address = (address, port)
        self.is_connected = False
        self.ack_val = 1
        self.seq_num = 1
        self.sock = sock
        self.incoming_queue = list()
        self.outgoing_queue = list()
        if not is_server:
            self.listening_thread = threading.Thread(target=self.listen, args=())
            self.listening_thread.start()
        self.sending_thread = threading.Thread(target=self.send_from_out_queue, args=())
        self.sending_thread.start()
        self.congestion_window_size = 8
        self.ss_thresh = 50
        self.current_datapack = list()
        self.whole_messages = list()
        self.message_handler = MessagesManager(self)

    # Used to notify to the connection instance that connection established, and start the message handler thread
    def set_connected(self, is_connected):
        self.is_connected = is_connected
        self.message_handler.start()

    # Connect to the dest address supplied in the constructor, this method will be used by the client.
    def connect(self):
        if handshake(self):
            self.set_connected(True)
        else:
            print("Fail to create a connection")

    # Listen for incoming data, this method is a thread target, the thread will listen for incoming data, and when
    # receiving data, will put it into a pre-made queue, the data will be handled by other threads.
    def listen(self):
        sock = self.sock
        endpoint_address = self.endpoint_address
        queue = self.incoming_queue
        while True:
            data, address = sock.recvfrom(MAX_PACKET_SIZE + HEADER_SIZE)
            if address == endpoint_address:
                queue.append(data)

    # This method is a target of a thread, for sending a complete wrapped frame to the end point, the frame will be
    # pushed into the outgoing_queue, and then the sending_thread, will send it to the end_point.
    def send_from_out_queue(self):
        sock = self.sock
        endpoint_address = self.endpoint_address
        queue = self.outgoing_queue
        while True:
            if len(queue) > 0:
                packet = queue.pop(0)
                sock.sendto(packet, endpoint_address)

    # Send ack to the endpoint, the ack value is the current connection ack.
    def send_ack(self):
        ack_packet = create_rudp_header(ack=True, ack_value=self.ack_val, seq_number=self.seq_num)
        self.outgoing_queue.append(ack_packet)

    # Submit a received fragment into a list of data packets, the data will be in order, at the time the whole message
    # will be received, the fragments will be connected into one whole message.
    def reassemble_data(self, packet):
        self.current_datapack.append(packet)

    # When a full message received, this method will be called, and will reconnect all the fragments in the current
    # datapack list into one whole message. After that, the message will be submitted to the whole messages list so
    # the client will be able to receive it.
    def pack_and_submit(self):
        whole_data = ''
        for fragment in self.current_datapack:
            whole_data += fragment.decode()
        self.whole_messages.append(whole_data)
        self.current_datapack = list()

    # This method will be called by the user when trying to send a message, the message will be sent to the
    # message_handler, that will cut it into fragments if needed, and handle the actual sending of those fragments.
    def send(self, message):
        self.message_handler.send_message(message)

    # Reduce the congestion control window size, in case of 3 duplicate acks received.
    def reduce_c_window_size(self):
        self.congestion_window_size = 8

    # Increase the congestion control window size, implements the AIMD Principle
    def update_c_window(self):
        if self.congestion_window_size > self.ss_thresh:
            self.congestion_window_size += 1
        else:
            self.congestion_window_size *= 2

    # This method will be called by the user when trying to receive a message, the user program will be blocked until
    # a full message has arrived.
    def recv(self):
        while len(self.whole_messages) == 0:
            pass
        return self.whole_messages.pop()


# Create a connection entity and return it
def create_connection(address, port, sock, is_server=False):
    connection = Connection(address, port, sock, is_server)
    return connection


# The three-way handshake process, will often be called by the client as part of establishing a connection to the server
def handshake(connection: Connection):
    syn_message = create_syn_message()
    is_synack_received = False
    trys = 0
    while not is_synack_received:
        connection.outgoing_queue.append(syn_message)
        time.sleep(1)
        trys += 1
        if len(connection.incoming_queue) > 0:
            message = connection.incoming_queue.pop(0)
            header = extract_header(message)
            if header[SYN] and header[ACK]:
                is_synack_received = True
        if trys == 5:
            print("Handshake was not completed, synack was not received")
            return False
    ack_message = create_ack_message()
    connection.outgoing_queue.append(ack_message)
    return True


# Check if a packet is the last fragment of the current message.
def is_data_closed(packet):
    packet_size = len(packet)
    if packet[packet_size - 1] == 0:
        return True
    return False


# This class will handle the receiving and sending of messages, and also will be able to recognize a congestion on the
# network, and handle it.
class MessagesManager:
    def __init__(self, connection: Connection):
        self.receiving_thread = threading.Thread(target=self.handle_receive)
        self.thread_pool = dict()
        self.connection = connection
        self.last_repeated_ack = -1
        self.num_of_repeats = 0
        self.full_window_counter = [0, time.time()]
        self.lock = threading.Lock()
        self.keep_handling = True
        self.fragments = list()
        self.is_sending = False

    # Start the receiving thread, responsible for receiving messages, classify them by the protocol guidelines, and
    # handle the data received.
    def start(self):
        self.receiving_thread.start()

    # The method called by the connection when the client sends a message.
    # The message will be fragmented into parts according to its size and the MAX_PACKET_SIZE allowed and defined.
    # After the fragmentation, for each fragment a fragment_thread will be created.
    def send_message(self, message):
        while self.is_sending:
            pass

        print("Sending")
        self.is_sending = True
        self.fragments = self.split_message(message)
        frag_threads_handler = threading.Thread(target=self.handle_threads)
        frag_threads_handler.start()

    # Handle the fragment threads, and keep the congestion controlled.
    def handle_threads(self):
        # Synchronized, when another message being trying to be sent, the other message_handler instance will be blocked
        # as long as the last message have not been sent properly.
        with self.lock:

            # While there are still fragment to send.
            while len(self.fragments) > 0:
                if self.keep_handling:
                    if len(self.thread_pool) < self.connection.congestion_window_size:
                        current_frag = self.fragments.pop(0)
                        frag_thread = FragmentThread(self.connection, current_frag)
                        self.thread_pool[current_frag.expected_ack] = frag_thread
                        self.thread_pool = sort_dict(self.thread_pool)
                        frag_thread.start()
                    else:
                        self.full_window_counter[0] = self.full_window_counter[0] + 1
                        self.check_if_timeout_required()

    # This method is a target of the receiving thread. It is responsible for getting the incoming data, and classify
    # it by the protocol guidelines.
    def handle_receive(self):
        while self.connection.is_connected:
            # If there are frames in the incoming queue
            if len(self.connection.incoming_queue) != 0:
                # Get the frame and the protocol attributes such as ack and cksum.
                packet = self.connection.incoming_queue.pop(0)
                header = extract_header(packet)
                body = extract_body(packet)
                ack = header[ACK_VAL]
                ck_sum = header[CKSUM]
                p_size = len(packet)

                # If the ack of the frame is an expected ack, update the fragments list, and stop all the
                # fragment_threads with an expected ack value lower that the received ack.
                if ack in self.thread_pool.keys():
                        self.connection.update_c_window()
                        if is_data_closed(self.thread_pool[ack].fragment.packet):
                            self.is_sending = False
                        for key in self.thread_pool.keys():
                            thread = self.thread_pool.pop(key)
                            thread.keep_on = False
                            if ack == key:
                                break

                # Check for a congestion in the network, if the ack is not an expected ack, save its value, and start
                # counting, if an ack received in sequence of 3 times, reduce the congestion control window size.
                elif len(self.thread_pool) > 0:
                    if ack < next(iter(self.thread_pool.keys())):
                        if self.last_repeated_ack == ack:
                            if self.num_of_repeats == 3:
                                self.connection.reduce_c_window_size()
                                self.num_of_repeats = 0
                            else:
                                self.num_of_repeats += 1
                        else:
                            self.last_repeated_ack = ack
                            self.num_of_repeats = 0
                # Check if the endpoint trying to close the connection
                if len(body) == 0:
                    if header[FIN]:
                        print("Finish")

                # If the frame contains data except of the header, check if the data is on sequence
                else:
                    seq_num = header[SEQ_NUM]

                    # If the incoming data is on sequence, send it to the datapack list, and if the data is a closing
                    # message, call pack and submit method so that the user will be able to receive the whole message.
                    if seq_num == self.connection.ack_val and checksum(body) == ck_sum:
                        self.connection.ack_val += p_size               # Update the connection ack value
                        if is_data_closed(packet):
                            b_size = len(body)
                            self.connection.reassemble_data(body[:b_size - 1])
                            self.connection.pack_and_submit()

                        else:
                            self.connection.reassemble_data(body)
                    # Send ack message on the data that been received
                    self.connection.send_ack()

    # Split a message into fragments, at max size of the defined MAX_PACKET_SIZE and add the correct rudp header,
    # contains the sequence number, ack value and checksum of the fragment.
    # Returns a list contains all the fragments in increasing order of sequence numbers
    def split_message(self, message):
        fragments = []
        for i in range(0, len(message), MAX_PACKET_SIZE):
            data = message[i:i + MAX_PACKET_SIZE]
            packet = create_packet(ack=True, ack_value=self.connection.ack_val,
                                   seq_number=self.connection.seq_num, checksum=checksum(data), data=data)
            if i + MAX_PACKET_SIZE >= len(message):
                packet += struct.pack("!1B", 0)
            fragment = Fragment(self.connection.seq_num, packet)
            self.connection.seq_num += fragment.frag_len
            fragments.append(fragment)
        return fragments

    # When the window size is full for a long time, the handling thread will pause for a short time amount to reduce
    # the congestion.
    def check_if_timeout_required(self):
        if self.full_window_counter[0] > 30 and time.time() - self.full_window_counter[1] < 3:
            time.sleep(2)
        elif time.time() - self.full_window_counter[1] > 3:
            self.full_window_counter[0] = 0
            self.full_window_counter[1] = time.time()


# The Fragment class describes a fragment of a whole message, and the properties of it, the sequence number, length,
# and the expected ack on the message.
class Fragment:
    def __init__(self, seq_num, packet):
        self.packet = packet
        self.seq_num = seq_num
        self.frag_len = len(packet)
        self.expected_ack = self.seq_num + self.frag_len


# Sorts a dictionary by increasing value of its keys.
def sort_dict(d):
    new_d = dict()
    for key in sorted(d):
        new_d[key] = d[key]
    return new_d


# The FragmentThread class is created for each fragment individually, it is responsible for sending the fragment every
# 0.5 second. the thread is keep running until the expected ack of that fragment has been received, and then it stops.
class FragmentThread:
    def __init__(self, connection: Connection, fragment):
        self.connection = connection
        self.fragment = fragment
        self.tries = 0
        self.keep_on = True
        self.thread = threading.Thread(target=self.send_fragment)

    def send_fragment(self):
        while self.keep_on:
            self.connection.outgoing_queue.append(self.fragment.packet)
            time.sleep(0.5)

    def start(self):
        self.thread.start()


# Deep copy a fragment_thread
def copy_frag_thread(frag_thread: FragmentThread):
    return FragmentThread(frag_thread.connection, frag_thread.fragment)