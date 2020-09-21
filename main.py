from client import Client
from convo import Convo
import threading
import time
import socket
import requests
import json
from encryption_handler import Enc_Endpoint

URL = "http://192.168.1.10:9898"
ENDPOINT_NEW_USER = "/add-user-to-sip-exten-conf/"
ENDPOINT_SIP_FILE = "/sip-file-lookup"
ENDPOINT_USER_STATUS_RDY = "/update-status-rdy/"
ENDPOINT_USER_STATUS_BUSY = "/update-status-busy/"
ENDPOINT_PEER = "/get-peer/"
ENDPOINT_USER_IP = "/user-ip/"
ENDPOINT_USER_STATUS_RDY_TO_TALK = "/update-status-rdy-to-talk/"

name=""
caller=0
exten = 0
partner_ip = 0
partner_name = ""


def get_user_status_value(u_name):
    final_endpoint = URL + "/user-status/" + u_name
    req = requests.get(final_endpoint)
    return req.text

def main():
    global name
    global caller
    global exten
    global partner_ip
    global partner_name

    # get my ip
    # s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # s.connect(("8.8.8.8", 80))
    # my_ip = s.getsockname()[0]
    # s.close()
    my_ip = '192.168.1.6'

    # get login from user
    while True:
        name = raw_input("Hi! What's your name? ")
        if len(name) > 0:
            final_endpoint = URL + ENDPOINT_NEW_USER + str(name)
            req = requests.post(final_endpoint)
            if (req.status_code != 200):
                print "Sorry, that name is already taken."
            else:
                break

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
                print 'youll be calling'
                caller=1
                info_dict = json.loads(req.text)
                partner_name = info_dict["call"]
                exten = info_dict["exten"]
                partner_ip = info_dict["ip_to_send_data"]
                print info_dict
                enc_endpoint = Enc_Endpoint(1, my_ip, partner_ip)

                # see if your partner is waiting for your call
                while True:
                    status = get_user_status_value(partner_name)
                    print status
                    if int(status) == 3:
                        break
                    time.sleep(1)

                # set Diffie-Hellman key for encrypted communication
                enc_endpoint.exchange_keys()
                break

            # you'll be waiting for SIP call
            if req.status_code == 230:
                print 'youll be waiting'
                info_dict = json.loads(req.text)
                print info_dict
                partner_ip = info_dict["ip_to_send_data"]
                partner_name = info_dict["call"]

                # set Diffie-Hellman key for encrypted communication
                enc_endpoint = Enc_Endpoint(0, my_ip, partner_ip)
                key_exchange_thread = threading.Thread(target=enc_endpoint.exchange_keys)
                key_exchange_thread.start()

                # let server know you're waiting for the call
                final_endpoint = URL + ENDPOINT_USER_STATUS_RDY_TO_TALK + str(name)
                req = requests.put(final_endpoint)
                if(req.status_code!=200):
                    print "Sorry, couldn't communicate with server."
                    break

                break

            time.sleep(1)

        client.set_exten(str(exten))
        client.set_caller(caller)
        # ***************************** CALL *********************************
        call = threading.Thread(target=client.start_call())
        call.start()

        while client.CALL_ACTIVE == 0:
            time.sleep(1)
            print "Waiting for partner..."

        # start text chat
        chat = Convo(my_ip, partner_ip, partner_name, enc_endpoint)
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
    final_endpoint = URL + "/delete-user/" + str(name)
    req = requests.delete(final_endpoint)
    client.end()




if __name__ == '__main__':
    main()
