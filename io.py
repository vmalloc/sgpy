from construct_utils import *
import cdb
import sg

import array
import fcntl

lba = 0
data_size = 512
SENSE_SIZE = 0xff
timeout = 30000
dev_name = "/dev/sg2"

data_buf = array.array("B", [0] * data_size)
data_ptr, data_len = data_buf.buffer_info()
read_cdb = cdb.Read10.build(Container(lba=lba,
                                      transfer_length=data_len / 512))
cdb_buf = array.array("B", read_cdb)
cdb_ptr, cdb_len = cdb_buf.buffer_info()

sense_buf = array.array("B", [0]*SENSE_SIZE)
sense_ptr, sense_len = sense_buf.buffer_info()

sg_hdr = sg.SgIoHdr.build(Container(dxfer_direction="SG_DXFER_FROM_DEV",
                                    cmd_len=cdb_len,
                                    mx_sb_len=sense_len,
                                    iovec_count=0,
                                    dxfer_len=data_len,
                                    dxferp=data_ptr,
                                    cmdp=cdb_ptr,
                                    sbp=sense_ptr))

dev = open(dev_name, 'r+')
result = fcntl.ioctl(dev, sg.SG_IO, sg_hdr)
print sg.SgIoHdr.parse(result)
