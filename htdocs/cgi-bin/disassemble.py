#!/usr/bin/python

#Disassemble lines for TI MSP430
#(C) 2001-2002 Chris Liechti <cliechti@gmx.net>
#
#GPL license
#see http://www.fsf.org/licenses/licenses.html#GPL for more information

import string, sys

#try to convert a string to a number
#treat 0xnn and nnh as hex, other as dec
def myint(s):
    if s[0:2] == '0x':
        return string.atoi(s[2:],16)
    else:
        return int(s)

regnames = [
    'PC',
    'SP',
    'SR',
    'CG2',
    'R4',
    'R5',
    'R6',
    'R7',
    'R8',
    'R9',
    'R10',
    'R11',
    'R12',
    'R13',
    'R14',
    'R15',
]

def addressMode(bytemode, as = None, ad = None, src = None, dest = None):
    x = y = ''
    c = 0
    #source first
    if as is not None:  #CG2
        if src == 2 and as > 1:
            #x = RegisterArgument(core,reg=core.R[src], bytemode=bytemode, am=as)
            x = "#%d" % (None,None,4,8)[as]
        elif src == 3:  #CG3
            #x = RegisterArgument(core,reg=core.R[src], bytemode=bytemode, am=as)
            x = "#%d" % (0,1,2,-1)[as]
        else:
            if   as == 0:   #register mode
                x = regnames[src]
                #x = RegisterArgument(core,reg=core.R[src], bytemode=bytemode, am=as)
            elif as == 1:   #pc rel
                if src == 0:
                    x = '%(x)s'
                    #x = IndexedRegisterArgument(core, reg=core.PC, offset=pc.next(), bytemode=bytemode)
                    c = c + 2  #fetch+read
                elif src == 2: #abs
                    x = '&%(x)s'
                    #x = MemoryArgument(core, address=pc.next(), bytemode=bytemode)
                    c = c + 2  #fetch+read
                else:           #indexed
                    x = '%%(x)s(%s)' % regnames[src]
                    #x = IndexedRegisterArgument(core, reg=core.R[src], offset=pc.next(), bytemode=bytemode)
                    c = c + 2  #fetch+read
            elif as == 2:   #indirect
                x = '@%s' % regnames[src]
                #x = IndirectRegisterArgument(core, reg=core.R[src], bytemode=bytemode)
                c = c + 1  #target mem read
            elif as == 3:
                if src == 0:    #immediate
                    x = '#%(x)s'
                    #x = ImmediateArgument(core, value=pc.next(), bytemode=bytemode)
                    c = c + 1  #fetch
                else:           #indirect autoincrement
                    x = '@%s+' % regnames[src]
                    #x = IndirectAutoincrementRegisterArgument(core, reg=core.R[src], bytemode=bytemode)
                    c = c + 1  #read
            else:
                raise "addressing mode error"
    #dest
    if ad is not None:
        if ad == 0:
            y = '%s' % regnames[dest]
            #y = RegisterArgument(core, reg=core.R[dest], bytemode=bytemode, am=ad)
            if dest == 0 and as != 1:
                c = c + 1  #modifying PC gives one cycle penalty
        else:
            if dest == 0:   #PC relative
                y = '%(y)s'
                #y = IndexedRegisterArgument(core, reg=core.PC, offset=pc.next(), bytemode=bytemode)
                c = c + 3  #fetch + read modify write
            elif dest == 2: #abs
                y = '&%(y)s'
                #y = MemoryArgument(core, address=pc.next(), bytemode=bytemode)
                c = c + 3  #fetch + read modify write
            else:           #indexed
                y = '%%(y)s(%s)' % regnames[dest]
                #y = IndexedRegisterArgument(core, reg=core.R[dest], offset=pc.next(), bytemode=bytemode)
                c = c + 3  #fetch + read modify write

    return x,y,c


singleOperandInstructions = {
    0x00: ('rrc',  0),
    0x01: ('swpb', 0),
    0x02: ('rra',  0),
    0x03: ('sxt',  0),
    0x04: ('push', 1),    #write of stack -> 2
    0x05: ('call', 1),    #write of stack -> 2, modify PC -> 1
    0x06: ('reti', 3),    #pop SR -> 1, pop PC -> 1, modify PC -> 1
}

doubleOperandInstructions = {
    0x4: ('mov',  0),
    0x5: ('add',  0),
    0x6: ('addc', 0),
    0x7: ('subc', 0),
    0x8: ('sub',  0),
    0x9: ('cmp',  0),
    0xa: ('dadd', 0),
    0xb: ('bit',  0),
    0xc: ('bic',  0),
    0xd: ('bis',  0),
    0xe: ('xor',  0),
    0xf: ('and',  0),
}

jumpInstructions = {
    0x0: ('jnz',  1), #jne
    0x1: ('jz',   1), #jeq
    0x2: ('jnc',  1),
    0x3: ('jc',   1),
    0x4: ('jn',   1),
    0x5: ('jge',  1),
    0x6: ('jl',   1),
    0x7: ('jmp',  1),
}

def disassemble(words):
        cycles = 1              #count cycles, start with insn fetch
        usedwords = 1
        x = y = None
        if len(words) < 3: words.extend(['UNKNOWN', 'UNKNOWN'])
        opcode = words[0]
        words = words[1:]   #pop used value
        #single operand
        if ((opcode & 0xf000) == 0x1000 and
                ((opcode>>7)&0x1f in singleOperandInstructions.keys())
        ):
            bytemode = (opcode>>6) & 1
            as = (opcode>>4) & 3
            src = opcode & 0xf
            x,y,c = addressMode(bytemode, as=as, src=src)
            name, addcyles = singleOperandInstructions[(opcode>>7) & 0x1f]
            cycles = cycles + c + addcyles #some functions have additional cycles (push etc)
            if not (src == 2 or src == 3):
                if as == 0:
                    if src == 0: cycles = cycles + 1 #destination PC adds one
                    if name == 'push': cycles = cycles + 2
                    if name == 'call': cycles = cycles + 2
                elif as == 1 or as == 2:
                    cycles = cycles + 1
                elif as == 3:
                    cycles = cycles + 1
                    if name == 'call': cycles = cycles + 1
            else: #this happens for immediate values provided by the constant generators
                if name == 'push': cycles = cycles + 2 -1
                if name == 'call': cycles = cycles + 3
            
            if '%' in x:
                x = x % {'x':words[0]}
                usedwords = usedwords + 1
            if name != 'reti':
                return "%s%s %s" % (name, (bytemode and '.b' or ''), x), usedwords, cycles
            else:
                return "reti", usedwords, cycles

        #double operand
        elif (opcode>>12)&0xf in doubleOperandInstructions.keys():
            bytemode = (opcode>>6) & 1
            x,y,c = addressMode(bytemode,
                src=(opcode>>8) & 0xf,
                ad=(opcode>>7) & 1,
                as=(opcode>>4) & 3,
                dest=opcode & 0xf
                )
            name, addcyles = doubleOperandInstructions[(opcode>>12) & 0xf]
            cycles = cycles + c + addcyles #some functions have additional cycles (push etc)
            if '%' in x:
                x = x % {'x':words[0]}
                words = words[1:]   #pop used value
                usedwords = usedwords + 1
            if '%' in y:
                y = y % {'y':words[0]}
                usedwords = usedwords + 1
            return "%s%s %s, %s" % (name, (bytemode and '.b' or ''), x, y), usedwords, cycles

        #jump instructions
        elif ((opcode & 0xe000) == 0x2000 and
             ((opcode>>10)&0x7 in jumpInstructions.keys())
        ):
            name, addcyles = jumpInstructions[(opcode>>10) & 0x7]
            offset = ((opcode&0x3ff)<<1)
            if offset & 0x400:  #negative?
                offset = -((~offset + 1) & 0x7ff)
            cycles = cycles + addcyles #jumps allways have 2 cycles
            return "%s %s" % (name, offset), usedwords, cycles

        #unkown instruction
        else:
            return 'illegal insn 0x%04x' % opcode, usedwords, cycles

if __name__ == '__main__':
    if len(sys.argv) > 1:
        import struct
        from optparse import OptionParser
        #extend with new int converter
        from copy import copy
        from optparse import Option, OptionValueError
        def check_intautobase(option, opt, value):
            try:
                return int(value, 0)
            except ValueError:
                raise OptionValueError(
                    "option %s: invalid integer value: %r" % (opt, value))
        class MyOption (Option):
            TYPES = Option.TYPES + ("intautobase",)
            TYPE_CHECKER = copy(Option.TYPE_CHECKER)
            TYPE_CHECKER["intautobase"] = check_intautobase
        
        
        parser = OptionParser(option_class=MyOption)
        parser.add_option("-b", "--bin", dest="binary",
                          help="read data from a binary file", metavar="FILE")
        parser.add_option("-s", "--startadr", dest="startadr",
                          help="startoffset for binary input", type="intautobase", default=0)
        
        (options, args) = parser.parse_args()
        
        if args:
            insn, words, cycles = disassemble(map(myint, args))
            sys.stdout.write("Parameter disassemble: %s  (%d words %d cycles)\n" % (insn, words, cycles))
            
        if options.binary is not None:
            sys.stderr.write("---- file: %s ----\n" % options.binary)
            if options.binary:
                import msp430, msp430.memory, msp430.elf
                data = msp430.memory.Memory()
                try:
                    data.loadFile(options.binary)
                except msp430.elf.ELFException:
                    sys.stderr.write("Attention: parsing binary file\n")
                    memory = file(options.binary, 'rb').read()
                    if len(memory) & 1: 
                        sys.stderr.write("odd length!!, cutting off last byte\n")
                        memory = memory[:-1]
                    memwords = [struct.unpack("<H", memory[x:x+2])[0] for x in range(0, len(memory), 2) ]
                    offset = 0
                    while offset < len(memwords):
                        insn, words, cycles = disassemble(memwords[offset:])
                        bytes = ' '.join(['%04x' % x for x in memwords[offset:offset+words]])
                        sys.stdout.write("0x%04x:  %-16s %-36s  (%d cycles)\n" % (options.startadr+offset*2, bytes, insn, cycles))
                        offset += words
                else:
                    memwords = []
                    for seg in data:
                        memwords = [struct.unpack("<H", seg.data[x:x+2])[0] for x in range(0, len(seg.data), 2) ]
                        sys.stdout.write("----- Address 0x%04x:\n" % seg.startaddress)
                        options.startadr = seg.startaddress
                        offset = 0
                        while offset < len(memwords):
                            insn, words, cycles = disassemble(memwords[offset:])
                            bytes = ' '.join(['%04x' % x for x in memwords[offset:offset+words]])
                            sys.stdout.write("0x%04x:  %-16s %-36s  (%d cycles)\n" % (options.startadr+offset*2, bytes, insn, cycles))
                            offset += words
    else:
        import cgi, os
        #cgitb is not available in py 1.5.2
        #import cgitb
        #cgitb.enable()

        try:
            print "Content-Type: text/html"
            print
            fields = cgi.FieldStorage()
            if fields.has_key("values"):
                values = fields['values'].value
                print "<H3>Disassembling the following words:</H3>"
                print "<pre>", values, "</pre>"
                print "<H3>Results in the following assembler instruction:</H3>"
                print "<pre>"
                insn, words, cycles = disassemble(map(myint, string.split(values)))
                print "%s  (%d cycles, %d words)" % (insn, cycles, words)
                print "</pre>"
            else:
                print "please go to the correct form to enter the data for this CGI!"
        except:
            print "there was an error :-("
            import traceback
            traceback.print_exc(file=sys.stdout)
