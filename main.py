from client import Client
from convo import Convo
import threading
import time
import socket


def main():
    # get login from user
    while True:
        name = raw_input("Hi! What's your name? ")
        if len(name) > 0:
            break
    client = Client(name)

    # main program loop
    while True:
        want = raw_input("Press Enter when you're ready to talk, " + name + '!'
                                                                            '\n Type "quit" if you want to quit.')
        if want == 'quit':
            break

        # get my ip
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        my_ip = s.getsockname()[0]
        s.close()
        #my_ip = '192.168.1.8'

        # TODO: get extension and partner's ip
        partner_ip = '192.168.1.6'
        ans = raw_input("EXTENSION:")
        client.set_exten(str(ans))

        # ***************************** CALL *********************************
        call = threading.Thread(target=client.start_call())
        call.start()

        while client.CALL_ACTIVE == 0:
            time.sleep(1)
            print "Waiting for partner..."

        # start text chat
        chat = Convo(my_ip, partner_ip)
        chat.start_convo()

        # wait for call to end
        while True:
            if client.CALL_ACTIVE == 0:  # someone hang up on us
                chat.end_convo()
                break
            elif chat.DONE_STATUS == 1:  # we want to hang up
                client.hangup()
                break
        # main loop repeats

    # kill the client
    client.end()


if __name__ == '__main__':
    main()
