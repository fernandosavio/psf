from collections import namedtuple
from struct import unpack
import zlib
import io

# MIPS R3000A-compatible R3051


"""
Versions:
    0x01: Playstation (PSF1)
    0x02: Playstation 2 (PSF2)
    0x11: Saturn (SSF) [TENTATIVE]
    0x12: Dreamcast (DSF) [TENTATIVE]
"""
Version = namedtuple('Version', ['name', 'shortname', 'code'])
VERSIONS = {
    0x01: Version('Playstation', 'PSF1', '0x01'),
    0x02: Version('Playstation 2', 'PSF2', '0x02'),
    0x11: Version('Saturn', 'SSF', '0x11'),
    0x12: Version('Dreamcast', 'DSF', '0x12'),
}

filename = "FF9.psf"


with open(filename, 'rb') as f:

    # First 3 bytes: ASCII signature: "PSF" (case sensitive)
    signature = f.read(3).decode('ascii')

    # Next 1 byte: Version byte
    psf_version = VERSIONS.get(ord(f.read(1)), None)

    # Next 4 bytes: Size of reserved area (R), little-endian unsigned long
    reserved_area_size = unpack('<L', f.read(4))[0]

    # Next 4 bytes: Compressed program length (N), little-endian unsigned long
    compressed_program_size = unpack('<L', f.read(4))[0]

    # Next 4 bytes: Compressed program CRC-32, little-endian unsigned long
    crc_32 = unpack('<L', f.read(4))[0]

    if reserved_area_size:
        # Next R bytes: Reserved area
        reserved_area = f.read(reserved_area_size)

    if compressed_program_size:
        # Next N bytes: Compressed program, in zlib compress() format.
        compressed_program = f.read(compressed_program_size)
        checksum = zlib.crc32(compressed_program)

        if checksum != crc_32:
            print('= = = WARNING = = =')
            print('CRC32 checksum not match.')
            print('Received: {}'.format(checksum))
            print('Expected: {}'.format(crc_32))

        program = zlib.decompress(compressed_program)


    # Next 5 bytes: ASCII signature: "[TAG]" (case sensitive)
    tag_mark = f.read(5)
    tags = {}

    if tag_mark == b'[TAG]':
        tag_raw = f.read()
        
        for line in tag_raw.decode('latin1').split('\n'):
            if not line.strip():
                continue

            tag, value = line.split('=', 1)
            tag, value = tag.strip(), value.strip()

            if tag in tags:
                tags[tag] += ' ' + value 
            else:
                tags[tag] = value
    
    print('=' * 15, 'PSF File Info', '=' * 15)
    print("signature: {!r}".format(signature))
    print("version: {!r}".format(psf_version))
    print("reserved_area_size: {!r}".format(reserved_area_size))
    print("compressed_program_size: {!r}".format(compressed_program_size))
    print("crc_32: {!r}".format(crc_32))
    print("checksum: {!r}".format(checksum))
    print("tag_mark: {!r}".format(tag_mark))
    
    for k, v in tags.items():
        print('TAG[{}]: {}'.format(k, v))

    print('\n\n')
    print('=' * 15, 'PSX EXE Program Info', '=' * 15)

    header = io.BytesIO(program[:0x800])
    text = io.BytesIO(program[0x800:])

    p_signature = header.read(8).decode('latin1')
    header.seek(0x010)
    p_initial_pc = unpack('<L', header.read(4))[0]
    header.seek(0x018)
    p_txt_section_start = unpack('<L', header.read(4))[0]
    header.seek(0x01C)
    p_txt_section_size = unpack('<L', header.read(4))[0]
    header.seek(0x030)
    p_initial_sp = unpack('<L', header.read(4))[0]
    header.seek(0x4C)
    p_remaining = header.read().strip(b'\x00')

    print("signature: {!r}".format(p_signature))
    print("initial_pc: {!r}".format(p_initial_pc))
    print("Text section start: {!r}".format(p_txt_section_start))
    print("Text section size: {!r}".format(p_txt_section_size))
    print("Initial SP: {!r}".format(p_initial_sp))
    # print("Resto: {!r}".format(p_remaining))


    # with open('teste.bin', 'wb') as t:
    #     t.write(text.read())
    
    


