from .construct_utils import *

"""
typedef struct sg_io_hdr
{
    int interface_id;           /* [i] 'S' for SCSI generic (required) */
    int dxfer_direction;        /* [i] data transfer direction  */
    unsigned char cmd_len;      /* [i] SCSI command length ( <= 16 bytes) */
    unsigned char mx_sb_len;    /* [i] max length to write to sbp */
    unsigned short iovec_count; /* [i] 0 implies no scatter gather */
    unsigned int dxfer_len;     /* [i] byte count of data transfer */
    void * dxferp;              /* [i] [*io] points to data transfer memory or
                                             scatter gather list */
    unsigned char * cmdp;       /* [i] [*i] points to SCSI command to perform */
    unsigned char * sbp;        /* [i] [*o] points to sense_buffer memory */
    unsigned int timeout;       /* [i] MAX_UINT->no timeout (unit: millisec) */
    unsigned int flags;         /* [i] 0 -> default, see SG_FLAG... */
    int pack_id;                /* [i->o] unused internally (normally) */
    void * usr_ptr;             /* [i->o] unused internally */
    unsigned char status;       /* [o] scsi status */
    unsigned char masked_status;/* [o] shifted, masked scsi status */
    unsigned char msg_status;   /* [o] messaging level data (optional) */
    unsigned char sb_len_wr;    /* [o] byte count actually written to sbp */
    unsigned short host_status; /* [o] errors from host adapter */
    unsigned short driver_status;/* [o] errors from software driver */
    int resid;                  /* [o] dxfer_len - actual_transferred */
    unsigned int duration;      /* [o] time taken (unit: millisec) */
    unsigned int info;          /* [o] auxiliary information */
} sg_io_hdr_t;  /* around 64 bytes long (on i386) */
"""

IOCTL_SG_IO = 0x2285
SG_MAX_QUEUE = 16

SgIoHdr = DefaultCStruct("sg_io_hdr",
                         Enum(SNInt("interface_id"), 
                              SCSI_GENERIC=ord('S')),
                         Enum(SNInt("dxfer_direction"),
                              SG_DXFER_NONE=-1,
                              SG_DXFER_TO_DEV=-2,
                              SG_DXFER_FROM_DEV=-3,
                              SG_DXFER_TO_FROM_DEV=-4),
                         UNChar("cmd_len"),
                         UNChar("mx_sb_len"),
                         UNShort("iovec_count"),
                         UNInt("dxfer_len"),
                         Pointer("dxferp"),
                         Pointer("cmdp"),
                         Pointer("sbp"),
                         UNInt("timeout"),
                         FlagsEnum(UNInt("flags"),
                                   SG_FLAG_DIRECT_IO=1,
                                   SG_FLAG_LUN_INHIBIT=2,
                                   SG_FLAG_NO_DXFER=0x10000),
                         SNInt("pack_id"),
                         Pointer("usr_ptr"),
                         UNChar("status"),
                         UNChar("masked_status"),
                         UNChar("msg_status"),
                         UNChar("sb_len_wr"),
                         UNShort("host_status"),
                         UNShort("driver_status"),
                         SNInt("resid"),
                         UNInt("duration"),
                         NativeToBigEndian(BitStruct("info",
                                                     Padding(int_in_bits - 3),
                                                     Enum(BitField("io_type", 2),
                                                          SG_INFO_INDIRECT_IO=0,
                                                          SG_INFO_DIRECT_IO=1,
                                                          SG_INFO_MIXED_IO=2),
                                                     Enum(BitField("status", 1),
                                                          SG_INFO_OK=0,
                                                          SG_INFO_CHECK=1))),
                         defaults=dict(interface_id="SCSI_GENERIC",
                                       iovec_count=0,
                                       dxfer_len=0,
                                       dxferp=0,
                                       timeout=0, # driver will set 60
                                       flags=Container(SG_FLAG_DIRECT_IO=False,
                                                       SG_FLAG_LUN_INHIBIT=False,
                                                       SG_FLAG_MMAP_IO=False,
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
                                       info=Container(status="SG_INFO_OK",
                                                      io_type="SG_INFO_INDIRECT_IO")))

SgIoHdrSize = SgIoHdr.sizeof()
