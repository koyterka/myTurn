from client import Client
from convo import Convo
import threading
import time
import socket
import requests
import ast

URL = "http://192.168.1.10:9898"
ENDPOINT_NEW_USER = "/add-user-to-sip-exten-conf/"
ENDPOINT_SIP_FILE = "/sip-file-lookup"
ENDPOINT_USER_STATUS_RDY = "/update-status-rdy/"
ENDPOINT_USER_STATUS_BUSY = "/update-status-busy/"
ENDPOINT_PEER = "/get-peer/"
ENDPOINT_USER_IP = "/user-ip/"
ENDPOINT_USER_STATUS_RDY_TO_TALK = "/update-status-rdy-to-talk/"

caller=0
exten = 0
partner_ip = 0
partner_name = ""

def get_user_status_value(u_name):
    final_endpoint = URL + "/user-status/" + u_name
    req = requests.get(final_endpoint)
    return req.text

def main():
    global caller
    global exten
    global partner_ip
    global partner_name

    # get login from user
    while True:
        name = raw_input("Hi! What's your name? ")
        if len(name) > 0:
            break

    # put user into SIP server files
    final_endpoint = URL + ENDPOINT_NEW_USER + str(name)
    req = requests.post(final_endpoint)
    if(req.status_code!=200):
        print "Sorry, couldn't put you into SIP server."
        return

    server_ip = '192.168.1.10'
    client = Client(name, server_ip)


    # main program loop
    while True:
        want = raw_input("Press Enter when you're ready to talk, " + name + '!'
                        + '\n Type "quit" if you want to quit.')
        if want == 'quit':
            print "Bye!"
            break

        # let server know you're ready to talk.
        final_endpoint = URL + ENDPOINT_USER_STATUS_RDY + str(name)
        req = requests.put(final_endpoint)
        if (req.status_code != 200):
            print "Sorry, couldn't let the server know you're ready."
            break


        # find a partner to talk to
        final_endpoint = URL + ENDPOINT_PEER + str(name)
        while True:
            req = requests.get(final_endpoint, verify=False)

            if req.status_code == 226:
                time.sleep(1)
                continue

            if req.status_code == 208:
                time.sleep(1)
                continue

            # you'll be making SIP call
            if req.status_code == 202:
                caller=1
                info_dict = ast.literal_eval(req.text)
                partner_name = info_dict["call"]
                exten = info_dict["exten"]
                partner_ip = info_dict["ip_to_send_data"]

                # see if your partner is waiting for your call
                while True:
                    status = get_user_status_value(partner_name)
                    if int(status) == 3:
                        break
                break

            # you'll be waiting for SIP call
            if req.status_code == 230:
                info_dict = ast.literal_eval(req.text)
                partner_ip = info_dict["ip_to_send_data"]
                partner_name = info_dict["name_ip"]
                final_endpoint = URL+ENDPOINT_USER_STATUS_RDY_TO_TALK + str(name)
                req = requests.put(final_endpoint)
                # let server know you're waiting for the call
                if(req.status_code!=200):
                    print "Sorry, couldn't communicate with server."
                    break

                break

            time.sleep(1)



        # get my ip
        # s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # s.connect(("8.8.8.8", 80))
        # my_ip = s.getsockname()[0]
        # s.close()
        my_ip = '192.168.1.6'

        client.set_exten(str(exten))
        client.set_caller(caller)
        # ***************************** CALL *********************************
        call = threading.Thread(target=client.start_call())
        call.start()

        while client.CALL_ACTIVE == 0:
            time.sleep(1)
            print "Waiting for partner..."

        # start text chat
        chat = Convo(my_ip, partner_ip, partner_name)
        chat.start_convo()

        # wait for call to end
        while True:
            if client.CALL_ACTIVE == 0:  # someone hang up on us
                chat.end_convo()
                break
            elif chat.DONE_STATUS == 1:  # we want to hang up
                client.hangup()
                break

        final_endpoint = URL + ENDPOINT_USER_STATUS_BUSY + str(name)
        req = requests.put(final_endpoint)
        # main loop repeats

    # kill the client
    client.end()


if __name__ == '__main__':
    main()
