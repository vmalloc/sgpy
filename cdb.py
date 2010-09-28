from construct_utils import *

def _Scsi6(name, opcode):
    return DefaultStruct(name,
                         Const(Byte("opcode"), opcode),
                         EmbeddedBitStruct(BitField("lun", 3),
                                           BitField("lba", 21)),
                         Byte("transfer_length"),
                         Byte("control"),
                         defaults=dict(opcode=opcode,
                                       #lun=0,
                                       control=0))                                 

def _Scsi10(name, opcode, protect_type):
    defaults = dict(opcode=opcode,
                    dpo=False,
                    fua=False,
                    fua_nv=False,
                    group_number=0,
                    control=0)
    defaults[protect_type] = 0
    return DefaultStruct(name,
                         Const(Byte("opcode"), opcode),
                         EmbeddedBitStruct(BitField(protect_type, 3),
                                           Flag("dpo"),
                                           Flag("fua"),
                                           Padding(1),
                                           Flag("fua_nv"),
                                           Padding(1)),
                         UBInt32("lba"),
                         EmbeddedBitStruct(Padding(3),
                                           BitField("group_number", 5)),
                         UBInt16("transfer_length"),
                         Byte("control"),
                         defaults=defaults)

Read6 = _Scsi6("Read6", 0x8)
Write6 = _Scsi6("Write6", 0xA)
Read10 = _Scsi10("Read10", 0x28, "rdprotect")
Write10 = _Scsi10("Write10", 0x2A, "wrprotect")
                                         
TestUnitReady = DefaultStruct("TestUnitReady",
                              Const(Byte("opcode"), 0),
                              Padding(4),
                              Byte("control"),
                              defaults=dict(opcode=0,
                                            control=0))
