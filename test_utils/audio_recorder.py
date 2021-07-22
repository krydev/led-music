# import numpy as np
# import pyaudio
# import time
# import librosa
#
# class AudioHandler(object):
#     def __init__(self):
#         self.FORMAT = pyaudio.paFloat32
#         self.CHANNELS = 1
#         self.RATE = 44100
#         self.CHUNK = 1024 * 2
#         self.p = None
#         self.stream = None
#
#     def start(self):
#         self.p = pyaudio.PyAudio()
#         self.stream = self.p.open(format=self.FORMAT,
#                                   channels=self.CHANNELS,
#                                   rate=self.RATE,
#                                   input=True,
#                                   output=False,
#                                   stream_callback=self.callback,
#                                   frames_per_buffer=self.CHUNK)
#
#     def stop(self):
#         self.stream.close()
#         self.p.terminate()
#
#     def callback(self, in_data, frame_count, time_info, flag):
#         numpy_array = np.frombuffer(in_data, dtype=np.float32)
#         librosa.feature.mfcc(numpy_array)
#         return None, pyaudio.paContinue
#
#     def mainloop(self):
#         while (self.stream.is_active()): # if using button you can set self.stream to 0 (self.stream = 0), otherwise you can use a stop condition
#             time.sleep(2.0)
#
#
# audio = AudioHandler()
# audio.start()     # open the the stream
# audio.mainloop()  # main operations with librosa
# audio.stop()

import pyaudio
import wave

FORMAT = pyaudio.paInt16
CHANNELS = 2
RATE = 44100
CHUNK = 1024
RECORD_SECONDS = 5
WAVE_OUTPUT_FILENAME = "file.wav"

audio = pyaudio.PyAudio()

# start Recording
stream = audio.open(format=FORMAT, channels=CHANNELS,
                    rate=RATE, input=True, input_device_index=5,
                    frames_per_buffer=CHUNK)
print("start")
frames = []

for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
    data = stream.read(CHUNK, exception_on_overflow = False)
    frames.append(data)
print("finish")
# stop Recording
stream.stop_stream()
stream.close()
audio.terminate()

waveFile = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
waveFile.setnchannels(CHANNELS)
waveFile.setsampwidth(audio.get_sample_size(FORMAT))
waveFile.setframerate(RATE)
waveFile.writeframes(b''.join(frames))
waveFile.close()
