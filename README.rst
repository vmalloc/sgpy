Why sgpy?
=========
sgpy provides a pythonic interface for sending scsi commands using the sg (SCSI Generic) linux driver.

Features
--------
#) asynchronous design allows sending multiple commands through multiple devices.
#) command failures (senses or various errors) are translated into exceptions (currently not very descriptive).
#) responses can be validated using a flexible callback mechanism, e.g: validate a certain sense was received, validate returned data. 

Top Level Design
----------------
sgpy consists of three layers (from application to phy):

#) Command - a scsi command, consists of a cdb (Command Descriptor block).
#) Channel - an interface for sending raw data through sg to a scsi device.
#) Reactor - provides an asynchronous interface for multiple channels.

API
===
Initialization
--------------
a channel can be created using a file descriptor,
or more commonly using the device's path:
::
  >>> from sgpy import Channel, command
  >>> Channel.from_path("/dev/sg3")
  Channel('/dev/sg3')

Basic Usage
-----------

execute a single command:
::
  >>> channel.cmd.TestUnitReady()
  NoDirectionIo(timeout=60000, returned=True)
  >>> channel.cmd.Write6(lba=0, data="a"*512)
  Output(timeout=60000, returned=True)

execute a single command asynchronously:
::
  >>> channel.cmd.Read10(lba=0, transfer_length=1, async=True)
  Input(timeout=60000, returned=False)
  >>> io = _
  >>> io.poll()
  False
  >>> io.wait()
  >>> io.poll() 
  True
  >>> io.data_buf.tostring()
  "aaa"...

execute a batch of commands:
::
  >>> cmd = command.Reserve6()
  >>> channel.execute_many([cmd, cmd])
  [NoDirectionIo(timeout=60000, returned=True),
   NoDirectionIo(timeout=60000, returned=True)]
  
execute a batch of commands asynchronously:
::
  >>> cmd = command.Release6()
  >>> channel.execute_many([cmd, cmd], async=True)
  [NoDirectionIo(timeout=60000, returned=False),
   NoDirectionIo(timeout=60000, returned=False)]
  >>> ios = _
  >>> channel.wait()
  >>> channel.poll()
  True
  >>> ios[0].poll()
  True

add response handlers:
::
  >>> command.Read10(lba=0,transfer_length=1)
  read10(control=0, lba=0, opcode=40, fua_nv=False, rdprotect=0, fua=False, dpo=False, transfer_length=1, group_number=0)
  >>> cmd = _
  >>> def print_duration(io):
  >>>     print "%r took %d milliseconds" % (io, io.hdr.duration)
  >>> cmd.add_handler(print_duration)
  >>> channel.execute(cmd) # prints: Input(timeout=60000, returned=True) took 4 milliseconds
  Input(timeout=60000, returned=True)

expecting failures (reading a non-existing lba):
::
  >>> command.Read16(lba=0xffffffff, transfer_length=1)
  Traceback (most recent call last):
  TaskFailed: Input(timeout=60000, returned=True)
  >>> command.Read16(lba=0xffffffff, transfer_length=1, verify_handler=handler.must_fail) 
  Input(timeout=60000, returned=True)

coming soon (that's what she said)
==================================
#) support for different senses / driver / host errors as exception, currently TaskFailed is raised on any error.
#) support for {might,must}_fail which expects a certain error, e.g: must fail on driver error.
#) support for running the reactor in a thread, this will allow doing ios asynchronously without blocking on the reactor.