from .construct_utils import *

struct_type = DefaultStruct

def service_struct_factory(protect_type):
    return EmbeddedBitStruct(Bits(protect_type, 3),
                             Flag("dpo"),
                             Flag("fua"),
                             Padding(1),
                             Flag("fua_nv"),
                             Padding(1))

GroupStruct = EmbeddedBitStruct(Padding(3),
                                Bits("group_number", 5))

def _scsi6(name, opcode):
    return struct_type(name,
                       Const(Byte("opcode"), opcode),
                       EmbeddedBitStruct(Bits("lun", 3),
                                         Bits("lba", 21)),
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

def _scsi16(name, opcode, protect_type):
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
                       UBInt64("lba"),
                       UBInt32("transfer_length"),
                       GroupStruct,
                       Byte("control"),
                       defaults=defaults)

Read6 = _scsi6("read6", 0x8)
Write6 = _scsi6("write6", 0xa)
Read10 = _scsi10("read10", 0x28, "rdprotect")
Write10 = _scsi10("write10", 0x2a, "wrprotect")
Read16 = _scsi16("read16", 0x88, "rdprotect")
Write16 = _scsi16("write16", 0x8a, "wrprotect")

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

#--extended-copy--#

def target_descriptor_factory(name,
                              descriptor_type_code,
                              target_descriptor_parameters,
                              device_type_specific_parameters):
    return struct_type(name,
                       Const(Byte("descriptor_type_code"), descriptor_type_code),
                       EmbeddedBitStruct(Enum(Bits("lu_id_type", 2),
                                              logical_unit_number=0,
                                              proxy_token=1),
                                         Flag("nul"),
                                         Bits("peripheral_device_type", 5)),
                       UBInt16("relative_initiator_port_identifier"),
                       target_descriptor_parameters,
                       device_type_specific_parameters,
                       defaults=dict(descriptor_type_code=descriptor_type_code))

def block_device_target_descriptor_factory(**kwargs):
    return target_descriptor_factory(device_type_specific_parameters=EmbeddedStruct(EmbeddedBitStruct(Padding(5),
                                                                                                      Flag("pad"),
                                                                                                      Padding(2)),
                                                                                    UBInt24("disk_block_length")),
                                     **kwargs)

IdentificationTargetDescriptor = block_device_target_descriptor_factory(name="identification_target_descriptor",
                       descriptor_type_code=0xe4,
                       target_descriptor_parameters=EmbeddedStruct(EmbeddedBitStruct(Padding(4),
                                                                                     Bits("code_set", 4),
                                                                                     Padding(2), 
                                                                                     Bits("association", 2),
                                                                                     Bits("designator_type", 4)),
                                                                   Padding(1),
                                                                   Byte("designator_length"),
                                                                   String("designator", 
                                                                          length=lambda con: con["designator_length"]),
                                                                   Padding(length=lambda con: 20 - con["designator_length"])))

def segment_descriptor_factory(name,
                               descriptor_type_code,
                               segment_descriptor_parameters):
    return struct_type(name,
                       Const(Byte("descriptor_type_code"), descriptor_type_code),
                       EmbeddedBitStruct(Padding(6),
                                         Flag("dc"),
                                         Flag("cat")),
                       UBInt16("descriptor_length"),
                       UBInt16("source_target_descriptor_index"),
                       UBInt16("destination_target_descriptor_index"),
                       segment_descriptor_parameters,
                       defaults=dict(descriptor_type_code=descriptor_type_code))

BlockDeviceToBlockDeviceSegmentDescriptor = segment_descriptor_factory(name="block_device_to_block_device_segment_descriptor",
                            descriptor_type_code=2,
                            segment_descriptor_parameters=EmbeddedStruct(Padding(2),
                                                                         UBInt16("block_device_number_of_blocks"),
                                                                         UBInt64("source_block_device_logical_block_address"),
                                                                         UBInt64("destination_block_device_logical_block_address")))

ParameterList = struct_type("parameter_list",
                            Byte("list_identifier"),
                            EmbeddedBitStruct(Padding(2),
                                              Flag("str"),
                                              Bits("list_id_usage", 2),
                                              Bits("priority", 3)),
                            UBInt16("target_descriptor_length"),
                            Padding(4),
                            UBInt32("segment_descriptor_length"),
                            UBInt32("inline_data_length"),
                            String("target_descriptors",
                                   length=lambda con: con["target_descriptor_length"]),
                            String("segment_descriptors",
                                   length=lambda con: con["segment_descriptor_length"]),
                            String("inline_data", 
                                   length=lambda con: con["inline_data_length"]))

ExtendedCopy = struct_type("extended_copy",
                           Const(Byte("opcode"), 0x83),
                           Padding(9),
                           UBInt32("parameter_list_length"),
                           Padding(1),
                           Byte("control"),
                           defaults=dict(opcode=0x83,
                                         control=0))
