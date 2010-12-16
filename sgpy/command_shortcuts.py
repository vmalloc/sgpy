from . import command

class CommandWrapper(object):
    
    def __init__(self, channel, cmd):
        self.channel = channel
        self.cmd = cmd

    def __call__(self, async=False, **kwargs):
        return self.channel.execute(self.cmd(**kwargs), async=async)

class CommandShortcuts(object):
    
    def __init__(self, channel):
        self.channel = channel
        for cmd in command.concrete_commands:
            setattr(self, cmd.__name__, CommandWrapper(self.channel, cmd))

