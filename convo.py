import socket
import threading
from voicecall import VoiceCall


class Convo:
    def __init__(self, host, partner, partner_name, encryption_handler):
        self.host = host       # my IP
        self.port = 4015
        self.addr = (partner, 4015)   # partner IP
        self.partner_name = partner_name

        self.s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.s.bind((self.host, self.port))

        self.DONE_STATUS = 0
        self.MICMODE = 0
        self.voicechat = VoiceCall(host, partner, encryption_handler)
        self.encryption_handler = encryption_handler

    def receive_text(self):
        while self.DONE_STATUS == 0:
            try:
                data_encrypted, _ = self.s.recvfrom(1024)
                #print "message before decryption:", data_encrypted
                #data_encrypted = data_encrypted.decode('utf-8')
                data_deciphered = self.encryption_handler.decrypt_msg(data_encrypted)
                print(self.partner_name+": "+data_deciphered)
            except:
                pass

    def send_text(self):
        while self.DONE_STATUS == 0:
            try:
                text = raw_input()
                if text == 'q':
                    self.end_convo()
                    break
                elif text == 'm':
                    self.voicechat.mic_switch()
                elif len(text) > 0:
                    text_encrypted = self.encryption_handler.encrypt_msg(text)
                    #print "message after encryption:", text_encrypted
                    #self.s.sendto(text_encrypted.encode('utf-8'), self.addr)
                    self.s.sendto(text_encrypted, self.addr)
                    continue
            except:
                pass

    def start_convo(self):
        print("Convo started! Type 'm' to put your mic on/off or 'q' to quit!")
        rcv_thread = threading.Thread(target=self.receive_text)
        snd_thread = threading.Thread(target=self.send_text)
        rcv_thread.start()
        snd_thread.start()
        self.voicechat.start_voice_call()

    def end_convo(self):
        self.DONE_STATUS = 1
        self.s.close()
        self.voicechat.end_voice_call()

