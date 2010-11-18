from . import io, cdb
from .construct_utils import AttrDict
from .handler import success

ASSERT_SUCCESS_HANDLER = success

class Command(object):

    __slots__ = ("cdb", "io_kwargs", 
                 "user_repr",
                 "response_handlers", 
                 "assert_success",)
    IO_TYPE = None

    def __init__(self, cdb, io_kwargs={}, user_repr=None):
        self.cdb = cdb
        self.io_kwargs = io_kwargs
        self.user_repr = user_repr
        self.response_handlers = []
        self.assert_success = True

    def __repr__(self):
        if self.user_repr is not None:
            return self.user_repr
        return super(Command, self).__repr__()

    def add_handler(self, handler, assert_success=True):
        self.assert_success &= assert_success & getattr(handler, 'assert_success', True)
        self.response_handlers.append(handler)

    def execute(self, channel, **channel_kwargs):
        response_handlers = self.response_handlers[:]
        if self.assert_success:
            response_handlers.insert(0, ASSERT_SUCCESS_HANDLER)
        return channel.execute_io(self.IO_TYPE(cdb=self.cdb, 
                                               channel_kwargs=channel_kwargs,
                                               response_handlers=response_handlers,
                                               **self.io_kwargs),
                                  **channel_kwargs)

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
        user_repr = "{0}({1})".format(self.cdb_construct.name,
                                      ", ".join("{0}={1}".format(k, v) for k, v in cdb_kwargs.iteritems()))
        return self.COMMAND_TYPE(cdb=self.cdb_construct.build(AttrDict(**cdb_kwargs)),
                                 io_kwargs=io_kwargs, user_repr=user_repr)

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

    def fixargs(self, cdb_kwargs):
        io_kwargs = dict(data_len=SECTOR*cdb_kwargs["transfer_length"])
        return cdb_kwargs, io_kwargs

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

class ExtendedCopyFactory(OutputCommandFactory):

    __slots__ = ()

    def fixargs(self, cdb_kwargs):
        parameter_list = cdb_kwargs.pop("parameter_list")
        cdb_kwargs["parameter_list_length"] = len(parameter_list)
        io_kwargs = dict(data=parameter_list)
        return cdb_kwargs, io_kwargs

TestUnitReady = NoDirectionCommandFactory(cdb.TestUnitReady)
Read6 = ReadCommandFactory(cdb.Read6)
Read10 = ReadCommandFactory(cdb.Read10)
Read16 = ReadCommandFactory(cdb.Read16)
Write6 = WriteCommandFactory(cdb.Write6)
Write10 = WriteCommandFactory(cdb.Write10)
Write16 = WriteCommandFactory(cdb.Write16)
CompareAndWrite = CompareAndWriteFactory(cdb.CompareAndWrite)
ExtendedCopy = ExtendedCopyFactory(cdb.ExtendedCopy)
