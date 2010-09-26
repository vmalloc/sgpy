import fcntl
import sg

class SgDevice(object):

    @classmethod
    def frompath(cls, path):
        return cls(file(path ,"r+"))
                    
    def __init__(self, dev):
        self._dev = dev

    def ioctl(self, *args, **kwargs):
        return fcntl.ioctl(self._dev, sg.SG_IO, *args, **kwargs)
                  
    def close(self):
        self._dev.close()

