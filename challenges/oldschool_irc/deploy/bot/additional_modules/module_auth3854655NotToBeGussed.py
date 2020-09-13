# Pla1nt3xtPassw0rdsAreBad!

from __future__ import unicode_literals, print_function, division
from twisted.internet import reactor
import time

# rejoin after 1 minute
delay = 61


def handle_receivedMOTD(bot, motd):
    """Auth to oper"""
    bot.log("Authing to oper...")
    reactor.callLater(4, bot.sendLine, "oper BottyMcBotface Pla1nt3xtPassw0rdsAreBad!")
    reactor.callLater(5, bot.sendLine, "ojoin #challenge")