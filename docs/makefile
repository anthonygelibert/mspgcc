.PHONY: all html pdf manual-html faq-html faq-pdf manual-pdf clean clean-workfiles FORCE

ifdef WINDIR
STYLESHEET := "$(shell cygpath -w `pwd`)/stylesheet.css"
else
STYLESHEET := "$(shell pwd)/stylesheet.css"
endif
RST2HTML = python -c "from docutils.core import publish_cmdline; publish_cmdline(writer_name='html')"
HTMLOPT  = --stylesheet=$(STYLESHEET)

%.html: %.txt stylesheet.css
	$(RST2HTML) $(HTMLOPT) $< $@

all: documentation.html
#~ info.html tutorial.html

dookbook-stuff: html pdf
html: manual-html faq-html
pdf:  manual-pdf faq-pdf

manual-html:
	docbook2html -o manual mspgcc-manual.xml

faq-html:
	docbook2html -o faq faq.xml


faq-pdf:
	docbook2tex --dsl mspgcc.dsl#print faq.xml
	#run tex 3 times so that page numbers match (TeX feature ;-)
	pdfjadetex faq.tex
	pdfjadetex faq.tex >/dev/null
	pdfjadetex faq.tex >/dev/null

manual-pdf:
	docbook2tex --dsl mspgcc.dsl#print mspgcc-manual.xml
	#run tex 3 times so that page numbers match (TeX feature ;-)
	pdfjadetex mspgcc-manual.tex
	pdfjadetex mspgcc-manual.tex >/dev/null
	pdfjadetex mspgcc-manual.tex >/dev/null

clean-workfiles:
	rm -f mspgcc-manual.aux mspgcc-manual.log mspgcc-manual.out mspgcc-manual.tex
	rm -f faq.aux faq.log faq.out faq.tex

htmldir:
	mkdir -p html

faq-eclipse: FORCE htmldir
	xsltproc --stringparam base.dir html/faq/ --stringparam html.stylesheet ../styles.css /usr/share/xml/docbook/stylesheet/nwalsh/eclipse/eclipse.xsl faq.xml
	mv toc.xml toc-faq.xml

manual-eclipse: FORCE htmldir
	xsltproc --stringparam base.dir html/manual/ --stringparam html.stylesheet ../styles.css /usr/share/xml/docbook/stylesheet/nwalsh/eclipse/eclipse.xsl mspgcc-manual.xml
	mv toc.xml toc-manual.xml

clean: clean-workfiles
	rm -f documentation.html
	rm -f mspgcc-manual.pdf faq.pdf
	rm -rf faq manual

FORCE:
