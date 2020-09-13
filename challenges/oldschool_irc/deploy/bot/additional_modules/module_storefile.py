# -*- coding: utf-8 -*-
"""Simple data storage for files in /uploads
"""

from __future__ import unicode_literals, print_function, division
import os

def command_storefile(bot, user, channel, args):
    """[DEBUG: module_storefile.py] Stores a file with user specified content . Usage: storefile [filename] [content]"""
    upload_directory = "./uploads"
    if os.path.isdir(upload_directory) == False:
        os.mkdir(upload_directory)

    params = args.split(u" ")
    print(params)
    if len(params) < 2:
        bot.say(channel, "Invalid number of arguments!")
        return

    filename = params[0].decode("utf-8")
    # Sanitize filename! We don't want vulnerabilites in there...
    filename = filename.replace("..", "")


    content = ""
    for c in params[1:]: content += c.decode("utf-8") + " "
    content = content[0:-1]

    print("Filename: %s Content: %s" % (filename, content))
    
    full_filename = "%s/%s" % (upload_directory, filename)
    if os.path.exists(full_filename):
        bot.say(channel, "File %s already exists! Can't overwrite the file!" % full_filename)
        return
    
    open(full_filename, "w").write(content)
    bot.say(channel, "Content with length of %d written to %s!" % (len(content), full_filename))

    return