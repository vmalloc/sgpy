from select import select
import time

class BaseReactor(object):
    """
    Required channel interface:
      get_fd, 
      has_pending_ios, 
      has_pending_input, 
      has_pending_output, 
      writable, 
      readable
    """

    class TimeoutError(Exception): pass
    class FdError(Exception): pass

    def __init__(self):
        self._channels = {}

    def __repr__(self):
        return "{0}({1})".format(self.__class__.__name__,
                                 ", ".join(map(repr, self._channels)))

    def register_channel(self, channel):
        self._channels[channel] = channel.get_fd()
        
    def unregister_channel(self, channel):
        self._channels.pop(channel)

    def _pending(self):
        return [channel for channel in self._channels if channel.has_pending_ios()]

    def has_pending(self):
        return bool(self._pending())

    def poll(self):
        self.wait(timeout=0, raise_on_timeout=False)
        return not self.has_pending()

    def loop(self):
        raise NotImplementedError("Abstract class")

    def wait(self, timeout=None, raise_on_timeout=True, poll=None):
        if poll is None:
            poll = lambda: not self.has_pending()
        if timeout is None:
            time_left = lambda: None
        else: 
            finish_time = time.time() + timeout
            time_left = lambda: max(0, finish_time - time.time())
        
        while not poll():
            loop_timeout = time_left() 
            self.loop(timeout=loop_timeout)
            if loop_timeout == 0: 
                if raise_on_timeout:
                    raise self.TimeoutError("timed out waiting for channels: %s" % self._pending())
                else:
                    return False
        return True

    def _get_pending_input(self):
        for channel, fd in self._channels.iteritems():
            if channel.has_pending_input():
                yield fd

    def _get_pending_output(self):
        for channel, fd in self._channels.iteritems():
            if channel.has_pending_output():
                yield fd

    def _fd_to_channel(self, fd):
        for channel, current_fd in self._channels.iteritems():
            if fd == current_fd:
                return channel
        assert False, "file descriptor not found"

    def _notify_readable(self, fd):
        self._fd_to_channel(fd).readable()

    def _notify_writable(self, fd):
        self._fd_to_channel(fd).writable()

    def _notify_error(self, fd):
        raise self.FdError("fd %d (channel %s) encountered an error" % (fd, self._fd_to_channel(fd)))

class SelectReactor(BaseReactor):

    def loop(self, timeout=None):
        r = list(self._get_pending_input())
        w = list(self._get_pending_output())
        e = list(set(r) | set(w))
        if not e:
            return
        r, w, e = select(r, w, e, timeout)
        for fd in e:
            self._notify_error(fd)
        for fd in r:
            self._notify_readable(fd)
        for fd in w:
            self._notify_writable(fd)
