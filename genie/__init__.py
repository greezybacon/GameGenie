# encoding: utf-8
import functools
import random

from .decompile import Opcodes as Ops, decompile

hexcodes = list('APZLGITYEOXUKSVN')
codes = {v:k for k,v in enumerate(hexcodes)}

def addr_data_to_code(addr, data, compare=False):
    base = addr - 0x8000
    n = [0] * (8 if compare is not False else 6)

    # Address
    n[3] |= (base >> 12) & 7
    n[5] |= (base >> 8) & 7
    n[4] |= (base >> 8) & 8
    n[2] |= (base >> 4) & 7
    n[1] |= (base >> 4) & 8
    n[4] |= base & 7
    n[3] |= base & 8

    # Data
    n[1] |= (data >> 4) & 7
    n[0] |= (data >> 4) & 8
    n[0] |= (data & 7)

    if compare is not False:
        n[2] |= 8
        n[7] |= data & 8

        # Compare
        n[7] |= (compare >> 4) & 7
        n[6] |= (compare >> 4) & 8
        n[6] |= compare & 7
        n[5] |= compare & 8
    else:
        n[5] |= data & 8


    return ''.join(map(lambda x: hexcodes[x], n))

def code_to_data_addr(code):
    n = list(map(lambda x: codes[x], list(code)))
    address = 0x8000 + (
          ((n[3] & 7) << 12)
        | ((n[5] & 7) << 8) | ((n[4] & 8) << 8)
        | ((n[2] & 7) << 4) | ((n[1] & 8) << 4)
        | (n[4] & 7) | (n[3] & 8)
    )
    data = (
          ((n[1] & 7) << 4) | ((n[0] & 8) << 4)
        | (n[0] & 7)
    )
    compare = None
    if len(code) == 8:
        data |= n[7] & 8
        compare = (
            ((n[7] & 7) << 4) | ((n[6] & 8) << 4)
          | (n[6] & 7) | (n[5] & 8)
        )
        return address, data, compare
    else:
        data |= n[5] & 8
        return address, data, None

def random_code():
    return addr_data_to_code(random.randint(0,(1<<16)-1),
        random.randint(0, 255));

def guess_safer_code(code, rom_path):
    rom = open(rom_path, 'rb')
    header = _read_rom_header(rom.read(16))

    addr, code, _ = code_to_data_addr(code)
    codes = set()
    root = header['offset'] + addr
    for x in range(header['prg_banks']):
        rom.seek(((x - 1) * 16384) + root, os.SEEK_SET)
        byte = rom.read(1)
        if byte == b'':
            break
        codes.add(addr_data_to_code(addr, code, ord(byte)))

    root = header['offset'] + (addr & 0x1FFF) + (16384 * header['prg_banks'])
    for x in range(header['chr_banks']):
        rom.seek(((x - 1) * 8192) + root, os.SEEK_SET)
        byte = rom.read(1)
        if byte == '':
            break
        codes.add(addr_data_to_code(addr, code, ord(byte)))

    return codes

def guess_based_on_char(char, rom_path, write=200, harder=False, short=False, check_dec=False):
    sta_assign = [
        [Ops.LDA(ord(char)).tobytes() + Ops.STA_A.tobytes(), 1],
        #[[0xA9, ord(char), 0x8D], 1],     # LDA Immediate, STA Absolute
        [[0xA9, ord(char), 0x85], 1],     # LDA Immediate, STA Zero Page
    ]

    dec_memory = lambda addr: [
        [Ops.DEC_A(addr).tobytes(), 0],   # DEC absolute
        #[bytes((0xC6, addr & 0xff)), 0],
        #[[0x8D, (addr >> 8) & 0xff, addr & 0xff], 0],
        [bytes([0xAE, addr & 0xff, (addr >> 8) & 0xff, 0xCA]), 0], # LDX absolute (16b), DECX
        [bytes([0xAC, addr & 0xff, (addr >> 8) & 0xff, 0x88]), 0], # LDY absolute (16b), DECY
        [bytes([0xAD, addr & 0xff, (addr >> 8) & 0xff, 0xE9]), 0], # LDA absolute (16b), SBC immediate
    ]

    if harder:
        sta_assign.extend([
            #[[b'\xa2', char, b'\x86'], 1],  # LDX Immediate, STX Zero Page
            #[[b'\xa0', char, b'\x84'], 1],  # LDY Immediate, STY Zero Page
            [[0xA0, ord(char), 0x8C], 1],   # LDY Immediate, STY Absolute
            [[0xA2, ord(char), 0x8E], 1],   # LDX Immediate, STX Absolute
    ])

    codes = set()
    for addr in _find_code_in_rom(rom_path, sta_assign):
        if check_dec:
            for code, _ in dec_memory(addr):
                if code in _read_rom(rom_path):
                    break
            else:
                # None of the bytes-sequences are in the ROM
                continue

        codes.add(addr_data_to_code(addr, write,
            ord(char) if not short else False))

    if len(codes) == 0 and not harder:
        return guess_based_on_char(char, rom_path, write, True)

    return codes

@functools.lru_cache(maxsize=2)
def _read_rom(rom_path):
    header = _read_rom_header(rom_path)
    with open(rom_path, 'rb') as rom:
        rom.seek(header['offset'], os.SEEK_SET)
        return rom.read()

def _find_code_in_rom(rom_path, sought):
    header = _read_rom_header(rom_path)
    buffer = _read_rom(rom_path)
    rom_end = 16384 * header['prg_banks']
    sought = [[bytearray(T), offset] for T, offset in sought]

    """
    for bc, location in decompile(memoryview(buffer)[:rom_end], pc=0x7ffc):
        if not bc:
            continue
        for T, offset in sought:
            if memoryview(buffer)[location:location+len(T)] == T:
                # NOTE: ROM is mapped at $8000-$FFFF, so offset
                yield ((location + offset) & 0x7FFF) + 0x8000

    return
    """

    for T, offset in sought:
        start = 0
        while True:
            try:
                location = buffer.index(T, start, rom_end)
                start = location + 1
                yield ((location + offset) & 0x7FFF) + 0x8000
            except ValueError:
                break


import struct, os
@functools.lru_cache
def _read_rom_header(rom_path):
    with open(rom_path, 'rb') as rom:
        header_bytes = rom.read(16)
        head = struct.unpack('BBBBBB', header_bytes[4:10])
        trainer = head[2] & 0x04
        return {
            'prg_banks':     head[0],
            'chr_banks':     head[1],
            'offset':        16 + (512 if trainer else 0),
        }
