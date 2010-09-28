from sg import SG_IO, SG_MAX_QUEUE, SgIoHdr, SgIoHdrSize
from fcntl import ioctl
from select import select
import os

class Reactor(object):
    _DEFAULT_START_INDEX = 0
    _DEFAULT_END_INDEX = 0xff

    @classmethod
    def fromPath(cls, path, *args, **kwargs):
        return cls(os.open(path, os.O_RDWR), *args, **kwargs)

    def __init__(self, device, 
                 queue_size=SG_MAX_QUEUE, 
                 start_index=_DEFAULT_START_INDEX,
                 end_index=_DEFAULT_END_INDEX):
        if end_index - start_index < queue_size:
            raise ValueError("index range (end - start) must be bigger then queue size")
        self._device = device
        self._queue_size = queue_size
        self._start_index = start_index
        self._end_index = end_index
        self._index = start_index
        self._in_flight_ios = {} # index to object

    def _nextIndex(self):
        index = self._index
        self._index += 1
        assert self._index <= self._end_index
        if self._index == self._end_index:
            self._index = self._start_index
        return index

    def ioctl(self, io):
        data = ioctl(self._device, SG_IO, 
                     SgIoHdr.build(io.getSgInfo()))
        io.handleSgHdr(SgIoHdr.parse(data))

    def write(self, io):
        info = io.getSgInfo()
        index = self._nextIndex()
        self._in_flight_ios[index] = io
        info["usr_ptr"] = index
        os.write(self._device, SgIoHdr.build(info))

    def read(self):
        data = os.read(self._device, SgIoHdrSize)
        hdr = SgIoHdr.parse(data)
        self._in_flight_ios.pop(hdr.usr_ptr).handleSgHdr(hdr)
        
    def process(self, ios):
        ios = iter(ios)
        PENDING_WRITES = True
        while 1:
            r, e = [self._device], []
            w = [self._device] if PENDING_WRITES else []
            r, w, e = select(r, w, e, 0)
            if self._device in r:
                self.read()
            if self._device in w:
                try:
                    io = ios.next()
                except StopIteration:
                    PENDING_WRITES = False
                else:
                    self.write(io)
            if not PENDING_WRITES and not self._in_flight_ios:
                break
