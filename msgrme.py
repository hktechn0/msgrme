#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
import signal
import gobject
import datetime
import pymsn, pymsn.event

from config import *
from msgrme_db import *  

VERSION = "1.1-devel"

# Init
recon = 0
chat = []
quit_flg = False
recontime = "None"

db = msgrme_db(HOST, USER, PASSWD, DBNAME, CHARSET)

def quit_logout(signum, frame):
    print "[Info] Get SIGINT"
    global quit_flg
    quit_flg = True
    mainloop.quit()

# Signal get setting
signal.signal(signal.SIGINT, quit_logout)

# Login Comeplete!
def complete_login():
    print "[Info] LoginComplete"

    messenger.profile.display_name = BOT_NAME
    messenger.profile.personal_message = BOT_MSG
    messenger.profile.privacy = pymsn.profile.Privacy.ALLOW
    messenger.profile.presence = pymsn.profile.Presence.ONLINE
    messenger.profile.client_id.is_bot = True
    
    print """================================================================================
Memberlist
================================================================================"""
    for contact in messenger.address_book.contacts:
        check = db.check_member(contact)
        if not check == 0:
            msg_send(contact, "Your ID: " + str(check) + FOOTER)
            print "%20s [%2s]: %30s [New Member]" % (
                contact.display_name, contact.memberships, 
                contact.account)
        else:
            print "%20s [%2s]: %30s" % (
                contact.display_name, contact.memberships, 
                contact.account)
    print "================================================================================"
    
    gobject.timeout_add(10000, sync_memberlist)

# Send Message
def msg_send(contact, message):
    conv = pymsn.Conversation(messenger, [contact])
    msg = pymsn.conversation.ConversationMessage(message)
    conv.send_text_message(msg)
    conv.leave()

# Sync Memberlist
def sync_memberlist():
    messenger.address_book.sync()
    lastsync = datetime.datetime.now()

    pending = notexist = deleted = 0

    for contact in messenger.address_book.contacts:
        # pending member
        if contact.memberships & 0x10:
            messenger.address_book.accept_contact_invitation(contact)
            pending += 1
            #print "[Pending] %s [%s]: %s" % (
            #    contact.display_name, contact.memberships, 
            #    contact.account )

        # not exist in my memberlist
        if not contact.memberships & 0x01:
            messenger.address_book.add_messenger_contact(contact)
            notexist += 1
            #print "[Not in list] %s [%s]: %s" % (
            #    contact.display_name, contact.memberships, 
            #    contact.account )

        # deleted me
        if not contact.memberships & 0x08:
            deleted += 1
            dflag = True
            #print "[Deleted Me] %s [%s]: %s" % (
            #    contact.display_name, contact.memberships, 
            #    contact.account )
        else:
            dflag = False

        db.set_deleted(db.get_id(contact), dflag)
        db.update_member(contact)

    os.system("clear")
    print "===== Messenger Me! System - version %s =====" % VERSION
    print "Total Members    : %d" % len(messenger.address_book.contacts)
    print "Deleted Members  : %d" % deleted
    print "Not exist Members: %d" % notexist
    print "Total Reconnect  : %d" % recon
    print "Last Reconnect   : %s" % recontime
    print "Last Synchronized: %s" % lastsync
    print ""

    gobject.timeout_add(SYNC_INTERVAL, sync_memberlist)


# Client Event
class ClientEventHandler(pymsn.event.ClientEventInterface):
    def on_client_state_changed(self, state):
        global quit_flg
        if state == pymsn.event.ClientState.OPEN:
            complete_login();
        elif state == pymsn.event.ClientState.CLOSED and (not quit_flg):
            print "[Info] ClosedConnection"
            mainloop.quit()
            
    def on_client_error(self, error_type, error):
        if error_type == pymsn.event.ClientErrorType.AUTHENTICATION:
            print "[Error] Wrong username or password."
            mainloop.quit()
        else:
            print "[Error] Client: %s, %s" % ( error_type, error )

# Conversation Event
class ConversationEventHandler(pymsn.event.ConversationEventInterface):
    def on_conversation_message_received(self, sender, message):
        print sender.account, "->", message.content

        if message.content == "getid":
            getid = db.get_id(sender)
            msg_log = "Your ID: " + str(getid)
            msg_txt = msg_log + FOOTER
        elif message.content == "status_img":
            getid = db.get_id(sender)
            msg_txt = 'stauts_img HTML Code:\n\
<a href="%s" target="_blank">\
<img src="%s%sstatus_img/%d" alt="Messenger me!" border="0">\
</a>' % (SITE, SITE, SCRIPT, getid)
            msg_log = "status_img HTML Code"
        elif message.content == "status_js":
            getid = db.get_id(sender)
            msg_txt = 'stauts_js HTML Code:\n\
<script type="text/javascript" src="%s%sstatus_js/%d"></script>' % (SITE, SCRIPT, getid)
            msg_log = "status_js HTML Code"
        else:
            msg_log = "Sorry, I am a bot."
            msg_txt = msg_log + FOOTER

        msg = pymsn.conversation.ConversationMessage(msg_txt)
        self.chat.send_text_message(msg)
        print sender.account, "<-", msg_log
        self.chat.leave()
        
        global chat
        chat.pop()

    def on_conversation_user_typing(self, contact):
        pass
    
    def on_conversation_error(self, type, error):
        print "[Error] Conversation: %s, %s" % ( type, error )

# AdressBook Event
class AddressBookEventHandler(pymsn.event.AddressBookEventInterface):
    def on_addressbook_messenger_contact_added(self, contact):
        print "[Added]:", contact.account
        sync_memberlist()

    def on_addressbook_contact_deleted(self, contact):
        print "[Deleted]:", contact.account
        sync_memberlist()

# Contact Event
class ContactEventHandler(pymsn.event.ContactEventInterface):
    def on_contact_memberships_changed(self, contact):
        print "[Info] ContactMembershipsChanged: %s, %s" % (
            contact.account, contact.memberships)
        db.update_member(contact)

    def on_contact_presence_changed(self, contact):
        print "[Info] ContactPresenceChanged: %s, %s" % (
            contact.account, contact.presence)
        db.update_member(contact)

    def on_contact_display_name_changed(self, contact):
        print "[Info] ContactNameChanged: %s, %s" % (
            contact.account, contact.display_name)
        db.update_member(contact)

    def on_contact_personal_message_changed(self, contact):
        print "[Info] ContactMessageChanged: %s, %s" % (
            contact.account, contact.personal_message)
        db.update_member(contact)

# Invite Event
class InviteEventHandler(pymsn.event.InviteEventInterface):
    def on_invite_conversation(self, conversation):
        global chat
        chat_event = ConversationEventHandler(conversation)
        chat_event.chat = conversation
        chat.append(chat_event)

# Main
while True:
    # Create Messenger Object
    messenger = pymsn.Client(SERVER)

    # Chat Array /clear
    chat = []

    # Create EventHandler
    pymsn_client_events = ClientEventHandler(messenger)
    pymsn_addressbook_events = AddressBookEventHandler(messenger)
    pymsn_contact_events = ContactEventHandler(messenger)
    invite_events = InviteEventHandler(messenger)
    
    # Option
    if len(sys.argv) > 1:
        if sys.argv[1] == "-d":
            import logging
            logging.basicConfig(level = logging.DEBUG)
            print "!! Debug Mode"
        elif sys.argv[1] == "--setup":
            db.setup();
            exit()
    
    # Messenger Login
    messenger.login(*ACCOUNT)  
    
    # Start
    mainloop = gobject.MainLoop()
    mainloop.run()
    
    # Close
    messenger.logout()

    # if Quit(C-c Interrupt) then...
    if quit_flg:
        print "Quit..."
        db.to_offline()
        db.close()
        exit()

    # nonono, New member restart...
    print "[Info] Reconnect..."
    recontime = datetime.datetime.now()
    recon += 1
