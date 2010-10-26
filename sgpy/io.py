from array import array

from .construct_utils import AttrDict

def bytearray(init=""):
    arr = array("b", init)
    return arr, arr.buffer_info()

class AbstractIo(object):

    __slots__ = ("cdb", "channel_kwargs", 
                 "timeout", "response_handlers",
                 "cdb_buf","cdb_ptr","cdb_len",
                 "sense_buf", "sense_ptr", "sense_len",
                 "channel", "hdr", "sense")
    SENSE_SIZE = 0xff
    DXFER_DIRECTION = None
    DEFAULT_TIMEOUT = 60000

    def __init__(self, cdb, channel_kwargs, timeout=60000, response_handlers=[]):
        self.cdb = cdb
        self.channel_kwargs = channel_kwargs
        self.timeout = timeout
        self.response_handlers = response_handlers
        self.cdb_buf, (self.cdb_ptr, self.cdb_len) = bytearray(self.cdb)
        self.sense_buf, (self.sense_ptr, self.sense_len) = bytearray([0]*self.SENSE_SIZE) 
        self.channel = None
        self.hdr = None

    def __repr__(self):
        return "{0}(timeout={1}, returned={2})".format(self.__class__.__name__,
                                                       self.timeout,
                                                       self.has_returned())

    def handle_start(self, channel):
        assert self.channel is None
        self.channel = channel

    def restart(self):
        assert self.has_returned()
        channel, self.channel, self.hdr = self.channel, None, None
        return channel.execute_io(self, **self.channel_kwargs)

    def get_sg_info(self):
        return AttrDict(dxfer_direction=self.DXFER_DIRECTION,
                        timeout=self.timeout,
                        cmd_len=self.cdb_len,
                        cmdp=self.cdb_ptr,
                        mx_sb_len=self.SENSE_SIZE,
                        sbp=self.sense_ptr)

    def handle_response(self, hdr):
        assert self.hdr is None
        self.hdr = hdr
        self.sense = self.sense_buf[:hdr.sb_len_wr].tostring()
        [handler(self) for handler in self.response_handlers]

    def has_returned(self):
        return self.hdr is not None

    def poll(self):
        assert self.channel is not None
        self.channel.poll()
        return self.has_returned()

    def wait(self, *args, **kwargs):
        self.channel.wait(poll=self.has_returned, *args, **kwargs)

class NoDirectionIo(AbstractIo):

    __slots__ = ()
    DXFER_DIRECTION = "SG_DXFER_NONE"

class InputOrOutput(AbstractIo):

    __slots__ = ()

    def get_sg_info(self):
        info = super(InputOrOutput, self).get_sg_info()
        info.__update__(dict(dxfer_len=self.data_len,
                             dxferp=self.data_ptr))
        return info

class Output(InputOrOutput):

    __slots__ = ("data_buf", "data_ptr", "data_len", "data")
    DXFER_DIRECTION = "SG_DXFER_TO_DEV"    

    def __init__(self, data, *args, **kwargs):
        super(Output, self).__init__(*args, **kwargs)
        self.data = data
        self.data_buf, (self.data_ptr, self.data_len) = bytearray(data)
                 
class Input(InputOrOutput):

    __slots__ = ("data_buf", "data_ptr", "data_len")
    DXFER_DIRECTION = "SG_DXFER_FROM_DEV"        

    def __init__(self, data_len, *args, **kwargs):
        super(Input, self).__init__(*args, **kwargs)
        self.data_buf, (self.data_ptr, self.data_len) = bytearray([0]*data_len)
