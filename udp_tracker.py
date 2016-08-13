import struct, socket
from utils import str_to_num

BUFSIZE = 1024

def connect(addr):
    """UDP tracker protocol - connect request

    Offset  Size            Name             Value
    0       64-bit integer  connection_id    0x41727101980
    8       32-bit integer  action           0  // connect
    12      32-bit integer  trasaction_id
    16
    """
    conn_id = 0x41727101980
    action = 0
    tid = str_to_num('conn')
    pkt = struct.pack('>Q2I', conn_id, action, tid)
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    nbytes = s.sendto(pkt, addr)
    assert nbytes == (64 + 32 + 32) / 8
    res, _ = s.recvfrom(BUFSIZE)
    s.close()
    return res

def post_connect(res):
    """UDP tracker protocol - connect response

    Offset  Size            Name             Value
    0       32-bit integer  action           0 // connect
    4       32-bit integer  trasaction_id
    8       64-bit integer  connection_id
    16
    """
    assert len(res) >= 16, 'packet size should be at least 16 bytes'
    action, tid, conn_id = struct.unpack('>2IQ', res)
    assert tid == str_to_num('conn'), 'transaction id not equal to "conn"'
    assert action == 0, 'action should be "0" (connect)'
    return conn_id

if __name__ == '__main__':
    addr = ('zer0day.ch', 1337)
    res = connect(addr)
    print 'connect, get response'
    conn_id = post_connect(res)
    print 'connected, connection id -> {}'.format(conn_id)
