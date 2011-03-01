#
# -*- coding: latin-1 -*-
import os
import time

import re, sys, traceback, time
from cStringIO import StringIO


def table(listoflist, tableattrs='border=1', header=None):
    print '<table %s>' % tableattrs
    if header:
        print '<tr>%s</tr>' % (('<th>%s</th>'*len(header)) % tuple(header))
    for row in listoflist:
        print '<tr>%s</tr>' % (('<td>%s</td>'*len(row)) % tuple(row))
    print '</table>'

py = re.compile(r'<py>(.*?)</py>', re.IGNORECASE | re.MULTILINE | re.DOTALL)
pyexpr = re.compile(r'£(.+?)£', re.IGNORECASE | re.MULTILINE | re.DOTALL)

class InlinePython:
    def __init__(self, generator=None):
        #populate the namespace with some useful stuff
        self.__inlinespace = {'table':table, 'sys':sys, 'os':os, 'time':time}
        #make the generator available if one specified
        if generator is not None:
            self.__inlinespace['gen'] = generator
            
    def __call__(self, text):
        #print >>sys.stderr, text
        found = 1
        while found:
            found = py.search(text)
            #print >>sys.stderr, found
            if found:
                stdout = sys.stdout
                sys.stdout = output = StringIO()
                try:
                    exec found.group(1) in self.__inlinespace
                except:
                    traceback.print_exc(file=sys.stderr)
                    output.write("<pre>")
                    traceback.print_exc(file=output)
                    output.write("</pre>")
                sys.stdout = stdout
                text = text[:found.start()] + output.getvalue() + text[found.end():]

        found = 1
        while found:
            found = pyexpr.search(text)
            #print >>sys.stderr, found
            if found:
                try:
                    output = str(eval(found.group(1), self.__inlinespace))
                except:
                    traceback.print_exc(file=sys.stderr)
                    output = "** ERROR **"
                text = text[:found.start()] + output + text[found.end():]
        return text
