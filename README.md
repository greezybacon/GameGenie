# GameGenie
Python library for creating and improving Game Genie codes

### CLI Interface

Create a random 6-digit code

```
$ python3 -m genie random -n 1
EOPGYI
```

### Python Interface

Create a random 6-digit code

    >>> from genie import *
    >>> random_code()
    'GGIVNX'

Get information about a code

    >>> code_to_data_addr('GGIVNX')
    ('0xea5f', 76)

Change the data in the code

    >>> addr_data_to_code(0xea5f, 77)
    'IGIVNX'

Guess safer codes (avoid crashes) with the actual ROM file

    >>> guess_safer_code('IGIVNX', 'Double Dragon II - The Revenge (USA).nes')
    set(['IGSVNXTU', 'IGSVNZOK', 'IGSVNXOV', 'IGSVNXLN', 'IGSVNXPE', 'IGSVNZAE', 
    'IGSVNXYO', 'IGSVNZYE', 'IGSVNXVN', 'IGSVNZAX', 'IGSVNXPX', 'IGSVNZEE', 
    'IGSVNXNN', 'IGSVNXLV'])

Try some codes to start with more lives (assuming we start with 3)

    >>> guess_based_on_char(0x03, 'Double Dragon II - The Revenge (USA).nes')
    set(['EGESEALE', 'EGSPGYLE', 'EGSEOILE', 'EKELZGLE', 'EGOESTLE', 'EGEUKYLE', 
    'EGVAXZLE', 'EKXOYYLE', 'EGXZTLLE', 'EKUPTZLE', 'EKEANLLE', 'EGNAEZLE', 
    'EKVPYPLE', 'EGKAYYLE', 'EGXOAPLE'])
