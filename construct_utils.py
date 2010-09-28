from ctypes import sizeof, c_int, c_char, c_short, c_voidp
import construct
from construct import *
from construct.lib.container import AttrDict

size_in_bits = lambda ctype: sizeof(ctype) * 8
int_from_bits = lambda signed: lambda bits: getattr(construct, "%sNInt%d" % (signed, bits))
signed_int_from_bits = int_from_bits("S")
unsigned_int_from_bits = int_from_bits("U")
int_in_bits = size_in_bits(c_int)
char_in_bits = size_in_bits(c_char)
short_in_bits = size_in_bits(c_short)
pointer_in_bits = size_in_bits(c_voidp)

SNInt = signed_int_from_bits(int_in_bits)
UNInt = unsigned_int_from_bits(int_in_bits)
SNChar = signed_int_from_bits(char_in_bits)
UNChar = unsigned_int_from_bits(char_in_bits)
SNShort = signed_int_from_bits(short_in_bits)
UNShort = unsigned_int_from_bits(short_in_bits)
Pointer = unsigned_int_from_bits(pointer_in_bits)

arch_to_align_func = {32 : lambda bytes: min(4, bytes),
                      64 : lambda bytes: bytes}
align_func = arch_to_align_func[pointer_in_bits]
def c_struct_aligned(subcons, padding_type=Padding):
    """
    This function adds padding between sub constructs as a compiler would do.
    on 32-bit linux: every member is aligned to min(member.size, bytes).
    on 64-bit linux: every member is aligned to its size.

    the last member is padded with the number of bytes required to 
    conform to the largest type of the structure.
    
    NOTE!: this function does not handle non-basic types like Struct and arrays,
           further code is required to decompose them to into basic types.
    TBD: handle non-basic types or raise a freakin exception!
    """
    index = 0
    largest_subcon = 0
    for subcon in subcons:
        subcon_size = subcon.sizeof()
        largest_subcon = max(subcon_size, 
                             largest_subcon)
        padding = index % subcon_size
        if padding != 0:
            index += padding
            yield padding_type(padding)
        yield subcon
        index += subcon_size
    if largest_subcon == 0:
        return
    padding = index % largest_subcon
    if padding != 0:
        yield padding_type(padding)

class CStruct(Struct):
    def __init__(self, name, *subcons, **kw):
        super(CStruct, self).__init__(name, *c_struct_aligned(subcons), **kw)

class DefaultStruct(Struct):
    def __init__(self, *args, **kwargs):
        self.defaults = kwargs.pop('defaults', {})
        super(DefaultStruct, self).__init__(*args, **kwargs)

        #subcons_names = set(subcon.name for subcon in self.subcons)
        #invalid_defaults = list(set(self.defaults) - subcons_names)
        #if invalid_defaults:
        #    raise ValueError("invalid default name/s: {0}".format(invalid_defaults))
        
    def build(self, obj):
        for k, v in self.defaults.iteritems():
            if not hasattr(obj, k):
                setattr(obj, k, v)
        return super(DefaultStruct, self).build(obj)

class DefaultCStruct(CStruct, DefaultStruct):
    def __init__(self, *args, **kwargs):
        super(DefaultCStruct, self).__init__(*args, **kwargs)
