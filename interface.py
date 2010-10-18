from inspect import getargspec

def match_signatures(f1, f2, spec_attrs=('args', 'varargs', 'keywords')):
    spec1, spec2 = (getargspec(f) for f in (f1,f2))
    for attr in spec_attrs:
        if not hasattr(spec1, attr):
            raise ValueError("illegal specification attribute: %s" % (attr,))
        attr1, attr2 = (getattr(spec, attr) for spec in (spec1, spec2))
        if attr1 != attr2:
            raise NotImplementedError("interface inconsistency: {f1}:{attr}={attr1} vs. {f2}:{attr}={attr2}".format(
                        f1=f1.__name__,
                        f2=f2.__name__,
                        attr=attr,
                        attr1=attr1,
                        attr2=attr2))
                        
class Interface(type):
    def __new__(mcls, name, bases, dict):
        for interface in (mcls,) + mcls.__bases__:
            for member_name, member in vars(interface).iteritems():
                if callable(member):
                    try:
                        func = dict[member_name]
                    except KeyError:
                        raise NotImplementedError("interface %s is not implemented" % member_name)
                    else:
                        match_signatures(member, func)
        return type.__new__(mcls, name, bases, dict)

class PollableInterface(Interface):
    def poll(self): pass # -> bool
    def wait(self, timeout=None): pass # timeout=None means no timeout

class ReactorInterface(PollableInterface):
    def register_channel(self, channel): pass
    def unregister_channel(self, channel): pass
    def loop(self, timeout=None): pass
    # poll -> bool - has pending ios

class ChannelInterface(PollableInterface):
    def execute(self, command, async=True): pass # -> io
    def many(self, commands, async=True): pass # -> ios
    def has_pending_input(self): pass # -> bool - has in-flight ios
    def has_pending_output(self): pass # -> bool - has pending ios
    def close(self): pass
    # poll -> bool - has pending ios

class FdChannelInterface(ChannelInterface):
    def get_fd(self): pass # -> file descriptor

class IoInterface(PollableInterface):
    def handle_response(self, hdr): pass 

class CommandInterfaceInterface(object):
    def execute(self, channel, async=True): pass # -> io




