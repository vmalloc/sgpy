
class TaskFailed(Exception):
    
    def __init__(self, io):
        super(TaskFailed, self).__init__()
        self.io = io
        
    def __str__(self):
        return "{0}".format(self.io)

def debug(io):
    print io.hdr

def might_fail(io): pass

def must_fail(io):
    assert io.hdr.info.status != "SG_INFO_OK"

def success(io):
    if io.hdr.info.status != "SG_INFO_OK":
        raise TaskFailed(io)
