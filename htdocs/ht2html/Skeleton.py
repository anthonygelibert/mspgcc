"""Skeleton class.

Should be sub-classed to provide basic generation of able-contained HTML
document.
"""

from ht2html import __version__

import sys
import time
from cStringIO import StringIO


class Skeleton:
    #
    # for sub-classes to override
    #

    def get_banner(self):
        """Returns HTML for the top banner, or None if no banner.
        """
        return None

    def get_left_sidebar(self):
        """Returns HTML for the left sidebar or None.
        """
        return None
    # for backwards compatibility
    get_sidebar = get_left_sidebar

    def get_right_sidebar(self):
        """Returns HTML for the right sidebar or None.
        """
        return None

    def get_banner_width(self):
        """HTML `width' of banner column as a percentage.

        Should be a string that does not include the percent sign (e.g. "90").
        This affects the column containing both the banner and body text (if
        they exist).
        """
        return '90'

    def get_corner(self):
        """Returns HTML for the upper-left corner or None.

        Note that if get_banner() and get_sidebar() both return None, then
        get_corner() is ignored.  Also if both get_banner() and get_sidebar()
        return a string, but get_corner() returns None, the smallest blank
        corner possible is emitted.
        """
        return None

    def get_body(self):
        """Returns HTML for the internal document body.

        Note that using this method causes the get_sidebar() -- if there is
        one -- to run the full height of the page.  If you don't want this,
        then make sure get_cont() returns a string.
        """
        return '<b>Intentionally left blank</b>'

    def get_cont(self):
        """Returns HTML for the continuation of the body.

        When this method returns a string, and there is a get_sidebar(), the
        continuation text appears below the get_sidebar() and get_body() at
        the full width of the screen.  If there is no get_sidebar(), then
        having a get_cont() is pointless.
        """
        return None

    def get_title(self):
        """Return the title of the page.  Required."""
        return 'Intentionally left blank'

    def get_meta(self):
        """Return extra meta-data.  Must be a string."""
        return ''

    def get_headers(self):
        """Return extra header information.  Must be a string."""
        return ''

    def get_bgcolor(self):
        """Return the background color"""
        return '#ffffff'

    def get_fgcolor(self):
        """Return foreground color"""
        return '#000000'

    def get_linkcolor(self):
        """Return link color"""
        return '#0000bb'

    def get_vlinkcolor(self):
        """Return vlink color"""
        return '#551a8b'

    def get_alinkcolor(self):
        """Return alink color"""
        return '#ff0000'

    def get_corner_bgcolor(self):
        """Return the background color for the corner"""
        return self.get_lightshade()

    # Barry's prefs
    def get_lightshade(self):
        """Return lightest of 3 color scheme shade."""
        return '#cdba96'

    def get_mediumshade(self):
        """Return middle of 3 color scheme shade."""
        return '#cc9966'

    def get_darkshade(self):
        """Return darkest of 3 color scheme shade."""
        return '#b78900'

    def get_body_attributes(self):
        """Return extra attributes for the body start tag."""
        return ''

    def get_banner_attributes(self):
        """Return extra attributes for the TABLE in the banner."""
        return 'CELLSPACING=0 CELLPADDING=2'

    def get_charset(self):
        """Return charset of pages"""
        return 'us-ascii'

    # Style sheets
    def get_style(self):
        """Return the style sheet for this document"""
        return '<style type="text/css">body { %s }</style>\n' % self.body_style()

    def body_style(self):
        return 'margin:0;'

    # Call this method
    def makepage(self):
        banner = self.get_banner()
        sidebar = self.get_sidebar()
        corner = self.get_corner()
        body = self.get_body()
        cont = self.get_cont()
        html = StringIO()
        stdout = sys.stdout
        closed = 0
        try:
            sys.stdout = html
            self.__do_head()
            self.__start_body()
            print '<!-- start of page table -->'
            print '<TABLE WIDTH="100%" BORDER=0 CELLSPACING=0 CELLPADDING=0>'
            if banner is not None:
                print '<!-- start of banner row -->'
                print '<TR>'
                if corner is not None:
                    self.__do_corner(corner)
                print '<!-- start of banner -->'
                print '<TD WIDTH="%s%%" BGCOLOR="%s">' % (
                    self.get_banner_width(), self.get_lightshade())
                print banner
                print '</TD><!-- end of banner -->'
                print '</TR><!-- end of banner row -->'
            # if there is a body but no sidebar, then we'll just close the
            # table right here and put the body (and any cont) in the full
            # page.  if there is a sidebar but no body, then we still create
            # the new row and just populate the body cell with a non-breaking
            # space.  Watch out though because we don't want to close the
            # table twice
            if sidebar is None:
                print '</TABLE><!-- end of page table -->'
                closed = 1
            else:
                print '<TR><!-- start of sidebar/body row -->'
                self.__do_sidebar(sidebar)
            if body is not None:
                if closed:
                    print body
                else:
                    self.__do_body(body)
            if not closed:
                print '</TR><!-- end of sidebar/body row -->'
                print '</TABLE><!-- end of page table -->'
            if cont is not None:
                self.__do_cont(cont)
            self.__finish_all()
        finally:
            sys.stdout = stdout
        return html.getvalue()

    def __do_corner(self, corner):
        print '<!-- start of corner cells -->'
        print '<TD WIDTH=150 VALIGN=MIDDLE BGCOLOR="%s">' % (
            self.get_corner_bgcolor())
        # it is important not to have a newline between the corner text and
        # the table close tag, otherwise layout is messed up
        if corner is None:
            print '&nbsp;',
        else:
            print corner,
        print '</TD>'
        print '<TD WIDTH=15 BGCOLOR="%s">&nbsp;&nbsp;</TD><!--spacer-->' % (
            self.get_lightshade())
        print '<!-- end of corner cells -->'

    def __do_sidebar(self, sidebar):
        print '<!-- start of sidebar cells -->'
        print '<TD WIDTH=150 VALIGN=TOP BGCOLOR="%s">' % (
            self.get_lightshade())
        print sidebar
        print '</TD>'
        print '<TD WIDTH=15>&nbsp;&nbsp;</TD><!--spacer-->'
        print '<!-- end of sidebar cell -->'

    def __do_body(self, body):
        print '<!-- start of body cell -->'
        print '<TD VALIGN=TOP WIDTH="%s%%"><BR>' % (
            self.get_banner_width())
        print body
        print '</TD><!-- end of body cell -->'

    def __do_cont(self, cont):
        print '<!-- start of continued wide-body text -->'
        print cont
        print '<!-- end of continued wide-body text -->'

    def __do_head(self):
        """Return the HTML <head> stuff."""
        print '''\
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN">
<HTML>
<!-- THIS PAGE IS AUTOMATICALLY GENERATED.  DO NOT EDIT. -->
<!-- %(time)s -->
<!-- USING HT2HTML %(version)s -->
<!-- SEE http://ht2html.sf.net -->
<!-- User-specified headers:
Title: %(title)s
%(headers)s
-->

<HEAD>
<TITLE>%(title)s</TITLE>
<META HTTP-EQUIV="Content-Type" CONTENT="text/html; charset=%(charset)s">
%(meta)s
%(style)s
</HEAD>''' % {'title'  : self.get_title(),
              'headers': self.get_headers(),
              'meta'   : self.get_meta(),
              'time'   : time.ctime(time.time()),
              'version': __version__,
              'charset': self.get_charset(),
              'style'  : self.get_style()
              }

    def __start_body(self):
        print '''\
<BODY BGCOLOR="%(bgcolor)s" TEXT="%(fgcolor)s"
      %(extraattrs)s
      LINK="%(linkcolor)s"  VLINK="%(vlinkcolor)s"
      ALINK="%(alinkcolor)s">''' % {
            'bgcolor'   : self.get_bgcolor(),
            'fgcolor'   : self.get_fgcolor(),
            'linkcolor' : self.get_linkcolor(),
            'vlinkcolor': self.get_vlinkcolor(),
            'alinkcolor': self.get_alinkcolor(),
            'extraattrs': self.get_body_attributes(),
            }

    def __finish_all(self):
        print '</BODY></HTML>'



# test script
class _Skeleton(Skeleton):
    def get_banner(self):
        return '<b>The Banner</b>'

    def get_sidebar(self):
        return '''<ul><li>Sidebar line 1
        <li>Sidebar line 2
        <li>Sidebar line 3
        </ul>'''

    def get_corner(self):
        return '<center><em>CORNER</em></center>'

    def get_body(self):
        return 'intentionally left blank ' * 110

    def get_cont(self):
        return 'wide stuff ' * 100

    def get_corner_bgcolor(self):
        return 'yellow'

    def get_banner_width(self):
        return "80"


if __name__ == '__main__':
    t = _Skeleton()
    print t.makepage()
