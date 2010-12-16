
def debug(io):
    print io.hdr

def might_fail(io): pass

def success(io):
    assert io.hdr.info.status == "SG_INFO_OK"
