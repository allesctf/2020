# -*- coding: utf-8 -*-
"""Simple data storage for files in /uploads
"""

from __future__ import unicode_literals, print_function, division
import os

def command_readfile(bot, user, channel, args):
    """[DEBUG: module_readfile.py]  Reads a file from the ./uploads folder. Usage: readfile [filename]"""
    upload_directory = "./uploads"
    if os.path.isdir(upload_directory) == False:
        os.mkdir(upload_directory)

    params = args.split(u" ")
    print(params)
    if len(params) < 1 or len(params[0]) == 0:
        bot.say(channel, "Invalid number of arguments!")
        return

    filename = params[0].decode("utf-8")
    
    full_filename = "%s/%s" % (upload_directory, filename)
    #print(os.listdir(full_filename))

    if (os.path.isdir(full_filename)):
        bot.say(channel, "File %s is a folder!" % full_filename)
        return
    if os.path.isfile(full_filename) == False:
        bot.say(channel, "File %s does not exist!" % full_filename)
        return
    
    content = open(full_filename, "r").read()
    bot.say(channel, "Content of file %s: %s!" % (full_filename, content))

    return