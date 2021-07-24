import matplotlib
# matplotlib.use('Agg')
import numpy as np
import pyaudio
import time
import librosa
import matplotlib.pyplot as plt
from matplotlib import style

class AudioHandler(object):
    def __init__(self):
        self.FORMAT = pyaudio.paFloat32
        self.CHANNELS = 1
        self.RATE = 44100
        self.CHUNK = 1024 * 2
        self.p = None
        self.stream = None
        self.mel_freqs = librosa.mel_frequencies()
        self.S_dB = None


    def start(self):
        self.p = pyaudio.PyAudio()
        self.stream = self.p.open(format=self.FORMAT,
                                  channels=self.CHANNELS,
                                  rate=self.RATE,
                                  input=True,
                                  output=False,
                                  input_device_index=5,
                                  frames_per_buffer=self.CHUNK)

    def stop(self):
        self.stream.close()
        self.p.terminate()

    def callback(self, in_data):
        y = np.frombuffer(in_data, dtype=np.float32)
        onset_env = librosa.onset.onset_strength(y=y, sr=self.RATE)
        # S = librosa.feature.melspectrogram(y=y, sr=self.RATE, n_fft=self.CHUNK)
        # S_dB = librosa.power_to_db(S, ref=np.max)
        times = librosa.times_like(onset_env, sr=self.RATE)
        ln.set_data(times, librosa.util.normalize(onset_env))
        # for i in range(S_dB.shape[1]):
        #     ydata = S_dB[:, i].reshape(-1)
        #     ln.set_data(self.mel_freqs, ydata)
        #     ax.relim()
        #     ax.autoscale_view()
        #     fig.canvas.draw()
        #     # plt.pause(0.05)
        #     fig.canvas.flush_events()


    def mainloop(self):
        # plt.xlim(self.mel_freqs[0], self.mel_freqs[-1])
        # plt.ylim(-80, 80)
        while (self.stream.is_active()):
            data = self.stream.read(self.CHUNK, exception_on_overflow=False)
            self.callback(data)


plt.ion() # Stop matplotlib windows from blocking
fig, ax = plt.subplots()
ln, = ax.plot([], [], label='Onset strength')

audio = AudioHandler()
audio.start()     # open the the stream
audio.mainloop()  # main operations with librosa
audio.stop()