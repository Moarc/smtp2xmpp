An extremely crude XMPP component that receives mail as a SMTP server and relays it to a specified set of XMPP users. Put together in a single morning and polished (yeah, right) in the afternoon.

Initially copied verbatim from ["XMPP ToDo List Example"](https://github.com/ntoll/xmppComponent), which seems to be a modified example from the SleekXMPP project. Supplemented with [usage examples](https://aiosmtpd.readthedocs.io/en/latest/controller.html) from aiosmtpd docs. Modified to accept a socket passed by systemd, since that allows us to listen on port 25 as an unpriviledged user.

Since the component example originally came from SleekXMPP, it's [MIT-licensed](LICENSE.SleekXMPP), I guess? The `receive_systemd_socket` function is a modification of `aiosmtpd.controller.InetMixin._create_server` from aiosmtpd, and the `MailHandler` class was copied directly from their docs, their code is under [Apache 2.0](LICENSE.aiosmtpd)
