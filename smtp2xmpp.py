#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import logging
import time
from optparse import OptionParser
import asyncio
import aiosmtpd
from aiosmtpd.controller import UnthreadedController
import socket
import email
import email.policy

import slixmpp
from slixmpp.componentxmpp import ComponentXMPP
from slixmpp.stanza.roster import Roster
from slixmpp.xmlstream import ElementBase
from slixmpp.xmlstream.stanzabase import ET, register_stanza_plugin

def receive_systemd_socket(self):
    """
    Creates a 'server task' that listens on a Unix Socket file.
    Does NOT actually start the protocol object itself;
    _factory_invoker() is only called upon fist connection attempt.
    """
    return self.loop.create_server(
        self._factory_invoker,
        sock=socket.fromfd(3, socket.AF_INET, socket.SOCK_STREAM),
        ssl=self.ssl_context,
        )

aiosmtpd.controller.InetMixin._create_server = receive_systemd_socket

class MailHandler:
    async def handle_RCPT(self, server, session, envelope, address, rcpt_options):
        #if not address.endswith('@localhost'):
        #    return '550 not relaying to that domain'
        envelope.rcpt_tos.append(address)
        return '250 OK'

    async def handle_DATA(self, server, session, envelope):
        fromjid = envelope.mail_from.replace('localhost',xmpp.boundjid.bare).replace('127.0.0.1',xmpp.boundjid.bare)
        body = email.message_from_bytes(envelope.content, policy=email.policy.default).get_body(preferencelist=('plain', 'html')).get_content()

        logging.log(5,'Message from %s' % envelope.mail_from)
        logging.log(5,'Message for %s' % envelope.rcpt_tos)
        logging.log(5,'Message data:\n')

        for ln in body.splitlines():
            logging.log(5,f'> {ln}'.strip())
        logging.log(5,'')
        logging.log(5,'End of message')

        if config['rosteronly']:
            for jid in xmpp.roster:
                xmpp.send_presence(pfrom=fromjid, pto=jid, pshow='xa')
                xmpp.send_message(mfrom=fromjid, mto=jid, mbody=body)
        else:
            for rcpt in envelope.rcpt_tos:
                rcpt = rcpt.replace('localhost',config['host']).replace('127.0.0.1',config['host'])
                xmpp.send_presence(pfrom=fromjid, pto=rcpt, pshow='xa')
                xmpp.send_message(mfrom=fromjid, mto=rcpt, mbody=body)
        return '250 Message accepted for delivery'

class Config(ElementBase):

    """
    In order to make loading and manipulating an XML config
    file easier, we will create a custom stanza object for
    our config XML file contents. See the documentation
    on stanza objects for more information on how to create
    and use stanza objects and stanza plugins.

    We will reuse the IQ roster query stanza to store roster
    information since it already exists.
    """

    name = "config"
    namespace = "slixmpp:config"
    interfaces = {'component', 'host', 'secret', 'server', 'port', 'rosteronly'}
    sub_interfaces = {'component', 'host', 'secret', 'server', 'port'}
    bool_interfaces = {'rosteronly'}


register_stanza_plugin(Config, Roster)


class ConfigComponent(ComponentXMPP):

    def __init__(self, config):
        """
        Create a ConfigComponent.

        Arguments:
            config      -- The XML contents of the config file.
            config_file -- The XML config file object itself.
        """
        ComponentXMPP.__init__(self, "{}.{}".format(config['component'],config['host']),
                                     config['secret'],
                                     config['server'],
                                     config['port'])

        # Store the roster information.
        self.roster = config['roster']['items']

        # The session_start event will be triggered when
        # the component establishes its connection with the
        # server and the XML streams are ready for use. We
        # want to listen for this event so that we we can
        # broadcast any needed initial presence stanzas.
        self.add_event_handler("session_start", self.start)

        # The message event is triggered whenever a message
        # stanza is received. Be aware that that includes
        # MUC messages and error messages.
        #self.add_event_handler("message", self.message)

    def start(self, event):
        """
        Process the session_start event.

        The typical action for the session_start event in a component
        is to broadcast presence stanzas to all subscribers to the
        component. Note that the component does not have a roster
        provided by the XMPP server. In this case, we have possibly
        saved a roster in the component's configuration file.

        Since the component may use any number of JIDs, you should
        also include the JID that is sending the presence.

        Arguments:
            event -- An empty dictionary. The session_start
                     event does not provide any additional
                     data.
        """
        for jid in self.roster:
            self.send_presence(pfrom=self.jid, pto=jid)

if __name__ == '__main__':
    # Setup the command line arguments.
    optp = OptionParser()

    # Output verbosity options.
    optp.add_option('-q', '--quiet', help='set logging to ERROR',
                    action='store_const', dest='loglevel',
                    const=logging.ERROR, default=logging.INFO)
    optp.add_option('-d', '--debug', help='set logging to DEBUG',
                    action='store_const', dest='loglevel',
                    const=logging.DEBUG, default=logging.INFO)
    optp.add_option('-v', '--verbose', help='set logging to COMM',
                    action='store_const', dest='loglevel',
                    const=5, default=logging.INFO)

    # Component name and secret options.
    optp.add_option("-c", "--config", help="path to config file",
                    dest="config", default="/etc/smtp2xmpp/config.xml")

    opts, args = optp.parse_args()

    # Setup logging.
    logging.basicConfig(level=opts.loglevel,
                        format='%(levelname)-8s %(message)s')

    # Load configuration data.
    config_file = open(opts.config, 'r')
    config_data = "\n".join([line for line in config_file])
    config = Config(xml=ET.fromstring(config_data))
    config_file.close()

    # Setup the ConfigComponent and register plugins. Note that while plugins
    # may have interdependencies, the order in which you register them does
    # not matter.
    xmpp = ConfigComponent(config)
    xmpp.register_plugin('xep_0030') # Service Discovery
    xmpp.register_plugin('xep_0004') # Data Forms
    xmpp.register_plugin('xep_0060') # PubSub
    xmpp.register_plugin('xep_0199') # XMPP Ping

    # Connect to the XMPP server and start processing XMPP stanzas.
    try:
        xmpp.connect()
        #xmpp.process()
        controller = UnthreadedController(MailHandler(), port=25, hostname="localhost", server_hostname="localhost", loop=xmpp.loop)
        controller.begin()
        #tasks = [asyncio.sleep(10)]
        tasks = [xmpp.disconnected]
        xmpp.loop.run_until_complete(asyncio.wait(tasks))
        #xmpp.loop.run_forever()
    except Exception as exception:
        logging.exception(exception)
    print("Done")
