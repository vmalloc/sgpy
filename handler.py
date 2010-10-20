
def response_handler(handler):
    def new_func(command):
        command.add_handler(handler)
        return command
    return new_func

@response_handler
def Debug(io):
    print io
    print io.hdr

def Success(io):
    print io.hdr
