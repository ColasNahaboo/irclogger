Irclogger installation
======================
IRC Logger python bot, http://colas.nahaboo.net/Software/IrcLogger

You will need to define 3 places:
   BIN (dir) where to put the CGI web executables and config file
   LOG (dir) where the logs will be stored (ideally out of the web space)
	     and optional html+css style files
   PASS (file) where is the apache passwords file for the channels
and the URL where BIN will be visible from the web
and optionally the CHANNEL to log on startup.

It is developed on linux, should work on all unixes (maybe with the various
utilities such as grep, sed,... in their GNU variants), may work on cygwin.

Quick Install:
==============
uncompress irclogger somewhere (/usr/local/irclogger is the default dir, so 
go to /usr/local, and uncompress the distribution there)
go to this dir
run: ./install BIN LOG PASS URL CHANNEL
follow the instructions.

You need to have agrep installed on your system (http://www.tgries.de/agrep/)
It should work with any 2.x python.

PS: to find quickly where irclogger has been installed on a machine, do
a "locate" to find files irclogger.log (for LOG) and irclogger.conf (for BIN)

Upgrade:
========
Due to the installation using symbolic links, upgrade is a breeze:
  [1] uncompress the distribution where you installed it (default: /usr/local)
  [2] check the HISTORY for other manual upgrade steps, if any
  [3] if the HISTORY says that "irclogger" changed, kill its running 
      instances, you can find them by: 
	   ps awx|grep 'python.*[i]rclogger'
      If you run it via an irclogger-run based script, they will be restarted
      automatically in 45s

Note: major versions (1.4, 1.5...) means that the irclogger python bot has
changed and that you should restart it. Minor versions (1.5a, 1.5b...) means
that only the doc or the cgi scripts have changed, so only step [1] should be
performed. Version of irclogger is specified at the head of irclogger and will
never be minor, version of the rest is in the HISTORY file.

Details:
========

irclogger.conf
--------------
in the BIN directory of the web server
Contains the path of the irclogger main LOG dir (logsdir). Each subdir in it
indicates that a channel of this name is logged.
syntax is bash variable declarations, and can be:

logsdir=/var/log/irclogger
passfile=/var/www/passwds/irclogger-passwds
private_image="${private_image:-<img src='http://colaz.net/qbullets/private.gif' width=11 height=10 alt='Password-protected log'>}"
top=URL where the upmost "back" link will bring the user

In the irclogger_dir LOG, one can put files:
   style.css  that will be included in all html pages
   message.html will be included at the top of the html index page

LOG must be read&writable by the UID you run the irclogger daemon
and readable by the web server UID
You should do in it:
echo 'deny from all' >.htaccess

Logs are in LOG/CHANNEL/YYYY-MM-DD,Day.log
Logs can be passord-protected by users from the web interface, except
     if a file named "PUBLIC" exists in its dir. Users cannot remove
     the protection (A channel log is protected if a user of the name of the
     channel exists in PASS)

In the Logs dir, you can create a file CHANNELS.deny to limit the logger to
log only the channel names (without the #, space-separated on one line) in it,
as some IRC servers limits the number of channels a single bot can monitor,
often 5.

passfile (aka PASS) must be web-server writable htpasswd file, and must exist

Logs can be compressed/decompressed at anytime via gzip. listing and searching
will work transparently with compressed files. If any file is compressed, the
search program will create a expansed mirror of all the logs in LOG/.exp that
should be created writable by the web server UID on installation

to run:
======

copy irclogger-run in /usr/local/bin, edit it, and run it once at startup,
via start-stop-daemon for instance. Copy it under as many copies as you want
to run separate irclogger bots.

On web server:
==============

With a web ScriptAlias dir BIN where you have "AllowOverride All" 
permissions, do:

then:
  S=/usr/local/irclogger
  cd $S
  cp htaccess.sample $BIN/.htaccess
  ln -fs $S/irclogger_* $S/nph-irclogger_reset_auth $BIN

  create a $BIN/irclogger.conf

  cd $BIN
  for i in logs password log log_search 
  do ln -s irclogger_${i} irclogger_${i}_a; done
  # Edit first line of $DIR/.htaccess to reflect $PASS value

  . irclogger.conf; touch $PASS;chmod a+rw $PASS

On your web pages, Call by something like:
<a href='/cgi-bin/irclogger_logs/XXX'>IRC log for channel #XXX</a>

-----------------------------------------------------------------------------

Implementation:
===============

This system is made of scripts running under linux and apache. It should run
on any similar system, such as cygwin on windows systems, but needs the GNU
version of unix tools (date, grep, sed...), not the old SYSV or BSD ones.


irclogger [python]
    Uses ircAsync.py. This script runs the robot
    which connects to channels and dumps logs in text form (MIRC format)
    in $LOG/logs dir
    The rest are shell (bash) scripts.

irclogger-run [bash]
    Is a sample sript to see how to run irclogger. It provides parameters,
    and restarts it on termnination (ircloggers quits in case of
    deconnection)

irclogger_tohtml [bash]
    irclogger_tohtml channel date selected < log
    
    Pretty-prints the channel log. If the channel log dir contains a file named
    "style.css", appends it to the current style (found in the parent dir).
    Possible classes of elements are:
        tr.even  the even rows
        tr.odd   the odd rows
        tr.sep   the separator rows (no messages for more than an hour)
        tr.irc   the control messages
        tr.selected the selection
    selected can be set to a line number to highlight
    If a style.css file is defined, it replaces the one built-in in 
    irclogger_tohtml in var DEFSTYLE

irclogger_totml [bash]
    irclogger_totml channel date selected < log
    Pretty-prints in a text form incluable in Wikis using the TML markup
    (Topic Markup Language), see http://foswiki.org/System/TextFormattingRules
    TML is used by Foswiki and TWiki

irclogger_totext [bash]
    irclogger_totext channel date selected < log
    prints only the contents without control messages and nicknames
    useful for getting meeting notes by a single scribe + correcters

irclogger_logs [bash, cgi]
    irclogger_logs/channel
    lists all available days in channel
    if a file message.html exists in the log dir it will be included at top

irclogger_log [bash, cgi]
    irclogger_log/channel?date=date&raw=on%sel=linenum

irclogger_log_search [bash, cgi]
    irclogger_log_search/channel...

irclogger_log_style [bash, cgi]
    irclogger_log_style channel
    generates a CSS for a channel with a color per active name

nph-irclogger_reset_auth [bash, cgi]
    used to reset the apache authentication to allow login on another
    protected channel

irclogger_password [bash, cgi]
    used to change/set passwords in the PASS file

irclogger_common [bash]
    a library of common functions used by the scripts

style.css [css]
    a sample CSS file to use to have a nicer look
