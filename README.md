## Prelude
I wanted to pass messages from [lilac](https://github.com/archlinuxcn/lilac) to Jabber, since I don't run a mail server. There was one archived project like that on GitHub, written in Go using an XMPP library that was wiped off the face of the internet a long time ago. I didn't want to bother the author of the library (who may or may not still have the code that he deleted from GitHub), and not knowing Go, I turned to Python. 'This can't be all that hard', I thought to myself. The result is this mess.

## What is it?
An extremely crude XMPP component that receives mail as a SMTP server and relays it to a specified set of XMPP users. Put together in a single morning and polished (yeah, right) in the afternoon.

Initially copied verbatim from ["XMPP ToDo List Example"](https://github.com/ntoll/xmppComponent), which seems to be a modified example from the SleekXMPP project. Supplemented with [usage examples](https://aiosmtpd.readthedocs.io/en/latest/controller.html) from aiosmtpd docs. Modified to accept a socket passed by systemd, since that allows us to listen on port 25 as an unpriviledged user.

## Licensing
Since the component example originally came from SleekXMPP, it's [MIT-licensed](LICENSE.SleekXMPP), I guess? The `receive_systemd_socket` function is a modification of `aiosmtpd.controller.InetMixin._create_server` from aiosmtpd, and the `MailHandler` class was copied directly from their docs, their code is under [Apache 2.0](LICENSE.aiosmtpd). I haven't published much code before, so if anyone gets outraged about the licensing - don't beat me too hard, contact me, and we'll clarify the situation.
