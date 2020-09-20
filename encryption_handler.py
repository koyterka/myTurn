import random
import socket
import sys

class Enc_Endpoint():
    def __init__(self, caller, host, partner):
        self.caller = caller
        self.private_key = random.randint(50, 200)

        if caller==1:
            self.public_key1 = random.randint(50, 200)
            self.public_key2 = None
            #print "{%s,%s}" % (self.public_key1, self.private_key)
        else:
            self.public_key1 = None
            self.public_key2 = random.randint(50, 200)
            #print "{%s,%s}" % (self.public_key2, self.private_key)

        self.full_key = None
        self.received_partial_key = None

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
        print "Sending partial key:" , partial_key
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
        partial_key = partial_key%self.public_key2
        return partial_key

    def generate_full_key(self):
        full_key = self.received_partial_key**self.private_key
        full_key = full_key%self.public_key2
        self.full_key = full_key
        print "Generated full key:", full_key

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


# bob = Enc_Endpoint(1, '192.168.1.8', '192.168.1.6')
# bob.exchange_keys()

# msg = 'hej'
# lenght = sys.getsizeof(msg)
# ciphered = bob.encrypt_msg(msg)
# lenght2 = sys.getsizeof(ciphered)
#
# msg2 = "eloszka"
# lenght3 = sys.getsizeof(msg2)
# cip2 = bob.encrypt_msg(msg2)
# cip_en = cip2.encode('utf-8')
# print "enc:" , cip_en
# print "dec:", cip_en.decode('utf-8')
# lenght4 = sys.getsizeof(cip2)
# print lenght, lenght2
#
# print lenght3, lenght4

