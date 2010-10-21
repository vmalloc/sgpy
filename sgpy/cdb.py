from .construct_utils import *

struct_type = DefaultStruct

def service_struct_factory(protect_type):
    return EmbeddedBitStruct(BitField(protect_type, 3),
                             Flag("dpo"),
                             Flag("fua"),
                             Padding(1),
                             Flag("fua_nv"),
                             Padding(1))

GroupStruct = EmbeddedBitStruct(Padding(3),
                                BitField("group_number", 5))

def _scsi6(name, opcode):
    return struct_type(name,
                       Const(Byte("opcode"), opcode),
                       EmbeddedBitStruct(BitField("lun", 3),
                                         BitField("lba", 21)),
                       Byte("transfer_length"),
                       Byte("control"),
                       defaults=dict(opcode=opcode,
                                     lun=0,
                                     control=0))

def _scsi10(name, opcode, protect_type):
    defaults = dict(opcode=opcode,
                    dpo=False,
                    fua=False,
                    fua_nv=False,
                    group_number=0,
                    control=0)
    defaults[protect_type] = 0
    return struct_type(name,
                       Const(Byte("opcode"), opcode),
                       service_struct_factory(protect_type),
                       UBInt32("lba"),
                       GroupStruct,
                       UBInt16("transfer_length"),
                       Byte("control"),
                       defaults=defaults)

Read6 = _scsi6("read6", 0x8)
Write6 = _scsi6("write6", 0xA)
Read10 = _scsi10("read10", 0x28, "rdprotect")
Write10 = _scsi10("write10", 0x2A, "wrprotect")

CompareAndWrite = struct_type("compare_and_write",
                              Const(Byte("opcode"), 0x89),
                              service_struct_factory("wrprotect"),
                              UBInt64("lba"),
                              Padding(3),
                              Byte("transfer_length"),
                              GroupStruct,
                              Byte("control"),
                              defaults=dict(opcode=0x89,
                                            wrprotect=0,
                                            dpo=False,
                                            fua=False,
                                            fua_nv=False,
                                            group_number=0,
                                            control=0))
                                         
TestUnitReady = struct_type("test_unit_ready",
                            Const(Byte("opcode"), 0),
                            Padding(4),
                            Byte("control"),
                            defaults=dict(opcode=0,
                                          control=0))
