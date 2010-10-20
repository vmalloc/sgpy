import os

from .reactor import SelectReactor
from .sg import SgIoHdr, SgIoHdrSize

def xrange_cycle(*args, **kwargs):
    while True:
        for i in xrange(*args, **kwargs):
            yield i

class Channel(object):

    _START_INDEX = 0
    _END_INDEX = 0xffffffff # max int

    @classmethod
    def from_path(cls, path, *args, **kwargs):
        return cls(os.open(path, os.O_RDWR | os.O_NONBLOCK), *args, **kwargs)

    def __init__(self, fd, reactor=None):
        self._fd = fd
        self._reactor = reactor if reactor is not None else SelectReactor()
        self._in_flight_ios = {}
        self._pending_ios = []
        self._index_gen = xrange_cycle(self._START_INDEX, self._END_INDEX)
        self._reactor.register_channel(self)

    #---user-interface---#
        
    def poll(self):
        self._reactor.poll()
        return not self.has_pending_ios()

    def wait(self, poll=None, *args, **kwargs):
        poll = poll if poll is not None else self.has_pending_ios
        self._reactor.wait(poll=poll, *args, **kwargs)

    def execute(self, command, *args, **kwargs):
        return command.execute(channel=self, *args, **kwargs)

    def execute_io(self, io, async=False, poll=True):
        self._pending_ios.append(io)
        io.handle_start(self)
        if async:
            if poll:
                self.poll()
        else:
            io.wait()
        return io

    def execute_many(self, commands, *args, **kwargs):
        return self.execute_many_ios([command.execute(channel=self) for command in commands], *args, **kwargs)

    def execute_many_ios(self, ios, async=True):
        if async:
            self.poll()
        else:
            [io.wait() for io in ios]
        return ios

    def close(self, fd=True):
        self._reactor.unregister_channel(self)
        os.close(self.fd)

    #---reactor-interface---#

    def get_fd(self):
        return self._fd
    
    def has_pending_ios(self):
        return self.has_pending_input() or self.has_pending_output()

    def has_pending_input(self):
        return bool(len(self._in_flight_ios))

    def has_pending_output(self):
        return bool(len(self._pending_ios))

    def writable(self):
        io = self._pending_ios.pop(0)
        info = io.get_sg_info()
        index = self._index_gen.next()
        self._in_flight_ios[index] = io
        info.usr_ptr = index
        os.write(self._fd, SgIoHdr.build(info))

    def readable(self):
        data = os.read(self._fd, SgIoHdrSize)
        hdr = SgIoHdr.parse(data)
        assert hdr.usr_ptr in self._in_flight_ios, "unknown io returned: %s" % (hdr,) 
        self._in_flight_ios.pop(hdr.usr_ptr).handle_response(hdr)
