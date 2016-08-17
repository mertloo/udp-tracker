import struct, socket
from utils import str_to_num, nid
from udp_tracker import *

BUFSIZE = 1024
NID = '\xf7\xdcg\x1d^P\xd6\x8e\xae\x1e\xf9\xa6\xfd\x01\x80CR\xd4G\xa4'

def announce_request(addr, myid, size, conn_id, info_hash, timeout, key, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.settimeout(timeout)
    #pkt = struct.pack('>Q2Iss3Q4iH',
    pkt = struct.pack('>Q2I20s20s3Q4iH',
            conn_id,
            1,
            str_to_num('anno'),
            info_hash,
            #myid,
            str(NID),
            0,
            size,
            0,
            2,
            0,
            key,
            -1,
            port,
            )
    #pkt = struct.pack('>Q2I2s3Q4IH', *args)
    nbytes = s.sendto(pkt, addr)
    assert nbytes == len(pkt)
    res, _ = s.recvfrom(BUFSIZE)
    return res

def test():
    addr = ('tracker.leechers-paradise.org', 6969)
    info_hash = 'ec34208da48eb6ddf4afb95100da800b75a4852e'
    conn_id = connect_response(connect_request(addr, timeout=8))
    print '[{1}:{2}] connect id -> {0}'.format(conn_id, *addr)
    myid = nid()
    key, port = str_to_num('mtpc'), 6887
    size = 2239 * 512 * 1024
    res = announce_request(addr, myid, size, conn_id, info_hash, 8, key, port)
    assert len(res) >= 20
    print 'announce response length -> {}'.format(len(res))
    #action, tid, interval, leechers, seeders, peers = struct.unpack('>5I', res)

if __name__ == '__main__':
    test()
