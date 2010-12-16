from . import io, cdb
from .construct_utils import AttrDict
from .handler import success

ASSERT_SUCCESS_HANDLER = success

#---commands---#

class Command(object):

    __slots__ = ("cdb", "io_kwargs", 
                 "response_handlers")
    IO_TYPE = None

    def __init__(self, cdb, io_kwargs={},
                 verify_handler=ASSERT_SUCCESS_HANDLER):
        self.cdb = cdb
        self.io_kwargs = io_kwargs
        self.response_handlers = [verify_handler]

    def __repr__(self):
        return "{0}(cdb(hex)={1}, io_kwargs={2})".format(self.__class__.__name__,
                                                        self.cdb.encode('hex'),
                                                        self.io_kwargs)

    def add_handler(self, handler):
        self.response_handlers.append(handler)

    def execute(self, channel, **channel_kwargs):
        return channel.execute_io(self.IO_TYPE(cdb=self.cdb,
                                               channel=channel,
                                               response_handlers=self.response_handlers,
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

class AbstractCdbCommand(Command):

    __slots__ = ("_repr",)
    CDB = None

    def fixargs(self, **kwargs):
        io_kwargs = {}
        if 'timeout' in kwargs:
            io_kwargs['timeout'] = kwargs.pop('timeout')
        return kwargs, io_kwargs

    def __init__(self, **kwargs):
        assert self.CDB is not None
        cdb_kwargs, io_kwargs = self.fixargs(**kwargs)
        super_kwargs = dict(cdb=self.CDB.build(AttrDict(**cdb_kwargs)), 
                            io_kwargs=io_kwargs)
        if 'verify_handler' in kwargs:
            super_kwargs['verify_handler'] = kwargs.pop('verify_handler')
        super(AbstractCdbCommand, self).__init__(**super_kwargs)
        attrs = self.CDB.defaults.copy()
        attrs.update(cdb_kwargs)
        self._repr = "{0}({1})".format(self.CDB.name,
                                       ", ".join("{0}={1}".format(k, v) for k, v in attrs.iteritems()))
        
    def __repr__(self):
        return self._repr

class NoDirectionCdbCommand(AbstractCdbCommand, NoDirectionCommand):

    __slots__ = ()
    
    def __init__(self, *args, **kwargs):
        return super(NoDirectionCdbCommand, self).__init__(*args, **kwargs)

class InputCdbCommand(AbstractCdbCommand, InputCommand):
    
    __slots__ = ()

    def __init__(self, *args, **kwargs):
        return super(InputCdbCommand, self).__init__(*args, **kwargs)

class OutputCdbCommand(AbstractCdbCommand, OutputCommand):

    __slots__ = ()

    def __init__(self, *args, **kwargs):
        return super(OutputCdbCommand, self).__init__(*args, **kwargs)

SECTOR = 512

class ReadCommand(InputCdbCommand):

    __slots__ = ()

    def fixargs(self, **kwargs):
        cdb_kwargs, io_kwargs = super(ReadCommand, self).fixargs(**kwargs)
        io_kwargs = dict(data_len=SECTOR*cdb_kwargs["transfer_length"])
        return cdb_kwargs, io_kwargs

class WriteCommand(OutputCdbCommand):

    __slots__ = ()

    def fixargs(self, **kwargs):
        cdb_kwargs, io_kwargs = super(WriteCommand, self).fixargs(**kwargs)
        data = cdb_kwargs.pop("data")
        io_kwargs = dict(data=data)
        blocks, leftover = divmod(len(data), SECTOR)
        assert leftover == 0
        cdb_kwargs["transfer_length"] = blocks
        return cdb_kwargs, io_kwargs

#---concrete-commands---#

class CompareAndWrite(OutputCdbCommand):

    __slots__ = ()    
    CDB = cdb.CompareAndWrite

    def fixargs(self, **kwargs):
        cdb_kwargs, io_kwargs = super(CompareAndWrite, self).fixargs(**kwargs)
        data = cdb_kwargs.pop("data")
        data_len = len(data)
        blocks, leftover = divmod(data_len, SECTOR)
        if leftover != 0:
            raise ValueError("data length({0}) does not divide in {1}".format(data_len, SECTOR))
        if blocks % 2 != 0:
            raise ValueError("compare_and_write requires an even number of blocks (got: {0})".format(blocks))

        cdb_kwargs["transfer_length"] = blocks / 2
        io_kwargs["data"] = data
        return cdb_kwargs, io_kwargs

class ExtendedCopy(OutputCdbCommand):

    __slots__ = ()
    CDB = cdb.ExtendedCopy

    def fixargs(self, **kwargs):
        cdb_kwargs, io_kwargs = super(ExtendedCopy, self).fixargs(**kwargs)
        parameter_list = kwargs.pop("parameter_list")
        cdb_kwargs["parameter_list_length"] = len(parameter_list)
        io_kwargs = dict(data=parameter_list)
        return cdb_kwargs, io_kwargs

class TestUnitReady(NoDirectionCdbCommand):
    __slots__ = ()
    CDB = cdb.TestUnitReady

class Read6(ReadCommand):
    __slots__ = ()
    CDB = cdb.Read6
class Read10(ReadCommand):
    __slots__ = ()
    CDB = cdb.Read10
class Read16(ReadCommand):
    __slots__ = ()
    CDB = cdb.Read16

class Write6(WriteCommand):
    __slots__ = ()
    CDB = cdb.Write6
class Write10(WriteCommand):
    __slots__ = ()
    CDB = cdb.Write10
class Write16(WriteCommand):
    __slots__ = ()
    CDB = cdb.Write16

class Reserve6(NoDirectionCdbCommand):
    __slots__ = ()
    CDB = cdb.Reserve6
class Release6(NoDirectionCdbCommand):
    __slots__ = ()
    CDB = cdb.Release6
class Reserve10(NoDirectionCdbCommand):
    __slots__ = ()
    CDB = cdb.Reserve10
class Release10(NoDirectionCdbCommand):
    __slots__ = ()
    CDB = cdb.Release10

concrete_commands = [CompareAndWrite,
                     ExtendedCopy,
                     TestUnitReady,
                     Read6,
                     Read10,
                     Read16,
                     Write6,
                     Write10,
                     Write16,
                     Reserve6,
                     Release6,
                     Reserve10,
                     Release10]

