''' Implementation of "UDP Tracker Protocol for Bittorrent".
Refer to "http://www.bittorrent.org/beps/bep_0015.html".
'''
import struct, socket, random, urllib, binascii

# TODO: enhance UDPClient.

class UDPClient(object):

    def __init__(self, tracker, info_hash):
        self.connect_id = 0x41727101980 # default connection ID
        self.tracker = tracker # tracker: (host, port)
        self.info_hash = info_hash # hex string
        self.peer_id = '-PU1-' + str(id(self))
        self.downloaded = 0
        self.left = 0
        self.uploaded = 0
        self.event = 0x0 # 0x0: none; 0x1: completed; 0x2: started; 0x3: stopped
        self.key = random.randint(0, 255)
        self.num_want = -1 # default: -1
        self.recv_port = 7886
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.settimeout(8)
        self.bufsize = 4096
        self.peers = [] # list of peers
        self.interval = 0
        self.seeders = []
        self.leechers = []
        self.completed = 0

    def __del__(self):
        self.sock.close()

    def connect(self):
        '''
        Send connect request, then parse response.
        '''
        tid = ord('c')
        req = struct.pack(
                '!Q2I',
                self.connect_id, # default: 0x41727101980 
                0x0, # action: connect
                tid, # transaction ID
                )
        nbytes = self.sock.sendto(req, self.tracker)
        assert nbytes == len(req), '{} bytes was sent, expected {}'.format(nbytes, len(req))
        res, _ = self.sock.recvfrom(self.bufsize)
        assert len(res) >= 16, 'response size should be at least 16 bytes'
        action = struct.unpack_from('!I', res)[0]
        offset = 4
        r_tid = struct.unpack_from('!I', res, offset)[0]
        offset += 4
        assert r_tid == tid, 'Transaction ID not matching. (Expected {}, got {})'.format(tid, r_tid)
        if action == 0x0:
            self.connect_id = struct.unpack_from('!Q', res, offset)[0]
        elif action == 0x3:
            error = struct.unpack_from('!s', buf, offset)
            raise RuntimeError('UDPClient: connect: {}'.format(error))
        else:
            raise RuntimeError('Unrecognized action: 0x{}. (expected 0x0)'.format(action))

    def announce(self):
        '''
        Send announce request, then parse response.
        '''
        assert self.connect_id != 0x41727101980, 'Has not connected to tracker. (default connect id)'
        tid = ord('a')
        ih = self.info_hash[0]
        req = struct.pack('!Q2I20s20s3q4iH',
                self.connect_id, # connect id recieved from tracker
                0x1, # action: announce
                tid,
                binascii.unhexlify(ih),
                self.peer_id,
                self.downloaded,
                self.left,
                self.uploaded,
                self.event,
                0, # IP: default 0
                self.key, 
                self.num_want,
                self.recv_port,
                )
        nbytes = self.sock.sendto(req, self.tracker)
        assert nbytes == len(req), '{} bytes was sent, expected {}'.format(nbytes, len(req))
        res, _ = self.sock.recvfrom(self.bufsize)
        assert len(res) >= 20, 'response size should be at least 20 bytes'
        action = struct.unpack_from('!I', res)[0]
        offset = 4
        r_tid = struct.unpack_from('!I', res, offset)[0]
        offset += 4
        assert r_tid == tid, 'Transaction ID not matching. (Expected {}, got {})'.format(tid, r_tid)
        if action == 0x1:
            self.interval, _leechers, _seeders = struct.unpack_from('!3I', res, offset)
            self.seeders.append(_seeders)
            self.leechers.append(_leechers)
            offset += 4 * 3
            while offset < len(res):
                ip = socket.inet_ntoa(res[offset+1:offset+5])
                offset += 4
                port = struct.unpack_from('!H', res, offset)[0]
                offset += 2
                peer = ip, port
                self.peers.append(peer)
        elif action == 0x3:
            error = struct.unpack_from('!s', buf, offset)
            raise RuntimeError('UDPClient: announce: {}'.format(error))
        else:
            raise RuntimeError('Unrecognized action: 0x{}. (expected 0x1)'.format(action))

    def scrape(self):
        '''
        Send scrape request, then parse response.
        '''
        tid = ord('s')
        req = struct.pack('!Q2I',
                self.connect_id,
                0x2, # action: scrape
                tid,
                )
        assert len(self.info_hash) <= 74, 'at most 74 torrents can be scraped at once.'
        for ih in self.info_hash:
            req += struct.pack('!20s', binascii.unhexlify(ih))
        nbytes = self.sock.sendto(req, self.tracker)
        assert nbytes == len(req), '{} bytes was sent, expected {}'.format(nbytes, len(req))
        res, _ = self.sock.recvfrom(self.bufsize)
        assert len(res) >= 8, 'response size should be at least 8 bytes'
        action = struct.unpack_from('!I', res)[0]
        offset = 4
        r_tid = struct.unpack_from('!I', res, offset)[0]
        offset += 4
        assert r_tid == tid, 'Transaction ID not matching. (Expected {}, got {})'.format(tid, r_tid)
        if action == 0x2:
            while offset < len(res):
                _seeders, self.completed, _leechers = struct.unpack_from('!3I', res, offset)
                self.seeders.append(_seeders)
                self.leechers.append(_leechers)
                offset += 4 * 3
        elif action == 0x3:
            error = struct.unpack_from('!s', buf, offset)
            raise RuntimeError('UDPClient: scrape: {}'.format(error))
        else:
            raise RuntimeError('Unrecognized action: 0x{}. (expected 0x2)'.format(action))

if __name__ == '__main__':
    tr = ('zer0day.ch', 1337)
    ih = ['2a3af168e68cf51d8b33eed21c2557547ef26249'] * 3
    print ih
    clnt = UDPClient(tr, ih)
    clnt.connect()
    print clnt.connect_id
    clnt.event = 0
    def announce_test(clnt):
        clnt.announce()
        print clnt.interval, clnt.seeders, clnt.leechers
        print clnt.peers

    def scrape_test(clnt):
        clnt.scrape()
        print clnt.completed, clnt.seeders, clnt.leechers
        print clnt.peers

    announce_test(clnt)
    #scrape_test(clnt)


