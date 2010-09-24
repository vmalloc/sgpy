from construct_utils import *
import cdb
import sg

import array
import fcntl
import os

lba = 0
data_size = 1024
SENSE_SIZE = 0xff
timeout = 30000
dev_name = "/dev/sg1"

data_buf = array.array("B", [0] * data_size)
data_ptr, data_len = data_buf.buffer_info()
read_cdb = cdb.Read6.build(Container(lba=lba,
                                     transfer_length=data_len))
cdb_buf = array.array("B", read_cdb)
cdb_ptr, cdb_len = cdb_buf.buffer_info()

sense_buf = array.array("B", [0]*SENSE_SIZE)
sense_ptr, sense_len = sense_buf.buffer_info()

sg_hdr = sg.SgIoHdr.build(Container(interface_id="SCSI_GENERIC",
                                    dxfer_direction="SG_DXFER_FROM_DEV",
                                    cmd_len=cdb_len,
                                    mx_sb_len=sense_len,
                                    iovec_count=0,
                                    dxfer_len=data_len,
                                    dxferp=data_ptr,
                                    cmdp=cdb_ptr,
                                    sbp=sense_ptr,
                                    timeout=timeout,
                                    flags=Container(SG_FLAG_DIRECT_IO=False,
                                                    SG_FLAG_LUN_INHIBIT=False,
                                                    SG_FLAG_NO_DXFER=False),
                                    pack_id=0,
                                    usr_ptr=0,
                                    status=0,
                                    masked_status=0,
                                    msg_status=0,
                                    sb_len_wr=0,
                                    host_status=0,
                                    driver_status=0,
                                    resid=0,
                                    duration=0,
                                    info=0))

sg_data = array.array("B", sg_hdr)
sg_data_ptr, sg_data_len = sg_data.buffer_info()
dev = os.open(dev_name, 'r+b')
result = dev.ioctl(sg_hdr, sg.SG_IO)
print result
