.PHONY: all html pdf manual-html faq-html faq-pdf manual-pdf clean clean-workfiles

all:  html pdf
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

clean: clean-workfiles
	rm -f mspgcc-manual.pdf faq.pdf
	rm -f faq/* manual/*
	rmdir -f faq manual
