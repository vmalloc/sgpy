from construct_utils import *

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

/* Use negative values to flag difference from original sg_header structure.  */
#define SG_DXFER_NONE -1        /* e.g. a SCSI Test Unit Ready command */
#define SG_DXFER_TO_DEV -2      /* e.g. a SCSI WRITE command */
#define SG_DXFER_FROM_DEV -3    /* e.g. a SCSI READ command */
#define SG_DXFER_TO_FROM_DEV -4 /* treated like SG_DXFER_FROM_DEV with the
                                   additional property than during indirect
                                   IO the user buffer is copied into the
                                   kernel buffers before the transfer */

/* following flag values can be "or"-ed together */
#define SG_FLAG_DIRECT_IO 1     /* default is indirect IO */
#define SG_FLAG_LUN_INHIBIT 2   /* default is to put device's lun into */
                                /* the 2nd byte of SCSI command */
#define SG_FLAG_NO_DXFER 0x10000 /* no transfer of kernel buffers to/from */
                                /* user space (debug indirect IO) */

/* The following 'info' values are "or"-ed together.  */
#define SG_INFO_OK_MASK 0x1
#define SG_INFO_OK      0x0     /* no sense, host nor driver "noise" */
#define SG_INFO_CHECK   0x1     /* something abnormal happened */

#define SG_INFO_DIRECT_IO_MASK  0x6
#define SG_INFO_INDIRECT_IO     0x0     /* data xfer via kernel buffers (or no xfer) */
#define SG_INFO_DIRECT_IO       0x2     /* direct IO requested and performed */
#define SG_INFO_MIXED_IO        0x4     /* part direct, part indirect IO */

"""

SG_IO = 0x2285

SgIoHdr = CStruct("sg_io_hdr",
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
                  BitStruct("flags",
                            Flag("SG_FLAG_DIRECT_IO"),
                            Flag("SG_FLAG_LUN_INHIBIT"),
                            Padding(14),
                            Flag("SG_FLAG_NO_DXFER"),
                            Padding(int_in_bits - 17)),
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
                  BitStruct("info",
                            Enum(BitField("status", 1),
                                 SG_INFO_OK=0,
                                 SG_INFO_CHECK=1),
                            Enum(BitField("io_type", 2),
                                 SG_INFO_INDIRECT_IO=0,
                                 SG_INFO_DIRECT_IO=1,
                                 SG_INFO_MIXED_IO=2),
                            Padding(5)))
