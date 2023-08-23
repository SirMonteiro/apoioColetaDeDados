import socket
from struct import unpack
from datetime import datetime


def requestTimefromNtp(addr="0.br.pool.ntp.org"):
    # https://stackoverflow.com/questions/36500197/how-to-get-time-from-an-ntp-server
    REF_TIME_1970 = 2208988800  # Reference time
    client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # data = b"\x1b" + 47 * b"\0"
    data = bytearray(48)
    data[0] = 0x1B
    client.sendto(data, (addr, 123))
    data = client.recvfrom(48)
    print(data)
    if data:
        t = unpack("!12I", data[0])[10] - REF_TIME_1970
        return t
    return -1


def isoDateTime(t):
    # https://www.geeksforgeeks.org/isoformat-method-of-datetime-class-in-python/
    dt = datetime.fromtimestamp(t)
    return dt.isoformat()
