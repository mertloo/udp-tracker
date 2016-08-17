import socket,struct
from udp_tracker import *
from udp_impl import *
from bencode import bencode, bdecode
clisocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
#connection_id=0x41727101980
connection_id = connect_response(connect_request(("9.rarbg.com", 2710), 8))
transaction_id = 12345

# responses Tracker : Specification  UDP [ User Datagaram Protocol ]
#info_hash  = "%1D%D4%D1%EDQn%DB%5CL%83%90%1B%2B%F8%83%A2%19%C0%7C%98"
info_hash = "%BAhPNX%CD%D6R%7C%FE%0DHrk%19%11%7E6Tm"
peer_id = "-UT1234-m%09%B2%D5%99%FA%1Fj%88%AC%0D%A7"
action =1 # announce
downloaded = 0
left = 0
uploaded = 0
event =0
ip = 0
key = 0
num_want = 3
port = 6883

announce_pack = struct.pack(">QLL20s20sQQQLLLLH",
        connection_id, action, transaction_id, info_hash, peer_id,
        downloaded, left, uploaded, event, ip, key, num_want, port
        )
try:
    clisocket.sendto(announce_pack, ("9.rarbg.com", 2710))
    #res, _ = clisocket.recvfrom(4096)
    res = clisocket.recv(4096)
except:
    print 'error'
finally:
    clisocket.close()
if res:
    print len(res)
    print type(res)
    '''
    _ =struct.unpack(">HLLLLQQQ20s20sLLQ",res)
    print _[1]
    print _[3]
    print _[4]
    act, tid, msg = struct.unpack(">LL12s", res)
    print act
    print tid
    print msg
    '''
    print udp_parse_announce_response(res, 12345)
#action=struct.unpack(">HLLLLQQQ20s20sLLQ",res)
