# Make rules for mspgcc.sf.net ht->html generation.  SOURCES
# indirection filters out "*.ht" value when no ht files are around.
THEUSER = cliechti@mspgcc.sf.net

SOURCES =	$(shell echo *.ht)
TARGETS =	$(filter-out *.html,$(SOURCES:%.ht=%.html)) $(EXTRA_TARGETS)
GENERATED_HTML= $(SOURCES:.ht=.html)

HTROOT = 	.
HT2HTML =	D:/prog/python/_thirdparty/ht2html/ht2html.py
HTSTYLE =	mspgccGenerator
HTALLFLAGS =	-f -s $(HTSTYLE)
HTFLAGS =	$(HTALLFLAGS) -r $(HTROOT)

DEST = 		$(THEUSER):/home/groups/m/ms/mspgcc/htdocs
CGIDEST = 	$(THEUSER):/home/groups/m/ms/mspgcc/cgi-bin
EXCLUDES =	--exclude=CVS --exclude=cgi-bin
CGIEXCLUDES =	--exclude=CVS
ARGS = 		--rsh=ssh -v -r -l -t --update --delete $(EXCLUDES)
CGIARGS = 	--rsh=ssh -v -r -l -t --update --delete $(CGIEXCLUDES)

.SUFFIXES:	.ht .html

.ht.html:
	$(HT2HTML) $(HTFLAGS) $<

all: $(TARGETS)

$(TARGETS): links.h

clean:
	-rm -f *~
	-rm $(GENERATED_HTML)

install: docinstall cgiinstall

docinstall: all
	rsync $(ARGS) . $(DEST)

cgiinstall:
	rsync $(CGIARGS) cgi-bin/ $(CGIDEST)
