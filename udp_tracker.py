import struct, socket
from utils import str_to_num

BUFSIZE = 1024

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
    tid = str_to_num('conn')
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
    action, tid, conn_id = struct.unpack('>2IQ', res)
    assert tid == str_to_num('conn'), 'transaction id not equal to "conn"'
    assert action == 0, 'action should be "0" (connect)'
    return conn_id

def announce_request(conn_id, info_hash, total):
    """UDP tracker protocol - announce request

    Offset  Size            Name             Value
    0       64-bit integer  connection_id
    8       32-bit integer  action           1 // announce
    12      32-bit integer  transaction_id
    16      20-byte string  info_hash
    36      20-byte string  peer_id
    56      64-bit integer  downloaded
    64      64-bit integer  left
    72      64-bit integer  uploaded
    80      32-bit integer  event            0 // 0: none; 1: completed; 2: started; 3: stopped
    84      32-bit integer  IP address       0 // default
    88      32-bit integer  key
    92      32-bit integer  num_want        -1 // default
    96      16-bit integer  port
    98
    """
    action = 1
    tid = str_to_num('anno')
    peer_id = ''.join([chr(random.randint(0, 255)) for _ in range(20)])
    # First time announce
    uploaded = downloaded = 0 # FIXME
    left = total
    event = 0
    key = 0# FIXME ??
    num_want = -1
    port = 6881

    pass

def announce_response():
    pass

if __name__ == '__main__':
    addr = ('zer0day.ch', 1337)
    res = connect_request(addr, 8)
    print 'connect, get response'
    conn_id = connect_response(res)
    print conn_id
    print 'connected, connection id -> {}'.format(conn_id)
