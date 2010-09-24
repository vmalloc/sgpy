from construct_utils import *

def Scsi6(name, opcode):
    return DefaultStruct(name,
                         Const(Byte("opcode"), opcode),
                         EmbeddedBitStruct(BitField("lun", 3),
                                           BitField("lba", 21)),
                         Byte("transfer_length"),
                         Byte("control"),
                         defaults=dict(opcode=opcode,
                                       lun=0,
                                       control=0))   

Write6 = Scsi6("Write6", 0xA)
Read6 = Scsi6("Read6", 0x8)
