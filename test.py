from cdb_adapters import Read10, Write10, SECTOR
from io import Input, Output
from reactor import Reactor
import os

reactor = None
def init(dev):
    global reactor
    reactor = Reactor.fromPath("/dev/sg%d" % (dev,))

def read_blocks(start, end, step=2048):
    ios = [Read10(lba=index, transfer_length=step) for index in range(start, end, step)]
    reactor.process(ios)
    return ios, ''.join([io.data_buf.tostring() for io in ios])

def bufferize(s, step):
    for i in range(0, len(s), step):
        yield s[i:i+step]

def write_blocks(data, lba, step=2048):
    data_bytes = len(data)
    assert data_bytes % 512 == 0
    ios = [Write10(lba=index, data=chunk) for index, chunk \
               in zip(range(lba, lba + (data_bytes / SECTOR), step), 
                      bufferize(data, step*SECTOR))]
    reactor.process(ios)
    return ios

def test_write():
    data = os.urandom(1024)
    write_blocks(data, 5, 2)
def test_read():
    assert read_blocks(0, 10, 2)[1] == read_blocks(0, 10, 1)[1]

import time
def test_iops(n=2**10, blocks=128):
    ios = [Read10(lba=0, transfer_length=blocks) for i in xrange(n)]
    stime = time.time()
    reactor.process(ios)
    print "iops: %f" % (len(ios) / (time.time() - stime))

def bad_ios(n=1000):
    ios = [Read10(lba=0, transfer_length=1) for i in xrange(n)]
    reactor.process(ios)
    return [io for io in ios if io.hdr.msg_status != 0 or io.hdr.driver_status != 0 or io.hdr.masked_status != 0 or io.hdr.status != 0]

if __name__ == '__main__':
    test_write()
    test_read()
    
