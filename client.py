from most.voip.api import VoipLib
from most.voip.constants import VoipEvent

import time, sys


class Client:
    def __init__(self, name):
        self.SERVER_ADDR = '192.168.1.10'
        self.name = name
        self.voip_params = {u'username': self.name,
                            u'sip_server_pwd': u'pas',
                            u'sip_server_address': self.SERVER_ADDR,
                            u'sip_server_user': self.name,
                            u'sip_server_transport': u'udp',
                            u'log_level': 1,
                            u'debug': True}
        self.CALL_ACTIVE = 0
        self.myVoip=VoipLib()
        print "Initializing the Voip Lib..."
        self.myVoip.init_lib(self.voip_params, self.call_events)
        print "Registering the account on the Sip Server..."
        self.myVoip.register_account()

    def set_exten(self, extension):
        self.extension = extension

    def call_events(self, voip_event_type, voip_event, params):
        print "Received event type:%s Event:%s -> Params: %s" % (voip_event_type, voip_event, params)

        # event triggered when the account registration has been confirmed by the remote Sip Server
        if (voip_event == VoipEvent.ACCOUNT_REGISTERED):
            print "Account registered"

        # event triggered when a new call is incoming
        elif (voip_event == VoipEvent.CALL_INCOMING):
            print "INCOMING CALL From %s" % params["from"]
            time.sleep(2)
            print "Answering..."
            self.myVoip.answer_call()

        # event  triggered when a call has been established
        elif (voip_event == VoipEvent.CALL_ACTIVE):
            print "The call with %s has been established" % self.myVoip.get_call().get_remote_uri()
            self.CALL_ACTIVE=1

        # events triggered when the call ends for some reasons
        elif (voip_event in [VoipEvent.CALL_REMOTE_DISCONNECTION_HANGUP, VoipEvent.CALL_REMOTE_HANGUP,
                             VoipEvent.CALL_HANGUP]):
            print "End of call."
            self.CALL_ACTIVE=0
            #self.myVoip.destroy_lib()

        # event triggered when the library was destroyed
        elif (voip_event == VoipEvent.LIB_DEINITIALIZED):
            print "Lib Destroyed. Exiting from the app."
            return

        # just print informations about other events triggered by the library
        else:
            print "Received unhandled event type:%s --> %s" % (voip_event_type, voip_event)

    def start_call(self):
        if self.extension!='wait':
            print "Making a call dialing the extension: %s" % self.extension
            self.myVoip.make_call(self.extension)

    def hangup(self):
        self.myVoip.hangup_call()

    def end(self):
        self.myVoip.destroy_lib()
