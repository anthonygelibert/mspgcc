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
                    x = '0x%(x)04x'
                    #x = IndexedRegisterArgument(core, reg=core.PC, offset=pc.next(), bytemode=bytemode)
                    c = c + 2  #fetch+read
                elif src == 2: #abs
                    x = '&0x%(x)04x'
                    #x = MemoryArgument(core, address=pc.next(), bytemode=bytemode)
                    c = c + 2  #fetch+read
                else:           #indexed
                    x = '0x%%(x)04x(%s)' % regnames[src]
                    #x = IndexedRegisterArgument(core, reg=core.R[src], offset=pc.next(), bytemode=bytemode)
                    c = c + 2  #fetch+read
            elif as == 2:   #indirect
                x = '@%s' % regnames[src]
                #x = IndirectRegisterArgument(core, reg=core.R[src], bytemode=bytemode)
                c = c + 1  #target mem read
            elif as == 3:
                if src == 0:    #immediate
                    x = bytemode and '#0x%(x)02x' or '#0x%(x)04x'
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
                y = '0x%(y)04x'
                #y = IndexedRegisterArgument(core, reg=core.PC, offset=pc.next(), bytemode=bytemode)
                c = c + 3  #fetch + read modify write
            elif dest == 2: #abs
                y = '&0x%(y)04x'
                #y = MemoryArgument(core, address=pc.next(), bytemode=bytemode)
                c = c + 3  #fetch + read modify write
            else:           #indexed
                y = '0x%%(y)04x(%s)' % regnames[dest]
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

INSN_WIDTH = 7          #instruction width (args follow)
symbols = {}            #address -> label
bits = {}               #label -> list of (bits, shift, width)
bits_speacial = {}      #label -> dict: value -> name

def symbol_from_adr(opt):
    """try to find a symbolname if the argument points to an absolute address"""
    if opt[0:1] == '&':
        adr = int(opt[1:], 0)
        if adr in symbols:
            return '&%s' % (symbols[adr], )
    return opt
    
def symbols_for_bits(arg, opt):
    """for known targets, convert immediate values to a list of or'ed bits"""
    if opt[0:1] == '&':
        reg = opt[1:]
        if arg[0:1] == '#' and reg in bits:
            value = int(arg[1:], 0)
            result = []
            for names, shift, width in bits[reg]:
                mask = ((1<<width) - 1) << shift
                x = (value & mask) >> shift
                if x and names[x]:
                    value &= ~mask  #clear these bits
                    result.append(names[x])
            #if there are bits left, append them to the result, so that nothing gets lost
            if value:
                if value in bits_speacial[reg]:
                    result.append(bits_speacial[reg][value])
                else:
                    result.append('0x%x' % value)
            return '#%s' % '|'.join(result)
    return arg

class Instruction:
    """this class s used to represent an MSP430 assembler instruction.
        emulated instructions are handled on class instantiation."""
    def __init__(self, name, bytemode=0, src=None, dst=None, usedwords=0, cycles=0):
        self.name = name
        self.bytemode = bytemode
        self.src = src
        self.dst = dst
        self.usedwords = usedwords
        self.cycles = cycles
        
        #transformations of emulated instructions
        new_name = None
        if self.name == 'add':
            if self.src == '#1':
                new_name = 'inc'
            elif self.src == '#2':
                new_name = 'incd'
            elif self.src == self.dst:
                new_name = 'rla'
        elif self.name == 'addc':
            if self.src == '#0':
                new_name = 'adc'
            elif self.src == self.dst:
                new_name = 'rlc'
        elif self.name == 'dadd' and self.src == '#0':
            new_name = 'dadc'
        elif self.name == 'sub':
            if self.src == '#1':
                new_name = 'dec'
            elif self.src == '#2':
                new_name = 'decd'
        elif self.name == 'subc' and self.src == '#0':
            new_name = 'sbc'
        elif self.name == 'xor' and self.src == '#-1':
            new_name = 'inv'
        elif self.name == 'mov':
            if self.src == '#0':
                if self.dst == 'CG2':
                    new_name = 'nop'
                    self.dst = None
                else:
                    new_name = 'clr'
            elif self.src == '@SP+':
                if self.dst == 'PC':
                    new_name = 'ret'
                    self.dst = None
                else:
                    new_name = 'pop'
            elif self.dst == 'PC':
                new_name = 'br'
                self.dst = self.src
        elif self.name == 'bic' and self.dst == 'SR':
            if self.src == '#8':
                new_name = 'dint'
                self.dst = None
            elif self.src == '#1':
                new_name = 'clrc'
                self.dst = None
            elif self.src == '#4':
                new_name = 'clrn'
                self.dst = None
            elif self.src == '#2':
                new_name = 'clrz'
                self.dst = None
        elif self.name == 'bis' and self.dst == 'SR':
            if self.src == '#8':
                new_name = 'eint'
                self.dst = None
            elif self.src == '#1':
                new_name = 'setc'
                self.dst = None
            elif self.src == '#4':
                new_name = 'setn'
                self.dst = None
            elif self.src == '#2':
                new_name = 'setz'
                self.dst = None
        elif self.name == 'cmp' and self.src == '#0':
            new_name = 'tst'
        #emulated insns have no src
        if new_name is not None:
            self.name = new_name
            self.src = None

        #try to replace values by symbols
        if self.dst: self.dst = symbol_from_adr(self.dst)
        if self.src:
                self.src = symbol_from_adr(self.src)
                self.src = symbols_for_bits(self.src, self.dst)

    def __str__(self):
        if self.src is not None and self.dst is not None:
            return ("%%-%ds %%s, %%s" % INSN_WIDTH) % ("%s%s" % (self.name, (self.bytemode and '.b' or '')), self.src, self.dst)
        elif self.dst is not None:
            return ("%%-%ds %%s" % INSN_WIDTH) % ( "%s%s" % (self.name, (self.bytemode and '.b' or '')), self.dst)
        else:
            return ("%%-%ds" % INSN_WIDTH) % (self.name,)

    def str_width_label(self, label):
        if not self.jumps(): raise ValueError('only possible with jump insns')
        if self.dst is not None and self.dst[0:1] == '#' and self.src is None:
            return ("%%-%ds #%%s" % INSN_WIDTH) % (self.name, label)
        raise ValueError('only possible with dst only insns')

    def jumps(self):
        """return true if this instructions jumps (modifies the PC)"""
        return (self.name == 'call' or self.dst == 'PC') and (self.dst[0] == '#')       #XXX relative address mode missing
    
    def targetAddress(self, address):
        """only valid for instructions that jump; return the target address of the jump"""
        if self.name == 'call' or self.name == 'br':
            if self.dst[0] == '#':
                return int(self.dst[1:], 0)
            else:
                return address + int(self.dst, 0)
        else:
            raise ValueError('not a branching instruction')

    def ends_a_block(self):
        """helper for a nice output. return true if execution does not continue
        after this instruction."""
        return self.name in ('ret', 'reti', 'br')


class JumpInstruction(Instruction):
    """represent jump instructions"""
    def __init__(self, name, offset, usedwords=0, cycles=0):
        Instruction.__init__(self, name, 0, None, None, usedwords, cycles)
        self.offset = offset
    
    def jumps(self):
        """return true because this instructions jumps (modifies the PC)"""
        return 1
    
    def targetAddress(self, address):
        """return the target address of the jump"""
        return address + self.offset
    
    def __str__(self):
        return ("%%-%ds %%+d" % INSN_WIDTH) % (self.name, self.offset)

    def str_width_label(self, label):
        return ("%%-%ds %%s" % INSN_WIDTH) % (self.name, label)

    def ends_a_block(self):
        """helper for a nice output. return true if execution does not continue
        after this instruction."""
        return self.name == 'jmp'

def disassemble(words):
        """disassembler one instruction from a stream of words. returns an
        instance of Instruction. that class has informationa bout how many
        wwords have been consumed and more."""
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
            if name == 'reti':
                return Instruction(name, usedwords=usedwords, cycles=cycles)
            else:
                return Instruction(name, bytemode, dst=x, usedwords=usedwords, cycles=cycles)

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
            return Instruction(name, bytemode, src=x, dst=y, usedwords=usedwords, cycles=cycles)

        #jump instructions
        elif ((opcode & 0xe000) == 0x2000 and
             ((opcode>>10)&0x7 in jumpInstructions.keys())
        ):
            name, addcyles = jumpInstructions[(opcode>>10) & 0x7]
            offset = ((opcode&0x3ff)<<1)
            if offset & 0x400:  #negative?
                offset = -((~offset + 1) & 0x7ff)
            cycles = cycles + addcyles #jumps allways have 2 cycles
            return JumpInstruction(name, offset, usedwords=usedwords, cycles=cycles)

        #unkown instruction
        else:
            return Instruction('illegal-insn-0x%04x' % opcode, usedwords=usedwords, cycles=cycles)

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
        parser.add_option("", "--symbols", dest="symbols",
                          help="read symbol addresses from a text file", metavar="FILE")
        parser.add_option("-s", "--startadr", dest="startadr",
                          help="startoffset for binary input", type="intautobase", default=0)
        
        (options, args) = parser.parse_args()
        
        if args:
            insn, words, cycles = disassemble(map(myint, args))
            sys.stdout.write("Parameter disassemble: %s  (%d words %d cycles)\n" % (insn, words, cycles))
            
        if options.binary is not None:
            #symbol file provided?
            if options.symbols is not None:
                #parse symbol file
                for line in file(options.symbols):
                    #skip comment lines
                    if line.strip()[0:1] == '#': continue
                    #break the line in elements (whitespace separated)
                    els = line.split()
                    if len(els) >= 2:
                        adr = els.pop(0)        #1st column -> address
                        name = els.pop(0)       #2nd column -> name
                        symbols[int(adr, 0)] = name
                        #the optional third column defines names for the bits
                        if els:
                            bitstring = els.pop(0)
                            bits[name] = []
                            b = bitstring.split('|')
                            b.reverse()
                            for n, bit in enumerate(b):
                                if bit != '?':
                                    bits[name].append((['', bit], n, 1))     #name, shift, width
                            bits[name].reverse()
                        #the optional fourth column defines names for special values
                        if els:
                            bits_speacial[name] = {}
                            consts = els.pop(0).split(',')
                            for const in consts:
                                cname, cvalue = const.split('=')
                                bits_speacial[name][int(cvalue, 0)] = cname
            sys.stderr.write("---- file: %s ----\n" % options.binary)
            import mspgcc, mspgcc.memory, mspgcc.elf
            data = mspgcc.memory.Memory()
            try:
                #try to load elf, IntelHex or TI-Text
                data.loadFile(options.binary)
            except mspgcc.elf.ELFException:
                #failed, treat it as binary file
                sys.stderr.write("Attention: parsing binary file\n")
                memory = file(options.binary, 'rb').read()
                if len(memory) & 1: 
                    sys.stderr.write("odd length!!, cutting off last byte\n")
                    memory = memory[:-1]
                #can't know startaddress, use cmdline option
                data.append(mspgcc.memory.Segment(options.startadr, memory))
            #disassemble memory
            memwords = []
            labels = {}
            label_num = 1
            for seg in data:
                memwords = [struct.unpack("<H", seg.data[x:x+2])[0] for x in range(0, len(seg.data), 2) ]
                sys.stdout.write("; Address 0x%04x:\n" % seg.startaddress)
                options.startadr = seg.startaddress
                offset = 0
                lines = []
                while offset < len(memwords):
                    address = options.startadr+offset*2
                    insn = disassemble(memwords[offset:])
                    bytes = ' '.join(['%04x' % x for x in memwords[offset:offset+insn.usedwords]])
                    instext = str(insn)
                    #does this instruction jump? if so, get a label for the jump target
                    if insn.jumps():
                        l_adr = insn.targetAddress(options.startadr+offset*2+2)
                        if l_adr not in labels:
                            #create a new label
                            label = '.L%04d' % label_num
                            label_num = label_num + 1
                            labels[l_adr] = label
                        #update note with information about the values
                        if isinstance(insn, JumpInstruction):
                            instext = insn.str_width_label(labels[l_adr])
                            note = ' %+d --> 0x%04x' % (insn.offset, l_adr)
                        else:
                            instext = insn.str_width_label(labels[l_adr])
                            note = ' --> 0x%04x' % (l_adr, )
                    else:
                        note = ''
                    #save generated line
                    lines.append((address, "0x%04x:  %-16s" % (address, bytes), "%-36s ;%d cycles%s\n" % (instext, insn.cycles, note)))
                    #after unconditional jumps, make an empty line
                    if insn.ends_a_block():
                        lines.append((None, '', '\n'))
                    offset += insn.usedwords
                #now output all the lines, put the labels where they belong
                unused_labels = dict(labels)        #work on a copy
                for address, prefix, suffix in lines:
                    if address in labels:
                        label = "%s:" % labels[address]
                        del unused_labels[address]  #remove used label
                    else:
                        label = ''
                    #render lines with labels
                    sys.stdout.write("%s %-7s %s" % (prefix, label, suffix))
                #if there are labels left, print them in a list
                if unused_labels:
                    sys.stdout.write("\nLabels that could not be placed:\n")
                    for address, label in unused_labels.items():
                        sys.stdout.write("    %s = 0x%04x\n" % (label, address))
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
                insn = disassemble(map(myint, string.split(values)))
                words, cycles = insn.usedwords, insn.cycles
                print "%s  (%d cycles, %d words)" % (insn, cycles, words)
                print "</pre>"
            else:
                print "please go to the correct form to enter the data for this CGI!"
        except:
            print "there was an error :-("
            import traceback
            traceback.print_exc(file=sys.stdout)
