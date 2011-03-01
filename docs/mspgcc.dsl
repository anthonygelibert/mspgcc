<!DOCTYPE style-sheet PUBLIC "-//James Clark//DTD DSSSL Style Sheet//EN" [
    <!ENTITY % html "IGNORE">
    <![%html;[
        <!ENTITY % print "IGNORE">
        <!ENTITY docbook.dsl PUBLIC "-//Norman Walsh//DOCUMENT DocBook HTML Stylesheet//EN" CDATA dsssl>
    ]]>
    
    <!ENTITY % print "INCLUDE">
    <![%print;[
        <!ENTITY docbook.dsl PUBLIC "-//Norman Walsh//DOCUMENT DocBook Print Stylesheet//EN" CDATA dsssl>
    ]]>
]>

<style-sheet>

<style-specification id="html" use="docbook">
<style-specification-body>

<!-- DSSSL for HTML output goes here  -->

</style-specification-body>
</style-specification>

<style-specification id="print" use="docbook">
<style-specification-body>

<!-- DSSSL for print output, i.e., TeX, RTF, MIF, goes here  -->
(declare-characteristic heading-level 
   "UNREGISTERED::James Clark//Characteristic::heading-level" 2)
(define %generate-heading-level% #t)

(define %paper-type% "A4")

(define %two-side% #t)

<!-- 
(declare-characteristic page-two-side?
    "UNREGISTERED::OpenJade//Characteristic::page-two-side?"
    #t)
-->

</style-specification-body>
</style-specification>

<external-specification id="docbook" document="docbook.dsl">

</style-sheet>
