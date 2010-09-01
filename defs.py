from ctypes import sizeof, c_int
import construct

int_in_bits = sizeof(c_int) * 8
SNInt = getattr(construct, "SNInt%d" % (int_in_bits))
UNInt = getattr(construct, "UNInt%d" % (int_in_bits))
    
