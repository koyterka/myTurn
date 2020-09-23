import random
import socket
from Crypto import Random
import Crypto.Cipher.AES as AES
import base64
import hashlib


class Enc_Endpoint:
    def __init__(self, caller, host, partner):
        self.caller = caller
        self.private_key = random.randint(50, 200)

        if caller == 1:
            self.public_key1 = random.randint(50, 200)
            self.public_key2 = None
            # print "{%s,%s}" % (self.public_key1, self.private_key)
        else:
            self.public_key1 = None
            self.public_key2 = random.randint(50, 200)
            # print "{%s,%s}" % (self.public_key2, self.private_key)

        self.full_key = None
        self.received_partial_key = None
        self.bs = AES.block_size

        self.host = host  # my IP
        self.port = 4015
        self.addr = (partner, 4015)  # partner IP
        self.s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.s.settimeout(1.0)
        self.s.bind((self.host, self.port))

    def exchange_keys(self):
        self.exchange_public_keys()
        self.exchange_partial_keys()

    def exchange_public_keys(self):
        if self.caller == 1:
            print "Sending public key 1:", self.public_key1
            self.s.sendto(str(self.public_key1).encode('utf-8'), self.addr)
            while True:
                try:
                    data, _ = self.s.recvfrom(1024)
                    data = data.decode('utf-8')
                    print 'Received public key 2:', data
                    self.public_key2 = int(data)
                    break
                except:
                    pass
        else:
            while True:
                try:
                    data, _ = self.s.recvfrom(1024)
                    data = data.decode('utf-8')
                    print 'Received public key 1:', data
                    self.public_key1 = int(data)
                    break
                except:
                    pass
            print "Sending public key 2:", self.public_key2
            self.s.sendto(str(self.public_key2).encode('utf-8'), self.addr)

    def exchange_partial_keys(self):
        partial_key = self.generate_partial_key()
        print "Sending partial key:", partial_key
        self.s.sendto(str(partial_key).encode('utf-8'), self.addr)
        while True:
            try:
                data, _ = self.s.recvfrom(1024)
                data = data.decode('utf-8')
                print 'Received partial key:', data
                self.received_partial_key = int(data)
                break
            except:
                pass
        self.s.close()
        self.generate_full_key()

    def generate_partial_key(self):
        partial_key = self.public_key1**self.private_key
        partial_key = partial_key % self.public_key2
        return partial_key

    def generate_full_key(self):
        full_key = self.received_partial_key**self.private_key
        full_key = full_key % self.public_key2
        full_key = hashlib.sha256(str(full_key).encode()).digest()
        self.full_key = full_key
        print "Generated full key."

    def get_full_key(self):
        return self.full_key

    def aes_encrypt(self, msg):
        raw = self.padding(msg)
        iv = Random.new().read(AES.block_size)
        cipher = AES.new(self.full_key, AES.MODE_CBC, iv)
        return base64.b64encode(iv + cipher.encrypt(raw.encode()))

    def aes_decrypt(self, enc):
        enc = base64.b64decode(enc)
        iv = enc[:AES.block_size]
        cipher = AES.new(self.full_key, AES.MODE_CBC, iv)
        return self.remove_padding(cipher.decrypt(enc[AES.block_size:])).decode('utf-8')

    def padding(self, s):
        return s + (self.bs - len(s) % self.bs) * chr(self.bs - len(s) % self.bs)

    @staticmethod
    def remove_padding(s):
        return s[:-ord(s[len(s) - 1:])]
