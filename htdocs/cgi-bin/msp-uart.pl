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
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA
#
# You can download a copy of the license at
# http://www.fsf.org/licenses/licenses.html#GPL

# cgi or command line usage?
$cgi=1;

sub mod_bit {
  my ($bit,$byte)=@_;
  $byte&=0xff;
  $byte=$byte+($byte<<8);
  if (((1<<$bit) & $byte) != 0) {
    return 1;
  } else {
    return 0;
  }
}

if ($cgi==1) {
  # using it as a cgi script
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
} else {
  # using it as a command line program.
  if (($ARGV[0] eq "") || ($ARGV[1] eq "")) {
    print "Usage: msp-uart.pl baudrate clock\n";
    print "  example: msp-uart.pl 115200 4000000\n";
    exit 1;
  }
  $br=$ARGV[0]+0;
  $xt=$ARGV[1]+0;
}

if ($xt<=0) { print "ERROR: clock <= 0\n"; exit 0; }
if ($br<=0) { print "ERROR: baud <= 0\n"; exit 0; }
$div=int($xt/$br); $t=(1/$br);
$gdiv=-1;

for ($div=(int($xt/$br)-1); $div<=(int($xt/$br)+1); $div++) {
  if ($div<1) { $div=1; } # assure limit
  if ($div>0xffff) { $div=0xffff; } # assure limit
  
  for ($mod=0x00; $mod<=0xff; $mod++) {
    # test all modulator combinations and check which one has
    # the lower error.
    
    $effective=0; # the effective time
    $desired=0; # the desired time (perfect clock, no errors)

    for ($i=0; $i<10; $i++) { # startbit + 8 bits + stopbit = 10bits

      $effective+=1/($xt/($div+mod_bit($i,$mod)));
      $desired+=$t;
      $error=abs($effective-$desired);

      if ($i==0) {
	# reset max bit error variable
	$max=$error;
      }

      # if this bit is worse then previous ones, store its error
      if ($error>$max) { $max=$error; }

    }

    if ($gdiv==-1) {
      # reset max global error variables
      $gmax=$max; $gmaxi=$mod; $gdiv=$div;
    }

    # store this values if result is better then previous mod values
    if ($max<$gmax) { 
      $gmax=$max; $gmaxi=$mod; $gdiv=$div}

    if (($mod==0xfe) && ($div!=0xffff)) { $mod++; }

  }
  if ($div==0xffff) { $div=(int($xt/$br)+1); } # will get out of for loop
}

# calculate effective division with final values
$div=0;
for ($i=0; $i<10; $i++) { # startbit + 8 bits + stopbit = 10bits
  $div+=$gdiv+mod_bit($i,$gmaxi);
}
$div/=10;

print  "/*\n";
print  "  uart calculator: http://mspgcc.sourceforge.net/baudrate.html\n";
print  "  this program license is at: http://www.fsf.org/".
  "licenses/licenses.html\#GPL\n";
print  "  this program is distributed WITHOUT ANY WARRANTY\n";
print  "\n";
print  "  clock: $xt"."Hz\n";
print  "  desired baud rate: $br"."bps\n";
printf("  division factor: %g\n",$div);
printf("  effective baud rate: %gbps\n",$xt/$div);
$gmax=int($gmax*1e10)/1e10;
printf("  maximum error: %gus %6.2f%%\n",$gmax*1000000,100*$gmax/$t);
print  "\n";

print  "  time table (microseconds):\n";
print  "        event      desired effective  error   error\%\n";
$effective=0; $desired=0;

$effective+=1/($xt/($gdiv+mod_bit(0,$gmaxi))); $desired+=$t;
$err=($desired-$effective); $err=int($err*1e10)/1e10;
printf "    startbit->D0 %9.2f %9.2f  %+7.3g %+6.2f\n",
  $desired*1000000,$effective*1000000,$err*1000000,$err*100/$t;

$effective+=1/($xt/($gdiv+mod_bit(1,$gmaxi))); $desired+=$t;
$err=($desired-$effective); $err=int($err*1e10)/1e10;
printf "    D0->D1       %9.2f %9.2f  %+7.3g %+6.2f\n",
  $desired*1000000,$effective*1000000,$err*1000000,$err*100/$t;

$effective+=1/($xt/($gdiv+mod_bit(2,$gmaxi))); $desired+=$t;
$err=($desired-$effective); $err=int($err*1e10)/1e10;
printf "    D1->D2       %9.2f %9.2f  %+7.3g %+6.2f\n",
  $desired*1000000,$effective*1000000,$err*1000000,$err*100/$t;

$effective+=1/($xt/($gdiv+mod_bit(3,$gmaxi))); $desired+=$t;
$err=($desired-$effective); $err=int($err*1e10)/1e10;
printf "    D2->D3       %9.2f %9.2f  %+7.3g %+6.2f\n",
  $desired*1000000,$effective*1000000,$err*1000000,$err*100/$t;

$effective+=1/($xt/($gdiv+mod_bit(4,$gmaxi))); $desired+=$t;
$err=($desired-$effective); $err=int($err*1e10)/1e10;
printf "    D3->D4       %9.2f %9.2f  %+7.3g %+6.2f\n",
  $desired*1000000,$effective*1000000,$err*1000000,$err*100/$t;

$effective+=1/($xt/($gdiv+mod_bit(5,$gmaxi))); $desired+=$t;
$err=($desired-$effective); $err=int($err*1e10)/1e10;
printf "    D4->D5       %9.2f %9.2f  %+7.3g %+6.2f\n",
  $desired*1000000,$effective*1000000,$err*1000000,$err*100/$t;

$effective+=1/($xt/($gdiv+mod_bit(6,$gmaxi))); $desired+=$t;
$err=($desired-$effective); $err=int($err*1e10)/1e10;
printf "    D5->D6       %9.2f %9.2f  %+7.3g %+6.2f\n",
  $desired*1000000,$effective*1000000,$err*1000000,$err*100/$t;

$effective+=1/($xt/($gdiv+mod_bit(7,$gmaxi))); $desired+=$t;
$err=($desired-$effective); $err=int($err*1e10)/1e10;
printf "    D6->D7       %9.2f %9.2f  %+7.3g %+6.2f\n",
  $desired*1000000,$effective*1000000,$err*1000000,$err*100/$t;

$effective+=1/($xt/($gdiv+mod_bit(8,$gmaxi))); $desired+=$t;
$err=($desired-$effective); $err=int($err*1e10)/1e10;
printf "    D7->stopbit  %9.2f %9.2f  %+7.3g %+6.2f\n",
  $desired*1000000,$effective*1000000,$err*1000000,$err*100/$t;

$effective+=1/($xt/($gdiv+mod_bit(9,$gmaxi))); $desired+=$t;
$err=($desired-$effective); $err=int($err*1e10)/1e10;
printf "    end of stopb %9.2f %9.2f  %+7.3g %+6.2f\n",
  $desired*1000000,$effective*1000000,$err*1000000,$err*100/$t;

print "*/\n";
printf("UBR00=0x%02X; UBR10=0x%02X; UMCTL0=0x%02X; /* uart0 %iHz %ibps */\n",
       $gdiv&0xff,($gdiv&0xfff00)>>8,$gmaxi,
       $xt,$xt/$div);
printf("UBR01=0x%02X; UBR11=0x%02X; UMCTL1=0x%02X; /* uart1 %iHz %ibps */\n",
       $gdiv&0xff,($gdiv&0xfff00)>>8,$gmaxi,
       $xt,$xt/$div);
exit 0;
