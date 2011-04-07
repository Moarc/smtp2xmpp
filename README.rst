XMPP ToDo List Example
======================

A very simple XMPP component created for demonstration purposes.

To make this work you need to have SleekXMPP on your Python path. You can grab it from the GitHub repository here:

https://github.com/fritzy/SleekXMPP

You'll also need an XMPP server running locally. I suggest you use Prosody since this is *really* easy to set up. On a Debian based machine you simply need to:

$ apt-get install prosody

You'll need to configure the server correctly to accept connections from the component. I've included my configuration file (localhost.cfg.lua) which you can modify to suit your needs and place in:

/etc/prosody/conf.avail

You'll also need to modify the prosody.cfg.lua file in /etc/prosody so that:

allow_registration = true;

So that players can join your server.

(See http://prosody.im/doc/creating_accounts for more information)

To see the changes take effect restart the prosody server thus:

$ /etc/init.d/prosody restart

Have fun!
