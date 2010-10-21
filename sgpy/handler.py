
def dont_assert_success(func):
    func.assert_success = False
    return func

def debug(io):
    print io.hdr

@dont_assert_success
def might_fail(io): pass

def success(io):
    assert io.hdr.info.status == "SG_INFO_OK"
