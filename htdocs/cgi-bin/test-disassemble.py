import unittest
import disassemble


formatItests = [
    #input,         iop,                             cycles
    ('mov R5, R8',              [['OPC', 0x4508]], 1),
    ('br R9',                   [['OPC', 0x4900]], 2), #emulated insn see next line
    ('add R5, 0x0003(R6)',      [['OPC', 0x5586], ['DW', 0x0003]], 4),
    ('xor R8, 0x04d2',          [['OPC', 0xe880], ['PCREL', 0x04d2]], 4),
    ('mov R5, &0x04d2',         [['OPC', 0x4582], ['DW', 0x04d2]], 4),
    
    ('and @R4, R5',             [['OPC', 0xf425]], 2),
    ('br @R8',                  [['OPC', 0x4820]], 3), #emulated insn see next line
    ('xor @R5, 0x0008(R6)',     [['OPC', 0xe5a6], ['DW', 0x0008]], 5),
    ('mov @R5, 0x04d2',         [['OPC', 0x45a0], ['PCREL', 0x04d2]], 5),
    ('xor @R5, &0x04d2',        [['OPC', 0xe5a2], ['DW', 0x04d2]], 5),
    
    ('add @R5+, R6',            [['OPC', 0x5536]], 2),
    ('br @R9+',                 [['OPC', 0x4930]], 3), #emulated insn see next line
    ('xor @R5+, 0x0008(R6)',    [['OPC', 0xe5b6], ['DW', 0x0008]], 5),
    ('mov @R9+, 0x04d2',        [['OPC', 0x49b0], ['PCREL', 0x04d2]], 5),
    ('mov @R9+, &0x04d2',       [['OPC', 0x49b2], ['DW', 0x04d2]], 5),
    
    ('mov #0x0014, R9',         [['OPC', 0x4039], ['DW', 0x0014]], 2),
    ('br #0x02ae',              [['OPC', 0x4030], ['DW', 0x02ae]], 3),  #emulated insn see next line
    ('mov #0x0300, 0x0000(SP)', [['OPC', 0x40b1], ['DW', 0x0300], ['DW', 0x0000]], 5),
    ('add #0x0021, 0x04d2',     [['OPC', 0x50b0], ['DW', 0x0021], ['PCREL', 0x04d2]], 5),
    ('add #0x0021, &0x04d2',    [['OPC', 0x50b2], ['DW', 0x0021], ['DW', 0x04d2]], 5),

    ('mov 0x0002(R5), R7',      [['OPC', 0x4517], ['DW', 0x0002]], 3),
    ('br 0x0002(R6)',           [['OPC', 0x4610], ['DW', 0x0002]], 3), #emulated insn see next line
    ('mov 0x0004(R7), 0x04d2',  [['OPC', 0x4790], ['DW', 0x0004], ['PCREL', 0x04d2]], 6),
    ('add 0x0003(R4), 0x0006(R9)',[['OPC', 0x5499], ['DW', 0x0003], ['DW', 0x0006]], 6),
    ('mov 0x0002(R5), &0x04d2', [['OPC', 0x4592], ['DW', 0x0002], ['DW', 0x04d2]], 6),
    
    ('and 0x04d2, R6',          [['OPC', 0xf016], ['PCREL', 0x04d2]], 3),
    ('br 0x04d2',               [['OPC', 0x4010], ['PCREL', 0x04d2]], 3), #emulated insn see next line
    ('cmp 0x04d2, 0x162e',      [['OPC', 0x9090], ['PCREL', 0x04d2], ['PCREL', 0x162e]], 6),
    ('mov 0x04d2, 0x0000(SP)',  [['OPC', 0x4091], ['PCREL', 0x04d2], ['DW', 0x0000]], 6),
    ('mov 0x04d2, &0x162e',     [['OPC', 0x4092], ['PCREL', 0x04d2], ['DW', 0x162e]], 6),
    
    
    ('mov &0x04d2, R8',         [['OPC', 0x4218], ['DW', 0x04d2]], 3),
    ('br &0x04d2',              [['OPC', 0x4210], ['DW', 0x04d2]], 3),
    ('mov &0x04d2, 0x162e',     [['OPC', 0x4290], ['DW', 0x04d2], ['PCREL', 0x162e]], 6),
    ('mov &0x04d2, 0x0000(SP)', [['OPC', 0x4291], ['DW', 0x04d2], ['DW', 0x0000]], 6),
    ('mov &0x04d2, &0x162e',    [['OPC', 0x4292], ['DW', 0x04d2], ['DW', 0x162e]], 6),
]

class TestFormatI(unittest.TestCase):
    def testFormatI(self):
        for line, iop, desired_cylces in formatItests:
            insn = disassemble.disassemble([w for m,w in iop])
            words, cycles = insn.usedwords, insn.cycles
            #~ print
            #~ print iop, cycles 
            #~ print desired_iop, desired_cylces
            self.failUnless(str(insn).split() == line.split(), '%r failed, wrong output (%s)' % (line, insn))
            self.failUnless(desired_cylces == cycles, '%r failed, wrong number of cycles' % line)


formatIItests = [
    #input,         iop,                             cycles
    ('push #0x0008',    [['OPC', 0x1230], ['DW', 0x0008]], 4),
    ('push #0x0007',    [['OPC', 0x1230], ['DW', 0x0007]], 4),
    ('push #0x0004',    [['OPC', 0x1230], ['DW', 0x0004]], 4),
    ('push #0',         [['OPC', 0x1203]], 3),
    ('push #1',         [['OPC', 0x1213]], 3),
    ('push #2',         [['OPC', 0x1223]], 3),
    ('push #-1',        [['OPC', 0x1233]], 3),
    
    ('push @R4',        [['OPC', 0x1224]], 4),
    ('push @R4+',       [['OPC', 0x1234]], 4),
    
    ('push 0x0000(R4)', [['OPC', 0x1214], ['DW', 0x0000]], 5),
    ('push 0x04d2',     [['OPC', 0x1210], ['PCREL', 0x04d2]], 5),
    ('push &0x04d2',    [['OPC', 0x1212], ['DW', 0x04d2]], 5),
    
    ('call R4',         [['OPC', 0x1284]], 4),
    ('call 0x04d2',     [['OPC', 0x1290], ['PCREL', 0x04d2]], 5),
    ('call @R4',        [['OPC', 0x12a4]], 4),
    ('call #0x04d2',    [['OPC', 0x12b0], ['DW', 0x04d2]], 5),

    ('swpb R4',         [['OPC', 0x1084]], 1),
    ('rra 0x04d2',      [['OPC', 0x1110], ['PCREL', 0x04d2]], 4),
    ('rrc @R4',         [['OPC', 0x1024]], 3),
    ('rra #0x04d2',     [['OPC', 0x1130], ['DW', 0x04d2]], 3),
]

class TestFormatII(unittest.TestCase):
    def testFormatII(self):
        for line, iop, desired_cylces in formatIItests:
            insn = disassemble.disassemble([w for m,w in iop])
            words, cycles = insn.usedwords, insn.cycles
            #~ print
            #~ print insn, words, cycles 
            #~ print line, desired_cylces
            self.failUnless(str(insn).split() == line.split(), '%r failed, wrong output (%s)' % (line, insn))
            self.failUnless(desired_cylces == cycles, '%r failed, wrong number of cycles' % line)

formatIIItests = [
    #input,         iop,               cycles
    ('jnz +8',       [['OPC', 0x2004]], 2),
    ('jz +4',        [['OPC', 0x2402]], 2),
    ('jnc +4',       [['OPC', 0x2802]], 2),
    ('jc +4',        [['OPC', 0x2c02]], 2),
    #~ ('jhs -8',      [['OPC', 0x2ffc]], 2), #alias for jc
    ('jn +4',        [['OPC', 0x3002]], 2),
    ('jge +4',       [['OPC', 0x3402]], 2),
    ('jl +4',        [['OPC', 0x3802]], 2),
    ('jmp +4',       [['OPC', 0x3c02]], 2),
    ('jmp -2',       [['OPC', 0x3fff]], 2),
    #~ ('jmp $',       [['OPC', 0x3fff]], 2), #alias for -2
    #~ ('jmp .',       [['OPC', 0x3fff]], 2), #alias for -2
    ('jmp -1024',    [['OPC', 0x3e00]], 2),
    ('jmp +1022',    [['OPC', 0x3dff]], 2),
]

class TestFormatIII(unittest.TestCase):
    def testFormatIII(self):
        for line, iop, desired_cylces in formatIIItests:
            insn = disassemble.disassemble([w for m,w in iop])
            words, cycles = insn.usedwords, insn.cycles
            #~ print
            #~ print insn, words, cycles 
            #~ print line, desired_cylces
            self.failUnless(str(insn).split() == line.split(), '%r failed, wrong output (%s)' % (line, insn))
            self.failUnless(desired_cylces == cycles, '%r failed, wrong number of cycles' % line)

    #~ def testOutOfRangeError(self):
        #~ self.failUnlessRaises(ValueError, disassemble.disassemble, [0xfffff])
        #~ self.failUnlessRaises(ValueError, disassemble.disassemble, [])
        #~ self.failUnlessRaises(ValueError, disassemble.disassemble, [-1])

    def testWrongInputError(self):
        self.failUnlessRaises(TypeError, disassemble.disassemble, ['quatsch'])
        
class TestFormatMisc(unittest.TestCase):
    def testMiscInsns(self):
        insn = disassemble.disassemble([0x1300])
        words, cycles = insn.usedwords, insn.cycles
        self.failUnless(str(insn).strip() == 'reti')
        self.failUnless(cycles == 5)

        
if __name__ == '__main__':
    import sys
    sys.argv.append("-v")
    unittest.main()