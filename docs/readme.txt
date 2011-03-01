Documentation on Documentation
------------------------------
The XML files contain the DocBook sources for the Manual and FAQ.
They are converted to HTML and can be found on the homepage
http://mspgcc.sf.net
The makefile also contains rules to build PDFs from these files.

Build overview
--------------
"openjade" is a jade implementation that can convert docbook XML sources
to different output formats. "jw" is a wrapper for call to jade/openjade
and "docbook2html" as well as "docbook2tex" are in turn wrappers to "jw".

That in mind we can simply call
$ docbook2html -o faq faq.xml
and get a ready made HTML documentation in the faq folder.

For the PDF docs it's slightly more complicated. We use two steps here.
First a TeX source file has to generated:
$ docbook2tex --dsl mspgcc.dsl#print mspgcc-manual.xml

The --dsl option loads a customization file for the jade processor. It
contains instructions for page size, double sided print and that the PDF
bookmark are generated (the dsl file could have options for html too, but
we currently do not use them).

Then that .tex file can be converted to PDF using 
$ pdfjadetex mspgcc-manual.tex

TeX is a single pass "compiler" so that indexes, table of contents (TOC) and such
use the page number of the *last* run. That means that we have to run it three
times to get correct page numbers. (1st pass with empty TOC, 2nd pass with correct
sized TOC but wrong page numbers as the TOC now uses more space on the page and
shifts down other contents, 3rd pass with correct TOC and page numbers)

"jadepdftex" can be customized with a jadetex.cfg file in the working directoty. We
use that to set TeX options, such as PDF author, bookmark expansion on startup, etc.

Files
-----
*.xml           DocBook XML sources "book" style
jadetex.cfg     TeX source, customizations for jadepdftex.
mspgcc.dsl      DSSSL Style Sheet for Jade, XML format.
makefile        Build commands for HTML and PDF docs

Requirements
------------

The following packages are required to run the makefile.

* Debian GNU/Linux
    apt-get install docbook
    apt-get install docbook-utils
    apt-get install openjade
    apt-get install jadetex

Do *not* install "jade". "openjade" provides a replacment that can also do the
PDF bookmarks, which the former can't. The docbook-utils such as "pdfjadetex"
autodetect jade and would take "jade" if it's installed.

Links
-----
http://www.docbook.org/tdg/en/html/docbook.html

http://docbook.sourceforge.net/
http://docbook.sourceforge.net/release/dsssl/current/doc/

http://www.dpawson.co.uk/docbook/index.html
http://www.dpawson.co.uk/docbook/dsssl/dssslpdf.html
