from .channel import Channel
from . import command

def init(dev=60):
    return Channel.from_path("/dev/sg{0}".format(dev))

def test():
    channel = init()
    read = command.Read10(lba=0, transfer_length=1)
    write = command.Write10(lba=0, data="a"*512)
    return channel.execute_many((read, write), async=False)
    
if __name__ == '__main__':
    test()
