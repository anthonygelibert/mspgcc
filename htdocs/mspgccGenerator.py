"""Generates the mspgcc documentation style
"""

import os
import time

import InlinePython
from cStringIO import StringIO

from Skeleton import Skeleton
from Sidebar import Sidebar, BLANKCELL
from Banner import Banner
from HTParser import HTParser
from LinkFixer import LinkFixer



sitelinks = [
    ('index.html',             'Home'),
    ('doc.html',               'Documentation'),
    ('http://sf.net/projects/mspgcc', 'mspgcc Project page on SourceForge'),
    ]


class mspgccGenerator(Skeleton, Sidebar, Banner):
    AUTHOR = 'Webmaster'
    EMAIL = 'cliechti@users.sf.net'

    def __init__(self, file, rootdir, relthis):
        root, ext = os.path.splitext(file)
        html = root + '.html'
        p = self.__parser = HTParser(file, self.AUTHOR, self.EMAIL)
        f = self.__linkfixer = LinkFixer(html, rootdir, relthis)
        self.__body = None
        self.__cont = None
        self.__inliner = InlinePython.InlinePython(self)
        
        # Calculate the sidebar links, adding a few of our own.
        self.__d = {'rootdir': rootdir}
        p.process_sidebar()
        p.sidebar.append((None, '<hr size=1>'))
        p.sidebar.append(('mailto:diwil@users.sf.net', 'Dmitry Diky'))
        p.sidebar.append(('mailto:cliechti@users.sf.net', 'Chris Liechti'))

        p.sidebar.append(BLANKCELL)
        # It is important not to have newlines between the img tag and the end
        # end center tags, otherwise layout gets messed up.
        #p.sidebar.append(('http://www.python.org/', '''<center><img alt="[Python Powered]" border=0 src="PythonPoweredSmall.png"></center>''' % self.__d))
        self.__linkfixer.massage(p.sidebar, self.__d)
        Sidebar.__init__(self, p.sidebar)
        p.sidebar.append(BLANKCELL)
        copyright = self.__parser.get('copyright', '2001-%d' %
                                      time.localtime()[0])
        p.sidebar.append((None, '&copy; ' + copyright))
        #p.sidebar.append((None, '<hr>'))
        #p.sidebar.append((file, '[page source]'))
        # Fix up our site links, no relthis because the site links are
        # relative to the root of our web pages.
        sitelink_fixer = LinkFixer(f.myurl(), rootdir)
        sitelink_fixer.massage(sitelinks, self.__d, aboves=1)
        Banner.__init__(self, sitelinks)

    def get_title(self):
        return self.__parser.get('title')

    def get_sidebar(self):
        if self.__parser.get('wide-page', 'no').lower() == 'yes':
            return None
        return Sidebar.get_sidebar(self)

    def get_banner(self):
        buf = StringIO()
        for adr,text,extra in sitelinks:
            if adr is None:
                buf.write(' | %s' % (text,))
            else:
                if ':' in str(adr):
                    buf.write(' | <A HREF="%s">%s</A>' % (adr,text))
                else:
                    buf.write(' | <A HREF="%s/%s">%s</A>' % (self.__d['rootdir'], adr,text))
        buf.write('</SPAN>')
        return buf.getvalue()

    def get_banner_attributes(self):
        return 'CELLSPACING=0 CELLPADDING=0'

    def get_corner(self):
        # It is important not to have newlines between the img tag and the end
        # anchor and end center tags, otherwise layout gets messed up
        return '<B>&nbsp;<FONT color="#ffffff" size="+2">mspgcc</FONT></B>'
        #return '<B><FONT color="#ff0000>mspgcc</FONT></B>'

    def get_body(self):
        self.__grokbody()
        return self.__body

    def get_body_attributes(self):
        return 'MARGINWIDTH="0" MARGINHEIGHT="0" TOPMARGIN="0" LEFTMARGIN="0"'

    def get_cont(self):
        self.__grokbody()
        return self.__cont

    def __grokbody(self):
        if self.__body is None:
            text = self.__parser.fp.read()
            text = self.__inliner(text)
            i = text.find('<!--table-stop-->')
            if i >= 0:
                self.__body = text[:i]
                self.__cont = text[i+17:]
            else:
                # there is no wide body
                self.__body = text
        self.__body = self.__body + "<br>"*3

    def get_style(self):
        extstyle = self.__parser.get("css", None)
        if extstyle:
            return '<LINK href="%s" rel="stylesheet" type="text/css">' % extstyle
        else:
            return '<style type="text/css">body { margin:0 }</style>'

    def get_lightshade(self):
        """Return lightest of 3 color scheme shade."""
        return '#55aaff'

    def get_mediumshade(self):
        """Return middle of 3 color scheme shade."""
        return '#2277dd'

    def get_darkshade(self):
        """Return darkest of 3 color scheme shade."""
        return '#0055aa'

    def get_corner_bgcolor(self):
        return self.get_mediumshade()
