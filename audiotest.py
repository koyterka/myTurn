import pyaudio
import wave

CHUNK = 1024

filename = 'ring_in_call.wav'
wf = wave.open(filename, 'rb')

p = pyaudio.PyAudio()
info = p.get_host_api_info_by_index(0)
numdevices = info.get('deviceCount')

for i in range(0, numdevices):
    if p.get_device_info_by_host_api_device_index(0, i).get('maxInputChannels')>0:
        print 'Input Device id ', i, '-', p.get_device_info_by_host_api_device_index(0,i).get('name')
    if p.get_device_info_by_host_api_device_index(0, i).get('maxOutputChannels') > 0:
        print 'Output Device id ', i, '-', p.get_device_info_by_host_api_device_index(0, i).get('name')

devinfo = p.get_device_info_by_index(0)
# print 'selected devide', devinfo.get('name')
# if p.is_format_supported(44100.0,
#                          input_device=devinfo['index'],
#                         input_channels=devinfo['maxInputChannels'],
#     input_format=pyaudio.paInt16): print 'yes', devinfo['maxInputChannels']

stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                channels=devinfo['maxOutputChannels'],
                rate=44100,
                output=True, output_device_index = 0)

# p.get_format_from_width(wf.getsampwidth()
# wf.getnchannels()
# wf.getframerate()
data = wf.readframes(CHUNK)

while len(data) > 0:
    stream.write(data)
    data = wf.readframes(CHUNK)

stream.stop_stream()
stream.close()

p.terminate()
