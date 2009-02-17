#!/usr/bin/python
"""

ircAsync -- An asynchronous IRC client interface.

This is intended as a component in a semantic web agent
with several interfaces, one of them being IRC.
It's implemented on top of asyncore so that the same
agent can export an HTTP interface in asynchronous,
non-blocking style.

see Log at end for recent changes/status info.

Share and Enjoy. Open Source license:
Copyright (c) 2001 W3C (MIT, INRIA, Keio)
http://www.w3.org/Consortium/Legal/copyright-software-19980720

$Id: ircAsync.py,v 1.9 2003/09/13 colas Exp $
"""

# asyncore -- Asynchronous socket handler 
# http://www.python.org/doc/current/lib/module-asyncore.html

import string, re
import socket
import asyncore, asynchat
import os



#RFC 2811: Internet Relay Chat: Client Protocol
#2.3 Messages
# http://www.valinor.sorcery.net/docs/rfc2812/2.3-messages.html
SPC="\x20"
CR="\x0d"
LF="\x0a"
CRLF=CR+LF
Port = 6667

# commands...
PRIVMSG = 'PRIVMSG'
NOTICE = 'NOTICE'
PING='PING'
PONG='PONG'
USER='USER'
NICK='NICK'
PASS='PASS'
JOIN='JOIN'
PART='PART'
INVITE='INVITE'
QUIT='QUIT'

# reply codes...
RPL_WELCOME='001'
TOPIC='332'
TOPICINFO='333'

class T(asynchat.async_chat):
    def __init__(self):
        asynchat.async_chat.__init__(self)
        self.bufIn = ''
        self.set_terminator(CRLF)

        # public attributes
        # no blanks in nick.
        # openprojects.net says:
        # Connect with your real username, in lowercase.
        # If your mail address were foo@bar.com, your username would be foo.
        # other limitations? @@see IRC RFC?"""

        self.nick = 'ircAsync' # manage this with __getattr__() in stead? hmm...
        self.userid = 'nobody'
        self.fullName = 'ircAsync user'
        self._startChannels = ['#test']
        self._dispatch = []
        self._doc = []
        
    def makeConn(self, host, port):
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        #debug("connecting to...", host, port)
        self.passwd = os.getenv('IRC_SERVER_PASSWORD')
        self.connect((host, port))

        self.bufIn = ''

    def todo(self, args, *text):
        command = string.join(args)
        if text: command = command + ' :' + string.join(text)

        self.push(command + CRLF)
        #debug("sent/pushed command:", command)

    # asyncore methods
    def handle_connect(self):
        #debug("connected")

        #@@ hmm... RFC says mode is a bitfield, but
        # irc.py by @@whathisname says +iw string.
        if self.passwd:
            self.todo([PASS, self.passwd])
        self.todo([NICK, self.nick])
        self.todo([USER, self.userid, "+iw", self.nick], self.fullName)
    def handle_close (self):
        #debug('socket closed')
        self.close()

    # asynchat methods
    def collect_incoming_data(self, bytes):
        self.bufIn = self.bufIn + bytes

    def found_terminator(self):
        #debug("found terminator", self.bufIn)
        line = self.bufIn
        self.bufIn = ''

        if line[0] == ':':
            origin, line = string.split(line[1:], ' ', 1)
        else:
            origin = None

        try:
            args, text = string.split(line, ' :', 1)
        except ValueError:
            args = line
            text = ''
        args = string.split(args)

        #debug("from::", origin, "|message::", args, "|text::", text)

        self.rxdMsg(args, text, origin)

    def bind(self, thunk, command, textPat=None, doc=None):
        """
        thunk is the routine to bind; it's called ala
          thunk(matchObj or None, origin, args, text)
        
        command is one of the commands above, e.g. PRIVMSG
        textpat is None or a regex object or string to compile to one
        
        doc should be a list of strings; each will go on its own line"""

        if type(textPat) is type(""): textPat = re.compile(textPat)

        self._dispatch.append((command, textPat, thunk))

        if doc: self._doc = self._doc + doc

    def rxdMsg(self, args, text, origin):
        if args[0] == PING:
            self.todo([PONG, text])

        for cmd, pat, thunk in self._dispatch:
            if args[0] == cmd:
                if pat:
                    #debug('dispatching on...', pat)
                    m = pat.search(text)
                    if m:
                        thunk(m, origin, args, text)
                else:
                    thunk(None, origin, args, text)

    def startChannels(self, chans):
        self._startChannels = chans
        self.bind(self._welcomeJoin, RPL_WELCOME)
                  
    def _welcomeJoin(self, m, origin, args, text):
        for chan in self._startChannels:
            self.todo(['JOIN', chan])

    def tell(self, dest, text):
        """send a PRIVMSG to dest, a channel or user"""
        self.todo([PRIVMSG, dest], text)

    def notice(self, dest, text):
        """send a NOTICE to dest, a channel or user"""
        self.todo([NOTICE, dest], text)

def actionFmt(str):
    return "\001ACTION" + str + "\001"

def replyTo(myNick, origin, args):
    target = args[1]
    if target == myNick: # just to me
        nick, user, host = splitOrigin(origin)
        return nick
    else:
        return target

def splitOrigin(origin):
    if origin and '!' in origin:
        nick, userHost = string.split(origin, '!', 1)
        if '@' in userHost:
            user, host = string.split(userHost, '@', 1)
        else:
            user, host = userHost, None
    else:
        nick = origin
        user, host = None, None
    return nick, user, host

# cf irc:// urls in Mozilla
# http://www.mozilla.org/projects/rt-messaging/chatzilla/irc-urls.html
# Tue, 20 Mar 2001 21:28:14 GMT

def serverAddr(host, port):
    if port == Port: portPart = ''
    else: portPart = ":%s" % port
    return "irc://%s%s/" % (host, portPart)
        
def chanAddr(host, port, chan):
    if port == Port: portPart = ''
    else: portPart = ":%s" % port
    if chan[0] == '&': chanPart = '%26' + chan[1:]
    elif chan[0] == '#': chanPart = chan[1:]
    else: raise ValueError # dunno what to do with this channel name
    return "irc://%s%s/%s" % (host, portPart, chanPart)
        
def debug(*args):
    import sys
    sys.stderr.write("DEBUG: ")
    for a in args:
        sys.stderr.write(str(a) + ' ')
    sys.stderr.write("\n")


def test(hostName, port, chan):
    c = T()
    c.startChannels([chan])

    def spam(m, origin, args, text, c=c):
        c.tell(args[1], "spam, spam, eggs, and spam!")
    c.bind(spam, PRIVMSG, r"spam\?")

    def bye(m, origin, args, text, c=c):
        c.todo([QUIT], "bye bye!")
    c.bind(bye, PRIVMSG, r"bye bye bot")

    c.makeConn(hostName, port)
    asyncore.loop()
    
    
if __name__=='__main__':
    test('irc.w3.org', 6665, '#rdfbot')
    #test('irc.openprojects.net', Port, '#rdfig')

        
#$Log: ircAsync.py,v $
#Revision 1.9 2003/09/13 10:13:28 colas
#removed debug statements, raises EOF on connection close
#
#Revision 1.8  2001/08/24 05:50:52  connolly
#replaced onPrivMsg, onInvite etc. by bind. introduced LOTS of bugs, but I think I fixed most of them. added some documentation, which doubles as test material.
#
#Revision 1.7  2001/08/21 23:03:50  connolly
#general clean-up and tidying... thinking
#about base URIs and contexts.
#
#Revision 1.6  2001/08/21 20:34:12  connolly
#integrated Aaron's patches for join/part.
#holding off on his default prefix patch
#to think about contexts some more.
#
#Revision 1.5  2001/08/20 14:04:56  connolly
#got rid of dead code.
#
#Revision 1.4  2001/08/20 07:39:21  connolly
#questions work now.
#syntax errors are reported.
#irc login protocol revised. (fixed?)
#
#Revision 1.3  2001/08/20 06:16:00  connolly
#woohoo! it's working...
#it accepts RDF/n3 via IRC and stores it in a cwm KB.
#
#Revision 1.2  2001/08/20 04:49:45  connolly
#rdfn3chat has one feature: replies to "help" messages
#with UTSL pointer
#
#Revision 1.1  2001/08/20 03:58:38  connolly
#connects, reponds to PINGs with PONGs.
#
