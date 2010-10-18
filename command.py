from . import io, cdb
from .construct_utils import AttrDict
from .handler import Success

class Command(object):

    __slots__ = ("cdb", "io_kwargs", 
                 "response_handlers", 
                 "assert_success")
    IO_TYPE = None

    def __init__(self, cdb, io_kwargs={}):
        self.cdb = cdb
        self.io_kwargs = io_kwargs
        self.response_handlers = []
        self.assert_success = True

    def add_handler(self, handler, assert_success=True):
        self.assert_success &= assert_success
        self.response_handlers.append(handler)

    def execute(self, channel, *args, **kwargs):
        if self.assert_success:
            self.response_handlers.insert(0, Success)
        return channel.execute_io(self.IO_TYPE(cdb=self.cdb, 
                                               response_handlers=self.response_handlers,
                                               **self.io_kwargs),
                                  *args, **kwargs)

class NoDirectionCommand(Command):

    __slots__ = ()
    IO_TYPE = io.NoDirectionIo

class InputCommand(Command):

    __slots__ = ()
    IO_TYPE = io.Input    

class OutputCommand(Command):

    __slots__ = ()
    IO_TYPE = io.Output

class AbstractCommandFactory(object):

    __slots__ = ('cdb_construct')
    COMMAND_TYPE = None

    def __init__(self, cdb_construct):
        self.cdb_construct = cdb_construct

    def fixargs(self, cdb_kwargs):
        return cdb_kwargs, {}

    def __call__(self, **cdb_kwargs):
        cdb_kwargs, io_kwargs = self.fixargs(cdb_kwargs)
        return self.COMMAND_TYPE(self.cdb_construct.build(AttrDict(**cdb_kwargs)), io_kwargs)

class NoDirectionCommandFactory(AbstractCommandFactory):

    __slots__ = ()
    COMMAND_TYPE = NoDirectionCommand

class InputCommandFactory(AbstractCommandFactory):

    __slots__ = ()
    COMMAND_TYPE = InputCommand

class OutputCommandFactory(AbstractCommandFactory):

    __slots__ = ()
    COMMAND_TYPE = OutputCommand

SECTOR = 512

class ReadCommandFactory(InputCommandFactory):

    __slots__ = ()

    def fixargs(self, cdbKwargs):
        ioKwargs = dict(data_len=SECTOR*cdbKwargs["transfer_length"])
        return cdbKwargs, ioKwargs

class WriteCommandFactory(OutputCommandFactory):

    __slots__ = ()

    def fixargs(self, cdb_kwargs):
        data = cdb_kwargs.pop("data")
        io_kwargs = dict(data=data)
        blocks, leftover = divmod(len(data), SECTOR)
        assert leftover == 0
        cdb_kwargs["transfer_length"] = blocks
        return cdb_kwargs, io_kwargs

class CompareAndWriteFactory(OutputCommandFactory):

    __slots__ = ()    

    def fixargs(self, cdb_kwargs):
        data = cdb_kwargs.pop("data")
        io_kwargs = dict(data=data)
        blocks, leftover = divmod(len(data), SECTOR)
        assert leftover == 0
        assert blocks % 2 == 0
        cdb_kwargs["transfer_length"] = blocks / 2
        return cdb_kwargs, io_kwargs

TestUnitReady = NoDirectionCommandFactory(cdb.TestUnitReady)
Read6 = ReadCommandFactory(cdb.Read6)
Read10 = ReadCommandFactory(cdb.Read10)
Write6 = WriteCommandFactory(cdb.Write6)
Write10 = WriteCommandFactory(cdb.Write10)
CompareAndWrite = CompareAndWriteFactory(cdb.CompareAndWrite)
