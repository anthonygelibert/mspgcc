# Make rules for mspgcc.sf.net ht->html generation.  SOURCES
# indirection filters out "*.ht" value when no ht files are around.
THEUSER = $(shell cat username)

SOURCES =	$(shell echo *.ht)
TARGETS =	$(filter-out *.html,$(SOURCES:%.ht=%.html)) $(EXTRA_TARGETS)
GENERATED_HTML= $(SOURCES:.ht=.html)

HTROOT = 	.
HT2HTML =	ht2html/ht2html.py
HTSTYLE =	mspgccGenerator
HTALLFLAGS =	-f -s $(HTSTYLE)
HTFLAGS =	$(HTALLFLAGS) -r $(HTROOT)

DEST = 		$(THEUSER):/home/groups/m/ms/mspgcc/htdocs
CGIDEST = 	$(THEUSER):/home/groups/m/ms/mspgcc/cgi-bin
EXCLUDES =	--exclude=CVS --exclude=cgi-bin --exclude=ht2html --exclude=manual --exclude=faq --exclude=username --exclude=\*.ht
CGIEXCLUDES =	--exclude=CVS --exclude=not_the_real_cgi_here.txt
RARGS = 	--rsh=ssh -v -r -l -t --update --delete $(EXCLUDES)
XMLRARGS = 	--rsh=ssh -v -r -l -t --update --delete
CGIRARGS = 	--rsh=ssh -v -r -l -t --update --delete $(CGIEXCLUDES)

.SUFFIXES:	.ht .html

.ht.html:
	$(HT2HTML) $(HTFLAGS) $<

all: $(TARGETS)

#dependencies for the ht files
$(TARGETS): links.h doc_links.h

clean:
	-rm -f *~
	-rm $(GENERATED_HTML)

install: docinstall cgiinstall

docinstall: all
	rsync $(RARGS) . $(DEST)

cgiinstall:
	rsync $(CGIRARGS) cgi-bin/ $(CGIDEST)

xmlinstall:
	#~ cd ../docs; make
	rsync $(XMLRARGS) ../docs/faq/ $(DEST)/faq
	rsync $(XMLRARGS) ../docs/manual/ $(DEST)/manual

username:
	echo $(USER)@mspgcc.sf.net >$@