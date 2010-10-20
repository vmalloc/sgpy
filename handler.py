
def Debug(io):
    print io.hdr

def Success(io):
    assert io.hdr.info.status == "SG_INFO_OK"
