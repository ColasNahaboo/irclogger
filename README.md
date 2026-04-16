# Irclogger

irclogger is a simple "bot", a program connecting as a client on IRC  servers to provide a web log of what is said. It aims to provide a  simple, fast, efficient and web-compliant service. It is quite robust  and mature, having be in daily heavy use for personal & business use since 2003. This page is at https://colas.nahaboo.net/Code/IrcLogger.

**Note in 2026:** This code is quite old, and although I still use it (on private IRC servers), I am a bit ashamed of its bash coding style, and the python part needs python v2.7 which is really obsolete. I would recommend using other IRC loggers, especially for public IRC sites. Note that I have currently recoded the IRC bot in Go, and may even rewrite the web display bash code for fun in the future to create an irclogger2.

## Goals 

-  **Be used on intranets**, where users can be trusted  and will not try constantly to crack the system. Thus the bot do not  need to provide the plethora of anti-hackers, channel defending measures
-  **Provide privacy**, users can set passwords on the log files, change them, but cannot remove them
-  **Be another web tool**, the bot obeys just the  minimal IRC commands to log or not a channel. All the rest is done via a web browser. Each logged phrase becomes a part of the web with its own  URL.

## More info

- its web page: https://colas.nahaboo.net/Code/IrcLogger
- its technical documentation in the [README.txt](README.txt) file, with the Installation instructions

## License

GPV v3
