import argparse

from . import *

def do_RANDOM(args):
    for _ in range(args.count):
        print(random_code())

def do_DETAIL(args):
    addr, value, cmp = code_to_data_addr(args.code)
    if cmp:
        print(f"addr={hex(addr)}, value={value}, check={cmp}")
    else:
        print(f"addr={hex(addr)}, value={value}")

def do_CHANGE(args):
    addr, value, cmp = code_to_data_addr(args.code)
    code = addr_data_to_code(addr, args.value, cmp or False)
    print(code)

def do_IMPROVE(args):
    for code in guess_safer_code(args.code, args.rom):
        print(code)

def do_CHARSEEK(args):
    for code in guess_based_on_char(args.char, args.rom, write=args.value):
        print(code)

parser = argparse.ArgumentParser('genie')
commands = parser.add_subparsers(title='action', help='Action to be performed')

random = commands.add_parser('random',
    help='Generate random code', aliases=['r'])
random.add_argument('-n', '--count', type=int, default=1,
    help="Number of codes to generate")
random.set_defaults(func=do_RANDOM)


detail = commands.add_parser('info', aliases=['n'],
    help="Get info on code")
detail.add_argument('code', help='6-character code to improve')
detail.set_defaults(func=do_DETAIL)


change = commands.add_parser('change', aliases=['e'],
    help="Change details of a code")
change.add_argument('code', help='6-/8-character code to change')
change.add_argument('-v', '--value', required=True,
    type=lambda c: int(c, 0),
    help='Replacement value')
change.set_defaults(func=do_CHANGE)


improve = commands.add_parser('improve',
    help='Expand code to 8-character using a ROM', aliases=['i'])
improve.add_argument('code', help='6-character code to improve')
improve.add_argument('-r', '--rom', required=True,
    help='Path to ROM file')
improve.set_defaults(func=do_IMPROVE)


charseek = commands.add_parser('search', aliases=['s', 'char'],
    help='Find where a value is statically assigned')
charseek.add_argument('char', 
    help='Character/value to search for, use `0x` prefix for hex/base-16',
    type=lambda c: chr(int(c, 0)).encode())
charseek.add_argument('-r', '--rom', required=True,
    help='Path to ROM file')
charseek.add_argument('-v', '--value', default=200,
    help='Replacement value; default is `200`',
    type=lambda c: int(c, 0))
charseek.set_defaults(func=do_CHARSEEK)

args = parser.parse_args()
args.func(args)