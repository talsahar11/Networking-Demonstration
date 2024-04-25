# Temporary image to install pip and net-tools
FROM ubuntu:20.04 AS builder

RUN apt-get update && \
    apt-get install -y net-tools && \
    apt-get install -y python3 && \
    apt-get install -y python3-pip && \
    apt-get install -y curl && \
    apt-get install -y libmnl0 && \
    apt-get install -y iproute2 && \
    apt-get install -y libbsd0 && \
    apt-get clean

# Download get-pip.py and install pip
RUN apt-get install -y python3-pip && \
    pip3 install pip==21.3.1 && \
    rm -rf /var/lib/apt/lists/*

# Final image based on mysql
FROM mysql:latest

# Copy over pip from the temporary image
COPY --from=builder /usr/local/bin/pip /usr/local/bin/pip

# Copy over net-tools from the temporary image
COPY --from=builder /sbin/ifconfig /sbin/ifconfig
COPY --from=builder /sbin/arp /sbin/arp
COPY --from=builder /sbin/route /sbin/route
COPY --from=builder /sbin/ip /sbin/ip
COPY --from=builder /usr/lib/x86_64-linux-gnu/libmnl.so.0 /usr/lib/x86_64-linux-gnu/libmnl.so.0
COPY --from=builder /usr/lib/x86_64-linux-gnu/libbsd.so.0 /usr/lib/x86_64-linux-gnu/libbsd.so.0

ENV LD_LIBRARY_PATH=/usr/lib/x86_64-linux-gnu
# Set the MYSQL_TCP_PORT environment variable
ENV MYSQL_TCP_PORT=30452

# Install any necessary Python packages
RUN pip install dnspython
RUN pip install netifaces
RUN pip install mysql-connector-python
# Start the MySQL server

CMD ["mysqld"]
