# -*- coding: utf-8 -*-
"""Simple data storage for files in /uploads
"""

from __future__ import unicode_literals, print_function, division
import os


def command_giveflag(bot, user, channel, args):
    """[DEBUG: module_giveflag.py] Usage: giveflag [password]"""
    params = args.split(u" ")
    print(params)
    if len(params) < 1 or len(params[0]) == 0:
        bot.say(channel, "No password provided. Go away!")
        return

    password = params[0].decode("utf-8")
    
    username = user.split("!")[0]
    if (password == username + "_can_h4ndl3_0ldschool_irc"):
        bot.say(channel, "Good job! Your flag is: ALLES{0ld_sch0ol_1rc_was_sooooo0_c00l!4857}")
    else:
        bot.say(channel, "Thats not the password. Try harder")

    return


