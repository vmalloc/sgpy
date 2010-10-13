from . import cdb
from . import io
from .construct_utils import AttrDict

class CommandAdapter(object):
    __slots__ = ('cdbConstruct',)
    IO_TYPE = io.Command
    def __init__(self, cdbConstruct):
        self.cdbConstruct = cdbConstruct
    def fixargs(self, kwargs):
        return kwargs, {}
    def __call__(self, timeout=None, **kwargs):
        cdbKwargs, ioKwargs = self.fixargs(kwargs)
        if timeout is not None:
            ioKwargs.update(timeout=timeout)
        return self.IO_TYPE(cdb=self.cdbConstruct.build(AttrDict(**cdbKwargs)), **ioKwargs) 

class InputAdapater(CommandAdapter):
    __slots__ = ()
    IO_TYPE = io.Input

class OutputAdapter(CommandAdapter):
    __slots__ = ()
    IO_TYPE = io.Output

SECTOR = 512

class ReadAdapter(InputAdapater):
    __slots__ = ()
    def fixargs(self, kwargs):
        ioKwargs = dict(data_len=SECTOR*kwargs['transfer_length'])
        return kwargs, ioKwargs

class WriteAdapter(OutputAdapter):
    __slots__ = ()
    def fixargs(self, kwargs):
        data = kwargs.pop('data')
        ioKwargs = dict(data=data)
        blocks, leftover = divmod(len(data), SECTOR)
        assert leftover == 0
        kwargs["transfer_length"] = blocks
        return kwargs, ioKwargs

TestUnitReady = CommandAdapter(cdb.TestUnitReady)
Read6 = ReadAdapter(cdb.Read6)
Read10 = ReadAdapter(cdb.Read10)
Write6 = WriteAdapter(cdb.Write6)
Write10 = WriteAdapter(cdb.Write10)
