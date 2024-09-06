from enum import Enum
from typing import Dict, NamedTuple


class AddressType(NamedTuple):
    addr_bytes: int
    is_absolute: bool = False

    def decode(self, addr: bytes):
        if self.addr_bytes == 2:
            return (addr[1] << 8) + addr[0]
        elif self.addr_bytes == 1:
            return addr[0]


class AddressingScheme:
    Accumulator     = AddressType(addr_bytes=0)
    Implied         = AddressType(addr_bytes=0)
    Immediate       = AddressType(addr_bytes=1)
    ZeroPage        = AddressType(addr_bytes=1)
    ZeroPage_X      = AddressType(addr_bytes=1)
    Absolute        = AddressType(addr_bytes=2, is_absolute=True)
    Absolute_X      = AddressType(addr_bytes=2, is_absolute=True)
    Absolute_Y      = AddressType(addr_bytes=2, is_absolute=True)
    Indirect        = AddressType(addr_bytes=2)
    Indirect_X      = AddressType(addr_bytes=1)
    Indirect_Y      = AddressType(addr_bytes=1)
    Relative        = AddressType(addr_bytes=1)


class Opcode(NamedTuple):
    opcode:         int
    address_type:   AddressType = AddressingScheme.Implied
    is_branch:      bool = False

    def __len__(self):
        return 1 + self.address_type.addr_bytes

    def for_addr(self, addr=None):
        if self.address_type.addr_bytes == 2:
            return self.for_data(bytearray((addr & 0xff, (addr >> 8) & 0xff)))

        if self.address_type.addr_bytes == 0:
            if addr is not None:
                raise ValueError('Opcode does not take an argument')
            return OpcodeInstance(self)
        
        return self.for_data(chr(addr & 0xff).encode())

    def for_data(self, data: bytes):
        return OpcodeInstance(self, data)


class OpcodeInstance:
    def __init__(self, opcode: Opcode, data: bytes=None):
        self.opcode = opcode
        self.data = data or b''

    def __add__(self, other):
        return OpcodeSequence(self) + other

    def jmp_target(self, pc):
        
        return self.address_type.target_of(pc)

    def tobytes(self):
        return bytes((self.opcode.opcode,)) + self.data


class Opcodes(Enum):
    ADC     = Opcode(0x69, AddressingScheme.Immediate)
    ADC_Z   = Opcode(0x65, AddressingScheme.ZeroPage)
    ADC_ZX  = Opcode(0x75, AddressingScheme.ZeroPage_X)
    ADC_A   = Opcode(0x6D, AddressingScheme.Absolute)
    ADC_AX  = Opcode(0x7D, AddressingScheme.Absolute_X)
    ADC_AY  = Opcode(0x79, AddressingScheme.Absolute_Y)
    ADC_IX  = Opcode(0x61, AddressingScheme.Indirect_X)
    ADC_IY  = Opcode(0x71, AddressingScheme.Indirect_Y)

    AND     = Opcode(0x29, AddressingScheme.Immediate)
    AND_Z   = Opcode(0x25, AddressingScheme.ZeroPage)
    AND_ZX  = Opcode(0x35, AddressingScheme.ZeroPage_X)
    AND_A   = Opcode(0x2D, AddressingScheme.Absolute)
    AND_AX  = Opcode(0x3D, AddressingScheme.Absolute_X)
    AND_AY  = Opcode(0x39, AddressingScheme.Absolute_Y)
    AND_IX  = Opcode(0x21, AddressingScheme.Indirect_X)
    AND_IY  = Opcode(0x31, AddressingScheme.Indirect_Y)

    ASL     = Opcode(0x0A, AddressingScheme.Accumulator)
    ASL_Z   = Opcode(0x06, AddressingScheme.ZeroPage)
    ASL_ZX  = Opcode(0x16, AddressingScheme.ZeroPage_X)
    ASL_A   = Opcode(0x0E, AddressingScheme.Absolute)
    ASL_AX  = Opcode(0x1E, AddressingScheme.Absolute_X)

    BIT_Z   = Opcode(0x24, AddressingScheme.ZeroPage)
    BIT_A   = Opcode(0x2C, AddressingScheme.Absolute)

    BCC     = Opcode(0x90, AddressingScheme.Relative, is_branch=True)
    BCS     = Opcode(0xB0, AddressingScheme.Relative, is_branch=True)
    BEQ     = Opcode(0xF0, AddressingScheme.Relative, is_branch=True)
    BMI     = Opcode(0x30, AddressingScheme.Relative, is_branch=True)
    BNE     = Opcode(0xD0, AddressingScheme.Relative, is_branch=True)
    BPL     = Opcode(0x10, AddressingScheme.Relative, is_branch=True)

    BRK     = Opcode(0x00)
    BVC     = Opcode(0x50, AddressingScheme.Relative, is_branch=True)
    BVS     = Opcode(0x70, AddressingScheme.Relative, is_branch=True)

    CLC     = Opcode(0x18)
    CLD     = Opcode(0xD8)
    CLI     = Opcode(0x58)
    CLV     = Opcode(0xB8)

    CMP     = Opcode(0xC9, AddressingScheme.Immediate)
    CMP_Z   = Opcode(0xC5, AddressingScheme.ZeroPage)
    CMP_ZX  = Opcode(0xD5, AddressingScheme.ZeroPage_X)
    CMP_A   = Opcode(0xCD, AddressingScheme.Absolute)
    CMP_AX  = Opcode(0xDD, AddressingScheme.Absolute_X)
    CMP_AY  = Opcode(0xD9, AddressingScheme.Absolute_Y)
    CMP_IX  = Opcode(0xC1, AddressingScheme.Indirect_X)
    CMP_IY  = Opcode(0xD1, AddressingScheme.Indirect_Y)

    CPX     = Opcode(0xE0, AddressingScheme.Immediate)
    CPX_Z   = Opcode(0xE4, AddressingScheme.ZeroPage)
    CPX_A   = Opcode(0xEC, AddressingScheme.Absolute)
    CPY     = Opcode(0xC0, AddressingScheme.Immediate)
    CPY_Z   = Opcode(0xC4, AddressingScheme.ZeroPage)
    CPY_A   = Opcode(0xCC, AddressingScheme.Absolute)

    DEC_Z   = Opcode(0xC6, AddressingScheme.ZeroPage)
    DEC_ZX  = Opcode(0xD6, AddressingScheme.ZeroPage_X)
    DEC_A   = Opcode(0xCE, AddressingScheme.Absolute)
    DEC_AX  = Opcode(0xDE, AddressingScheme.Absolute_X)

    DEX     = Opcode(0xCA)
    DEY     = Opcode(0x88)

    EOR     = Opcode(0x49, AddressingScheme.Immediate)
    EOR_Z   = Opcode(0x45, AddressingScheme.ZeroPage)
    EOR_ZX  = Opcode(0x55, AddressingScheme.ZeroPage_X)
    EOR_A   = Opcode(0x4D, AddressingScheme.Absolute)
    EOR_AX  = Opcode(0x5D, AddressingScheme.Absolute_X)
    EOR_AY  = Opcode(0x59, AddressingScheme.Absolute_Y)
    EOR_IX  = Opcode(0x41, AddressingScheme.Indirect_X)
    EOR_IY  = Opcode(0x51, AddressingScheme.Indirect_Y)

    INC_Z   = Opcode(0xE6, AddressingScheme.ZeroPage)
    INC_ZX  = Opcode(0xF6, AddressingScheme.ZeroPage_X)
    INC_A   = Opcode(0xEE, AddressingScheme.Absolute)
    INC_AX  = Opcode(0xFE, AddressingScheme.Absolute_X)

    INX     = Opcode(0xE8)
    INY     = Opcode(0xC8)

    JMP_A   = Opcode(0x4C, AddressingScheme.Absolute, is_branch=True)
    JMP_I   = Opcode(0x4C, AddressingScheme.Indirect, is_branch=True)

    JSR     = Opcode(0x20, AddressingScheme.Absolute, is_branch=True)

    LDA     = Opcode(0xA9, AddressingScheme.Immediate)
    LDA_Z   = Opcode(0xA5, AddressingScheme.ZeroPage)
    LDA_ZX  = Opcode(0xB5, AddressingScheme.ZeroPage_X)
    LDA_A   = Opcode(0xAD, AddressingScheme.Absolute)
    LDA_AX  = Opcode(0xBD, AddressingScheme.Absolute_X)
    LDA_AY  = Opcode(0xB9, AddressingScheme.Absolute_Y)
    LDA_IX  = Opcode(0xA1, AddressingScheme.Indirect_X)
    LDA_IY  = Opcode(0xB1, AddressingScheme.Indirect_Y)

    LDX     = Opcode(0xA2, AddressingScheme.Immediate)
    LDX_Z   = Opcode(0xA6, AddressingScheme.ZeroPage)
    LDX_ZX  = Opcode(0xB6, AddressingScheme.ZeroPage_X)
    LDX_A   = Opcode(0xAE, AddressingScheme.Absolute)
    LDX_AX  = Opcode(0xBE, AddressingScheme.Absolute_X)

    LDY     = Opcode(0xA0, AddressingScheme.Immediate)
    LDY_Z   = Opcode(0xA4, AddressingScheme.ZeroPage)
    LDY_ZX  = Opcode(0xB4, AddressingScheme.ZeroPage_X)
    LDY_A   = Opcode(0xAC, AddressingScheme.Absolute)
    LDY_AX  = Opcode(0xBC, AddressingScheme.Absolute_X)

    LSR     = Opcode(0x4A, AddressingScheme.Accumulator)
    LSR_Z   = Opcode(0x46, AddressingScheme.ZeroPage)
    LSR_ZX  = Opcode(0x56, AddressingScheme.ZeroPage_X)
    LSR_A   = Opcode(0x4E, AddressingScheme.Absolute)
    LSR_AX  = Opcode(0x5E, AddressingScheme.Absolute_X)

    NOP     = Opcode(0xEA)

    ORA     = Opcode(0x09, AddressingScheme.Immediate)
    ORA_Z   = Opcode(0x05, AddressingScheme.ZeroPage)
    ORA_ZX  = Opcode(0x15, AddressingScheme.ZeroPage_X)
    ORA_A   = Opcode(0x0D, AddressingScheme.Absolute)
    ORA_AX  = Opcode(0x1D, AddressingScheme.Absolute_X)
    ORA_AY  = Opcode(0x19, AddressingScheme.Absolute_Y)
    ORA_IX  = Opcode(0x01, AddressingScheme.Indirect_X)
    ORA_IY  = Opcode(0x11, AddressingScheme.Indirect_Y)

    PHA     = Opcode(0x48, AddressingScheme.Implied)
    PHP     = Opcode(0x08, AddressingScheme.Implied)
    PLA     = Opcode(0x68, AddressingScheme.Implied)
    PLP     = Opcode(0x28, AddressingScheme.Implied) 

    ROL     = Opcode(0x2A, AddressingScheme.Accumulator)
    ROL_ZP  = Opcode(0x26, AddressingScheme.ZeroPage)
    ROL_ZX  = Opcode(0x36, AddressingScheme.ZeroPage_X)
    ROL_A   = Opcode(0x2E, AddressingScheme.Absolute)
    ROL_AX  = Opcode(0x2E, AddressingScheme.Absolute_X)

    ROR     = Opcode(0x6A, AddressingScheme.Accumulator)
    ROR_ZP  = Opcode(0x66, AddressingScheme.ZeroPage)
    ROR_ZX  = Opcode(0x76, AddressingScheme.ZeroPage_X)
    ROR_A   = Opcode(0x6E, AddressingScheme.Absolute)
    ROR_AX  = Opcode(0x6E, AddressingScheme.Absolute_X)

    RTI     = Opcode(0x40)
    RTS     = Opcode(0x60)

    SBC     = Opcode(0xE9, AddressingScheme.Immediate)
    SBC_Z   = Opcode(0xE5, AddressingScheme.ZeroPage)
    SBC_ZX  = Opcode(0xF5, AddressingScheme.ZeroPage_X)
    SBC_A   = Opcode(0xED, AddressingScheme.Absolute)
    SBC_AX  = Opcode(0xFD, AddressingScheme.Absolute_X)
    SBC_AY  = Opcode(0xF9, AddressingScheme.Absolute_Y)
    SBC_IX  = Opcode(0xE1, AddressingScheme.Indirect_X)
    SBC_IY  = Opcode(0xF1, AddressingScheme.Indirect_Y)

    SEC     = Opcode(0x38)
    SED     = Opcode(0xF8)
    SEI     = Opcode(0x78)

    STA_Z   = Opcode(0x85, AddressingScheme.ZeroPage)
    STA_ZX  = Opcode(0x95, AddressingScheme.ZeroPage_X)
    STA_A   = Opcode(0x8D, AddressingScheme.Absolute)
    STA_AX  = Opcode(0x9D, AddressingScheme.Absolute_X)
    STA_AY  = Opcode(0x99, AddressingScheme.Absolute_Y)
    STA_IX  = Opcode(0x81, AddressingScheme.Indirect_X)
    STA_IY  = Opcode(0x91, AddressingScheme.Indirect_Y)

    STX_Z   = Opcode(0x86, AddressingScheme.ZeroPage)
    STX_ZX  = Opcode(0x96, AddressingScheme.ZeroPage_X)
    STX_A   = Opcode(0x8E, AddressingScheme.Absolute)

    STY_Z   = Opcode(0x84, AddressingScheme.ZeroPage)
    STY_ZX  = Opcode(0x94, AddressingScheme.ZeroPage_X)
    STY_A   = Opcode(0x8C, AddressingScheme.Absolute)

    TAX     = Opcode(0xAA)
    TAY     = Opcode(0xA8)
    TSX     = Opcode(0xBA)
    TXA     = Opcode(0x8A)
    TXS     = Opcode(0x9A)
    TYA     = Opcode(0x98)

    def __call__(self, addr: int):
        return self.value.for_addr(addr)

    def tobytes(self):
        return bytes((self.value.opcode,))


class OpcodeSequence(list):
    def __init__(self, first):
        self.ops = [first]
        self.next = None

    def __iadd__(self, other):
        if isinstance(other, OpcodeSequence):
            if self.next is None:
                self.next = other
            else:
                self.next += other
        else:
            self.ops.append(other)

        return self

    def __iter__(self):
        yield from self.ops
        if self.next is not None:
            yield from self.next


_op_table = {
    op.value.opcode: op.value
    for op in Opcodes
}

def decode(data: bytes, *, pc=None, table: Dict[int, Opcode]=_op_table):
    """
    Given 6502 compiled code and a staring PC, returns a generator of a sequence
    of (Opcode, bytes, PC) tuples. See RETURNS for more info.

    Parameters:
    pc: int = None
        "Program Counter". Default is NONE which means the compiler should start
        at chip reset and read the PC from the reset vector of $FFFC and $FFFD.

    Returns: Generator[Tuple[Opcode, bytes, int]]
    A generator yielding tuples of three values: (1) the opcode at the PC
    position, (2) the bytes to be interepreted with the opcode (including
    the opcode itself), and (3) the current PC location.
    """
    dmv = memoryview(data)
    if pc is None:
        # NOTE: 6502 is little-endian
        pc = data[0xFFFD] << 8 + data[0xFFFC]

    while True:
        try:
            bc = table[dmv[pc]]
            lbc = len(bc)
            yield bc, dmv[pc:pc+lbc], pc
            pc += lbc
        except KeyError:
            # NOT a valid bytecode, just yield the one byte
            yield None, dmv[pc], pc
            pc += 1
        except IndexError:
            break

def decompile(data: bytes, *, pc: int=None):
    """
    Similar to ::decode, except that it additionally OpcodeInstance values which
    allow for more detailed output.
    """
    for op, data, pc in decode(data, pc=pc):
        if op:
            yield op.for_data(data[1:]), pc