import unittest
import assemble

formatItests = [
    #input,         iop,                             cycles
    ('mov R5, R8',      [['OPC', 0x4508]], 1),
    ('br  R9',          [['OPC', 0x4900]], 2),
    
    ('add R5, 3(R6)',   [['OPC', 0x5586], ['DW', 0x0003]], 4),
    ('xor R8, 1234',    [['OPC', 0xe880], ['PCREL', 0x04d2]], 4),
    ('mov R5, &1234',   [['OPC', 0x4582], ['DW', 0x04d2]], 4),
    
    ('mov 2(R5), R7',   [['OPC', 0x4517], ['DW', 0x0002]], 3),
    ('and 1234, R6',    [['OPC', 0xf016], ['PCREL', 0x04d2]], 3),
    ('mov &1234, R8',   [['OPC', 0x4218], ['DW', 0x04d2]], 3),
    
    ('add 3(R4), 6(R9)',[['OPC', 0x5499], ['DW', 0x0003], ['DW', 0x0006]], 6),
    ('cmp 1234, 5678',  [['OPC', 0x9090], ['PCREL', 0x04d2], ['PCREL', 0x162e]], 6),
    ('mov 2(R5), &1234',[['OPC', 0x4592], ['DW', 0x0002], ['DW', 0x04d2]], 6),
    ('add 1234, &5678', [['OPC', 0x5092], ['PCREL', 0x04d2], ['DW', 0x162e]], 6),
    
    ('and @R4, R5',     [['OPC', 0xf425]], 2),
    
    ('xor @R5, 8(R6)',  [['OPC', 0xe5a6], ['DW', 0x0008]], 5),
    ('mov @R5, 1234',   [['OPC', 0x45a0], ['PCREL', 0x04d2]], 5),
    ('xor @R5, &1234',  [['OPC', 0xe5a2], ['DW', 0x04d2]], 5),
    
    ('add @R5+, R6',    [['OPC', 0x5536]], 2),
    ('br  @R9+',        [['OPC', 0x4930]], 3),
    ('mov #20, R9',     [['OPC', 0x4039], ['DW', 0x0014]], 2),
    ('br  #0x02ae, R9', [['OPC', 0x4030], ['DW', 0x02ae]], 3),
    
    ('mov @R9+, 2(R4)', [['OPC', 0x49b4], ['DW', 0x0002]], 5),
    ('add #33, 1234',   [['OPC', 0x50b0], ['DW', 0x0021], ['PCREL', 0x04d2]], 5),
    ('mov @R9+, &1234', [['OPC', 0x49b2], ['DW', 0x04d2]], 5),
    ('add #33, &1234',  [['OPC', 0x50b2], ['DW', 0x0021], ['DW', 0x04d2]], 5),
]

class TestFormatI(unittest.TestCase):
    def testFormatI(self):
        for line, desired_iop, desired_cylces in formatItests:
            iop, comment, cycles = assemble.assemble(line)
            #~ print
            #~ print iop, cycles 
            #~ print desired_iop, desired_cylces
            self.failUnless(desired_iop == iop, '%r failed, wrong iop' % line)
            self.failUnless(desired_cylces == cycles, '%r failed, wrong number of cycles' % line)


formatIItests = [
    #input,         iop,                             cycles
    ('push #8',     [['OPC', 0x1230], ['DW', 0x0008]], 4),
    ('push #7',     [['OPC', 0x1230], ['DW', 0x0007]], 4),
    ('push #4',     [['OPC', 0x1230], ['DW', 0x0004]], 4),
    ('push #0',     [['OPC', 0x1203]], 3),
    ('push #1',     [['OPC', 0x1213]], 3),
    ('push #2',     [['OPC', 0x1223]], 3),
    ('push #-1',    [['OPC', 0x1233]], 3),
    
    ('call R4',     [['OPC', 0x1284]], 4),
    ('call 1234',   [['OPC', 0x1290], ['PCREL', 0x04d2]], 5),
    ('call @R4',    [['OPC', 0x12a4]], 4),
    ('call #1234',  [['OPC', 0x12b0], ['DW', 0x04d2]], 5),

    ('swpb R4',     [['OPC', 0x1084]], 1),
    ('rra 1234',    [['OPC', 0x1110], ['PCREL', 0x04d2]], 4),
    ('rrc @R4',     [['OPC', 0x1024]], 3),
    ('rra #1234',   [['OPC', 0x1130], ['DW', 0x04d2]], 3),
]

class TestFormatII(unittest.TestCase):
    def testFormatII(self):
        for line, desired_iop, desired_cylces in formatIItests:
            iop, comment, cycles = assemble.assemble(line)
            #~ print
            #~ print iop, cycles 
            #~ print desired_iop, desired_cylces
            self.failUnless(desired_iop == iop, '%r failed, wrong iop' % line)
            self.failUnless(desired_cylces == cycles, '%r failed, wrong number of cycles' % line)

formatIIItests = [
    #input,         iop,               cycles
    ('jnz 8',       [['OPC', 0x2004]], 2),
    ('jz 4',        [['OPC', 0x2402]], 2),
    ('jnc 4',       [['OPC', 0x2802]], 2),
    ('jc 4',        [['OPC', 0x2c02]], 2),
    ('jhs -8',      [['OPC', 0x2ffc]], 2),
    ('jn 4',        [['OPC', 0x3002]], 2),
    ('jge 4',       [['OPC', 0x3402]], 2),
    ('jl 4',        [['OPC', 0x3802]], 2),
    ('jmp 4',       [['OPC', 0x3c02]], 2),
    ('jmp -2',      [['OPC', 0x3fff]], 2),
]

class TestFormatIII(unittest.TestCase):
    def testFormatIII(self):
        for line, desired_iop, desired_cylces in formatIIItests:
            iop, comment, cycles = assemble.assemble(line)
            #~ print
            #~ print iop, cycles 
            #~ print desired_iop, desired_cylces
            self.failUnless(desired_iop == iop, '%r failed, wrong iop' % line)
            self.failUnless(desired_cylces == cycles, '%r failed, wrong number of cycles' % line)

class TestFormatMisc(unittest.TestCase):
    def testMiscInsns(self):
        iop, comment, cycles = assemble.assemble('reti')
        self.failUnless(iop == [['OPC', 0x1300]])
        self.failUnless(cycles == 5)

        
if __name__ == '__main__':
    import sys
    sys.argv.append("-v")
    unittest.main()