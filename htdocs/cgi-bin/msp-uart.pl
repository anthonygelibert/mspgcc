#!/usr/bin/perl

# msp-uart.cgi -- calculates the uart registers for MSP430
#
# Copyright (C) 2002 - Pedro Zorzenon Neto - pzn dot debian dot org
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
# You can download a copy of the license at
# http://www.fsf.org/licenses/licenses.html#GPL

if ( ($ENV{'REQUEST_METHOD'} eq 'GET') ||
     ($ENV{'REQUEST_METHOD'} eq 'HEAD') ) {
    $cgi= $ENV{'QUERY_STRING'} ;
} elsif ($ENV{'REQUEST_METHOD'} eq 'POST') {
    read(STDIN, $cgi, $ENV{'CONTENT_LENGTH'}) ;
}
foreach (split('&', $cgi)) {
    s/\+/ /g ;
    ($name, $value)= split('=', $_, 2) ;
    $cgi{$name}.= $value ;
}

$xt=$cgi{"clock"}+0;
$br=$cgi{"baud"}+0;

print "Content-type: text/plain\n\n";

if ($xt<=0) { print "ERROR: clock <= 0\n"; exit 0; }
if ($br<=0) { print "ERROR: baud <= 0\n"; exit 0; }
$div=int($xt/$br); $t=(1/$br);
for ($mod=0; $mod<256; $mod++) {
    $real=0;
    for ($i=1; $i<11; $i++) {
        $j=$i-1; if ($j>7) { $j-=8; }
        $k=1<<$j; $l=$k&$mod;
        if ($l==0) { $modb=0; } else { $modb=1; }
        $real=1/($xt/($div+$modb))+$real;
        $ideal=($i*$t);
        $erro=abs($real-$ideal);
        if ($i==1) {
            $max=$erro; $min=$erro;
        } else {
            if ($erro>$max) { $max=$erro; }
            if ($erro<$min) { $min=$erro; }
        }
    }
    if ($mod==0) {
        $gmax=$max; $gmin=$min; $gmaxi=$mod; $gmini=$mod;
    } else {
        if ($gmax>$max) { $gmax=$max; $gmaxi=$mod; }
    }
}
print "/* uart calculator: http://igbt.sel.eesc.sc.usp.br/~pzn/\n";
print "   clock: $xt"."Hz\n";
print "   baud rate: $br"."bps\n";
$porc=100*($gmax/$t); $gmax*=1000000;
printf("   maxerr:%6.3fus %4.2f\% */\n",$gmax,$porc);
printf("UBR00=0x%02X; UBR10=0x%02X; UMCTL0=0x%02X; // uart 0\n",$div&0xff,($div&0xfff00)>>8,$gmaxi);
printf("UBR01=0x%02X; UBR11=0x%02X; UMCTL1=0x%02X; // uart 1\n",$div&0xff,($div&0xfff00)>>8,$gmaxi);
if ($div>0xffff) { print "ERROR: this baud rate is impossible... div > 0xffff\n"; }
