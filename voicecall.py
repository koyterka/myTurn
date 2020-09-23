import socket
import threading
import pyaudio


class VoiceCall:
    def __init__(self, host, partner, encryption_handler):
        self.host = host
        self.port = 9000
        self.addr = (partner, 9000)
        self.s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.s.bind((self.host, self.port))
        self.DONE_STATUS = 0
        self.MIC_ON = 0
        self.encryption_handler = encryption_handler

        # audio stream config
        self.chunk_size = 1024
        self.audio_format = pyaudio.paInt16
        self.channels = 1
        self.rate = 44100
        self.p = pyaudio.PyAudio()
        self.recording_stream = None
        self.playing_stream = None

    def receive_data(self):
        self.playing_stream = self.p.open(format=self.audio_format, channels=self.channels, rate=self.rate, output=True,
                                          frames_per_buffer=self.chunk_size)
        while self.DONE_STATUS == 0:
            try:
                encrypted_data = self.s.recvfrom(16)
                decrypted_data = self.encryption_handler.aes_decrypt(encrypted_data)
                self.playing_stream.write(decrypted_data)
            except:
                pass

    def send_data(self):
        self.recording_stream = self.p.open(format=self.audio_format, channels=1, rate=self.rate,
                                            input=True,
                                            frames_per_buffer=self.chunk_size)
        while self.MIC_ON == 1:
            try:
                data = self.recording_stream.read(16)
                encrypted_data = self.encryption_handler.aes_encrypt(data)
                self.s.sendto(encrypted_data, self.addr)
            except:
                pass

    def start_voice_call(self):
        print "Starting voice call!"
        receive_thread = threading.Thread(target=self.receive_data)
        receive_thread.start()
        # receive_thread.join()
        # send_thread.join()

    def mic_on(self):
        self.MIC_ON = 1
        send_thread = threading.Thread(target=self.send_data)
        send_thread.start()

    def mic_off(self):
        self.MIC_ON = 0
        self.recording_stream.stop_stream()
        self.recording_stream.close()

    def mic_switch(self):
        if self.MIC_ON == 0:
            print "Your mic is now on!"
            self.mic_on()
        else:
            print "Your mic is now off!"
            self.mic_off()

    def end_voice_call(self):
        self.DONE_STATUS = 1
        self.s.close()
        self.playing_stream.stop_stream()
        self.playing_stream.close()
        self.p.terminate()
