from array import array
from .construct_utils import AttrDict

def bytearray(init=""):
    arr = array("b", init)
    return arr, arr.buffer_info()

class Command(object):
    SENSE_SIZE = 0xff
    
    def __init__(self, cdb, timeout=0):
        self.cdb = cdb
        self.cdb_buf, (self.cdb_ptr, self.cdb_len) = bytearray(self.cdb)
        self.sense_buf, (self.sense_ptr, self.sense_len) = bytearray([0]*self.SENSE_SIZE) 

    def getSgInfo(self):
        return AttrDict(dxfer_direction="SG_DXFER_NONE",
                        cmd_len=self.cdb_len,
                        mx_sb_len=self.SENSE_SIZE,
                        cmdp=self.cdb_ptr,
                        sbp=self.sense_ptr)

    def handleSgHdr(self, sgHdr):
        self.hdr = sgHdr

# abstract
class InputOrOutput(Command):
    
    def __init__(self, *args, **kwargs):
        super(InputOrOutput, self).__init__(*args, **kwargs)
        
    def getSgInfo(self):
        info = super(InputOrOutput, self).getSgInfo()
        info.__update__(dict(dxfer_len=self.data_len,
                             dxferp=self.data_ptr))
        return info

class Output(InputOrOutput):
    
    def __init__(self, data, *args, **kwargs):
        super(Output, self).__init__(*args, **kwargs)
        self.data_buf, (self.data_ptr, self.data_len) = bytearray(data)

    def getSgInfo(self):
        info = super(Output, self).getSgInfo()
        info.__update__(dict(dxfer_direction="SG_DXFER_TO_DEV"))
        return info
                 
class Input(InputOrOutput):
    
    def __init__(self, data_len, *args, **kwargs):
        super(Input, self).__init__(*args, **kwargs)
        self.data_buf, (self.data_ptr, self.data_len) = bytearray([0]*data_len)

    def getSgInfo(self):
        info = super(Input, self).getSgInfo()
        info.__update__(dict(dxfer_direction="SG_DXFER_FROM_DEV"))
        return info
