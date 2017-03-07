# MIPS R3000A-compatible R3051

from collections import namedtuple

OPCode = namedtuple('OPCode', 'mnemonic desc type opcode funct')

class Instruction():
    
    def __init__(self, opcode):
        self.opcode = opcode

    @staticmethod
    def factory(word):
        opcode = hex((word & 0xfc000000) >> 26)
        funct = hex(word & 0x3f)

        inst = JInstruction.check((opcode, None))
        if inst:
            return JInstruction(word, inst)

        inst = RInstruction.check((opcode, funct))
        if inst:
            return RInstruction(word, inst)

        inst = JInstruction.check((opcode, None))
        if inst:
            return JInstruction(word, inst)

        return None


class RInstruction(Instruction):
    
    instructions_opcode = {
        ('0x00', '0x20'): OPCode('add', 'Add', 'R', '0x00', '0x20'),
        ('0x00', '0x21'): OPCode('addu', 'Add Unsigned', 'R', '0x00', '0x21'),
        ('0x00', '0x24'): OPCode('and', 'Bitwise AND', 'R', '0x00', '0x24'),
        ('0x00', '0x1A'): OPCode('div' 'Divide', 'R', '0x00', '0x1A'),
        ('0x00', '0x1B'): OPCode('divu', 'Unsigned Divide', 'R', '0x00', '0x1B'),
        ('0x00', '0x08'): OPCode('jr', 'Jump to Address in Register', 'R', '0x00', '0x08'),
        ('0x00', '0x10'): OPCode('mfhi', 'Move from HI Register', 'R', '0x00', '0x10'),
        ('0x00', '0x12'): OPCode('mflo', 'Move from LO Register', 'R', '0x00', '0x12'),
        ('0x10',  None ): OPCode('mfc0', 'Move from Coprocessor 0', 'R', '0x10', None),
        ('0x00', '0x18'): OPCode('mult', 'Multiply', 'R', '0x00', '0x18'),
        ('0x00', '0x19'): OPCode('multu', 'Unsigned Multiply', 'R', '0x00', '0x19'),
        ('0x00', '0x27'): OPCode('nor' , 'Bitwise NOR (NOT-OR)', 'R', '0x00', '0x27'),
        ('0x00', '0x26'): OPCode('xor', 'Bitwise XOR (Exclusive-OR)', 'R', '0x00', '0x26'),
        ('0x00', '0x25'): OPCode('or', 'Bitwise OR', 'R', '0x00', '0x25'),
        ('0x00', '0x2A'): OPCode('slt', 'Set to 1 if Less Than', 'R', '0x00', '0x2A'),
        ('0x00', '0x2B'): OPCode('sltu', 'Set to 1 if Less Than Unsigned', 'R', '0x00', '0x2B'),
        ('0x00', '0x00'): OPCode('sll', 'Logical Shift Left', 'R', '0x00', '0x00'),
        ('0x00', '0x02'): OPCode('srl', 'Logical Shift Right (0-extended)', 'R', '0x00', '0x02'),
        ('0x00', '0x03'): OPCode('sra', 'Arithmetic Shift Right (sign-extended)', 'R', '0x00', '0x03'),
        ('0x00', '0x22'): OPCode('sub', 'Subtract', 'R', '0x00', '0x22'),
        ('0x00', '0x23'): OPCode('subu', 'Unsigned Subtract', 'R', '0x00', '0x23'),
    }

    def __init__(self, word, opcode=None):
        super().__init__(opcode)
        self.opcode = (word & 0xfc000000) >> 26
        self.rs = (word & 0x3e00000) >> 21
        self.rt = (word & 0x1f0000) >> 16
        self.rd = (word & 0xf800) >> 11
        self.shift = (word & 0x7c0) >> 6
        self.funct = word & 0x3f

    @classmethod
    def check(cls, word):
        opcode = hex((word & 0xfc000000) >> 26)
        funct = hex(word & 0x3f)

        return (opcode, funct) in cls.instructions_opcode


class IInstruction(Instruction):

    instructions_opcode = {
        'addi': OPCode('addi', 'Add Immediate', 'I', '0x08', None),
        'addiu': OPCode('addiu', 'Add Unsigned Immediate', 'I', '0x09', None),
        'andi': OPCode('andi', 'Bitwise AND Immediate', 'I', '0x0C', None),
        'beq': OPCode('beq', 'Branch if Equal', 'I', '0x04', None),
        'bne': OPCode('bne', 'Branch if Not Equal', 'I', '0x05', None),
        'lbu': OPCode('lbu', 'Load Byte Unsigned', 'I', '0x24', None),
        'lhu': OPCode('lhu', 'Load Halfword Unsigned', 'I', '0x25', None),
        'lui': OPCode('lui', 'Load Upper Immediate', 'I', '0x0F', None),
        'lw': OPCode('lw', 'Load Word', 'I', '0x23', None),
        'ori': OPCode('ori', 'Bitwise OR Immediate', 'I', '0x0D', None),
        'sb': OPCode('sb', 'Store Byte', 'I', '0x28', None),
        'sh': OPCode('sh', 'Store Halfword', 'I', '0x29', None),
        'slti': OPCode('slti', 'Set to 1 if Less Than Immediate', 'I', '0x0A', None),
        'sltiu': OPCode('sltiu', 'Set to 1 if Less Than Unsigned Immediate', 'I', '0x0B', None),
        'sw': OPCode('sw', 'Store Word', 'I', '0x2B', None),
    }
    
    def __init__(self, word, opcode=None):
        super().__init__(opcode)
        self.opcode = (word & 0xfc000000) >> 26
        self.rs = (word & 0x3e00000) >> 21
        self.rt = (word & 0x1f0000) >> 16
        self.imm = word & 0xffff


    @classmethod
    def check(cls, word):
        opcode = hex((word & 0xfc000000) >> 26)
        return (opcode) in cls.instructions_opcode
        

class JInstruction(Instruction):

    instructions_opcode = {
        OPCode('j', 'Jump to Address', 'J', '0x02', None),
        OPCode('jal', 'Jump and Link', 'J', '0x03', None),
    }
    
    def __init__(self, word, opcode=None):
        super().__init__(opcode)
        self.opcode = (word & 0xfc000000) >> 26
        self.pseudo_address = word & 0x3ffffff


    @classmethod
    def check(cls, word):
        opcode = hex((word & 0xfc000000) >> 26)
        return (opcode) in cls.instructions_opcode


def teste(word):
    opcode = hex((word & 0xfc000000) >> 26)
    rs = hex((word & 0x3e00000) >> 21)
    rt = hex((word & 0x1f0000) >> 16)
    rd = hex((word & 0xf800) >> 11)
    shift = hex((word & 0x7c0) >> 6)
    funct = hex(word & 0x3f)
    return Instruction(opcode, rs, rt, rd, shift, funct)
