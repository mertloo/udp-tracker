import random
import socket


class _Defer(object):

    def __init__(self, name, transaction_id):
        self.name = name
        self.transaction_id = transaction_id
        self.result = None
        self.state = ''
        self.exception = None


class UDPTrackerProtocol(object):

    recv_buff_size = 4096

    def __init__(self, evloop):
        self.defers = set()
        self.evloop = evloop
        self.connection_id = 0x0

    get_transaction_id = lambda: int(random.randrange(0, 255))

    def socket(cls):
        ''' make a non-blocking socket (SOCK_DRAM)
        '''
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setblocking(0)
        return sock

    def connect(self, tracker_addr, callback):
        ''' Connect: get a connection_id
        '''
        def _read():
            ''' Connect response
            Offset  Size            Name            Value
            0       32-bit integer  action          0 // connect
            4       32-bit integer  transaction_id
            8       64-bit integer  connection_id
            16
            '''
            pkt = sock.recvfrom(self.recv_buff_size)
            if len(pkt) < 16:
                defer.exception = Exception("Packet length less than 16 bytes.") # TODO: custom exception
                defer.state = 'exception'
                return
            action, transaction_id, connection_id = struct.unpack('>2IQ', pkt)
            if action != 0x0:
                defer.exception = Exception('Response action is not "connect".') # TODO: custom exception
                defer.state = 'exception'
                return
            if transaction_id != defer.transaction_id:
                defer.exception = Exception('Inconsistent transaction_id.') # TODO: custom exception
                defer.state = 'exception'
                return
            self.connection_id = connection_id
            defer.state = 'done'

        def _write():
            ''' Connect request
            Offset  Size            Name            Value
            0       64-bit integer  protocol_id     0x41727101980 // magic constant
            8       32-bit integer  action          0 // connect
            12      32-bit integer  transaction_id
            16
            '''
            sock.sendto(pkt, tracker_addr)
            defer.state = 'sent'
            self.evloop.register(sock, READABLE, _read)

        defer = _Defer('connect', self.get_transaction_id())
        args = (0x41727101980, 0, defer.transaction_id)
        pkt = struct.pack('>Q2I', *args)
        sock = self.socket()
        # FIXME
        self.evloop.register(sock, WRITABLE, _write)
        self.defers.add(defer)
        return defer
