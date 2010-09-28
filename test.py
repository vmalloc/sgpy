from construct_utils import AttrDict
from cdb import Read10, Write10
from io import Input, Output
from reactor import Reactor
import os

SECTOR = 512
reactor = None

def init(dev):
    global reactor
    reactor = Reactor.fromPath("/dev/sg%d" % (dev,))

def createRead10(lba, blocks):
    return Input(cdb=Read10.build(AttrDict(lba=lba, transfer_length=blocks)), data_len=SECTOR*blocks)
def createWrite10(lba, data):
    data_len = len(data)
    assert data_len % 512 == 0
    data_blocks = data_len / 512
    return Output(cdb=Write10.build(AttrDict(lba=lba, transfer_length=data_blocks)), data=data)

def read_blocks(start, end, step):
    ios = []
    for index in range(start, end, step):
        ios.append(createRead10(index, step))
    reactor.process(ios)
    return ''.join([io.data_buf.tostring() for io in ios])

def write_blocks(data, lba, step):
    data_bytes = len(data)
    assert data_bytes % 512 == 0
    data_blocks = data_bytes / 512
    ios = []
    for index in range(lba, lba + data_blocks, step):
        ios.append(createWrite10(index, data[(index - lba)*512:((index - lba) +step)*512]))
    reactor.process(ios)

def test_write():
    data = os.urandom(1024)
    write_blocks(data, 5, 2)

def test_read():
    assert read_blocks(0, 10, 2) == read_blocks(0, 10, 1)

import time

def test_iops(n=2**16):
    ios = [createRead10(0, 1) for i in xrange(n)]
    stime = time.time()
    reactor.process(ios)
    print "iops: %f" % (len(ios) / (time.time() - stime))

def bad_ios(n=1000):
    ios = [createRead10(0, 1) for i in xrange(n)]
    reactor.process(ios)
    return [io for io in ios if io.hdr.msg_status != 0 or io.hdr.driver_status != 0 or io.hdr.masked_status != 0 or io.hdr.status != 0]

if __name__ == '__main__':
    
    test_write()
    test_read()
    
