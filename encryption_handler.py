import random
import socket

class Enc_Endpoint():
    def __init__(self, caller, host, partner):
        self.caller = caller
        self.private_key = random.randint(50, 200)

        if caller==1:
            self.public_key1 = random.randint(50, 200)
            self.public_key2 = None
            # print "{%s,%s}" % (self.public_key1, self.private_key)
        else:
            self.public_key1 = None
            self.public_key2 = random.randint(50, 200)
            # print "{%s,%s}" % (self.public_key2, self.private_key)

        self.full_key = None
        self.received_partial_key = None

        self.host = host  # my IP
        self.port = 4015
        self.addr = (partner, 4015)  # partner IP
        self.s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.s.bind((self.host, self.port))

    def exchange_keys(self):
        self.exchange_public_keys()
        self.exchange_partial_keys()

    def exchange_public_keys(self):
        if self.caller == 1:
            print "SENDING PUBLIC KEY 1" + self.public_key1
            self.s.sendto(self.public_key1.encode('utf-8'), self.addr)
            while True:
                try:
                    data, _ = self.s.recvfrom(1024)
                    data = data.decode('utf-8')
                    print 'RECEIVED PUBLIC KEY 2' + data
                    self.public_key2 = data
                    break
                except:
                    pass
        else:
            while True:
                try:
                    data, _ = self.s.recvfrom(1024)
                    data = data.decode('utf-8')
                    print 'RECEIVED PUBLIC KEY 1' + data
                    self.public_key1 = data
                    break
                except:
                    pass
            print "SENDING PUBLIC KEY 2" + self.public_key2
            self.s.sendto(self.public_key2.encode('utf-8'), self.addr)

    def exchange_partial_keys(self):
        partial_key = self.generate_partial_key()
        print "SENDING PARTIAL KEY" + partial_key
        self.s.sendto(partial_key.encode('utf-8'), self.addr)
        while True:
            try:
                data, _ = self.s.recvfrom(1024)
                data = data.decode('utf-8')
                print 'RECEIVED PARTIAL KEY' + data
                self.received_partial_key = data
                break
            except:
                pass
        self.s.close()
        self.generate_full_key()

    def generate_partial_key(self):
        partial_key = self.public_key1**self.private_key
        partial_key = partial_key%self.public_key2
        return partial_key

    def generate_full_key(self):
        full_key = self.received_partial_key**self.private_key
        full_key = full_key%self.public_key2
        self.full_key = full_key
        print "GENERATED FULL KEY:", full_key

    def get_full_key(self):
        return self.full_key

    def encrypt_msg(self, msg):
        encrypted_msg = ""
        key = self.full_key
        for c in msg:
            encrypted_msg += chr(ord(c)+key)
        return encrypted_msg

    def decrypt_msg(self, encrypted_msg):
        decrypted_msg = ""
        key = self.full_key
        for c in encrypted_msg:
            decrypted_msg += chr(ord(c)-key)
        return decrypted_msg


mark = Enc_Endpoint(caller = 1, host= '192.168.1.6', partner='192.168.1.8')
bob = Enc_Endpoint(caller = 0, host = '192.168.1.8', partner='192.168.1.6')

mark.exchange_keys()
bob.exchange_keys()


msg = "eloszka kokoszka"
enc_msg = bob.encrypt_msg(msg)
dec_msg = bob.decrypt_msg(enc_msg)

print dec_msg



