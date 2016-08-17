import struct, socket, random

BUFSIZE = 1024

get_tid = lambda: random.randint(0, 255)

def connect(host, port, timeout):
    """UDP tracker protocol - connect request

    Offset  Size            Name             Value
    0       64-bit integer  connection_id    0x41727101980
    8       32-bit integer  action           0  // connect
    12      32-bit integer  trasaction_id
    16

    UDP tracker protocol - connect response

    Offset  Size            Name             Value
    0       32-bit integer  action           0 // connect
    4       32-bit integer  trasaction_id
    8       64-bit integer  connection_id
    16
    """
    conn_id = 0x41727101980
    action = 0
    tid = get_tid()
    pkt = struct.pack('>Q2I', conn_id, action, tid)
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.settimeout(timeout)
    assert isinstance(host, str)
    assert isinstance(port, int)
    addr = (host, port)
    nbytes = s.sendto(pkt, addr)
    assert nbytes == (64 + 32 + 32) / 8
    res, _ = s.recvfrom(BUFSIZE)
    s.close()
    assert len(res) >= 16, 'packet size should be at least 16 bytes'
    action, r_tid, conn_id = struct.unpack('>2IQ', res)
    assert r_tid == tid, 'transaction id not equal to "conn"'
    assert action == 0, 'action should be "0" (connect)'
    return conn_id

def test():
    host, port, timeout = 'zer0day.ch', 1337, 8
    conn_id = connect(host, port, timeout)
    print 'connection ID of "udp://zer0day.ch:1337/" -> {}'.format(conn_id)

if __name__ == '__main__':
    test()
