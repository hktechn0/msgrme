# -*- coding: utf-8 -*-

import MySQLdb
from mod_python import util

from config import *
from db_read import *

# Basic Function
def index():
    ret = u'''Error'''
    return ret

def _nln2online(s):
    if s == "NLN":
        status = "Online"
    elif s == "BSY" or s == 'PHN':
        status = "Busy"
    elif s == "IDL" or s == "AWY" or s == "BRB" or s == "LUN":
        status = "Away"
    else:
        status = "Offline"
    
    return status

# JavaScript status
def status_js(req, id = 0, style = 0):
    db = msgrme_read_db()
    
    id = db.check_id(id)
    if not bool(id):
        return "document.write('ID Error');"
    
    info = db.get_info(id)
    
    db.close()
    del db
    
    presence = info[3]
    status = _nln2online(presence)
    
    if style == "1":
        ret = "document.write('[%s] %s');" % (status, info[0])
    elif style == "2":
        ret = "document.write('[%s] %s');" % (status, info[1])
    elif style == "3":
        ret = "document.write('[%s] %s - %s');" % (status, info[1], info[2])
    elif style == "4":
        ret = "document.write('[%s] %s<br>%s - %s');" % (
            status, info[0], info[1], info[2])
    elif style == "5":
        ret = "document.write('[%s] %s (%s)');" % (status, info[0], info[1])
    elif style == "6":
        ret = "document.write('[%s] %s (%s)');" % (status, info[1], info[0])
    else:
        ret = "document.write('%s');" % status
    
    ret += """document.write(' <a href="http://www.msgrme.com/" target="_blank">\
<img src="http://www.msgrme.com/img/link.png" alt="Messenger me!" border="0" align="top">\
</a>');"""
    
    return ret

# Image Status
def status_img(req, id = 0, style = 0):
    db = msgrme_read_db()

    try:
        style = int(style)
    except:
        style = 0

    id = db.check_id(id)
    if not bool(id):
        util.redirect(req, "%s%02d_fln.png" % (IMGDIR, style))
        return ""
    
    info = db.get_info(id)
    s = info[3]

    db.close()
    del db
    
    if s == "NLN":
        util.redirect(req, "%s%02d_nln.png" % (IMGDIR, style))
    elif s == "BSY" or s == 'PHN':
        util.redirect(req, "%s%02d_bsy.png" % (IMGDIR, style))
    elif s == "IDL" or s == "AWY" or s == "BRB" or s == "LUN":
        util.redirect(req, "%s%02d_awy.png" % (IMGDIR, style))
    else:
        util.redirect(req, "%s%02d_fln.png" % (IMGDIR, style))
    
    return ""

# Image + Text Status
def status(req, id = 0, style = 0):
    db = msgrme_read_db()

    id = db.check_id(id)
    if not bool(id):
        util.redirect(req, "%s01_fln.png" % (IMGDIR))
        return ""
    
    info = db.get_info(id)

    db.close()
    del db

    def buildimage(background = 0x000000, fill = 0xffffff, text = "None"):
        import Image, ImageDraw, ImageFont

        img = Image.new("RGB", (400, 100), background)
        draw = ImageDraw.Draw(img)
        font = ImageFont.truetype(FONTDIR + "VL-PGothic-Regular.ttf", FONTSIZE)

        draw.text((0,0), text, font = font, fill = fill)
        return img

    if style == "1":
        outtext = info[1]
    elif style == "2":
        outtext = "%s - %s" % (info[1], info[2])
    else:
        style = 0
        outtext = info[0]

    img = buildimage(text = outtext)
    trim = img.getbbox()
    
    img = buildimage(0xffffff, 0x000000, outtext)
    img = img.crop(trim)
    
    img.save(SAVEDIR + "%02d%02d.png" % (int(style), id), "PNG")
    del img
    
    html = """\
<a href="%s"><img src="%smme/status_img/1/%d" alt="Messenger me!" border="0"></a> \
<img src="%s%02d%02d.png" alt="address" border="0">""" % (
        SITE, SITE, id, 
        DIMGDIR, int(style), id)
    
    return "document.write('%s');" % html
