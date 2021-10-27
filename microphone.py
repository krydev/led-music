import matplotlib
# matplotlib.use('Agg')
import numpy as np
import pyaudio
import time
import librosa
import matplotlib.pyplot as plt
from matplotlib import style

from cmds import set_rgb_color


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
        onset_env = librosa.onset.onset_strength(y=y, sr=self.RATE, n_fft=self.CHUNK, aggregate=np.median)
        normalized_onset = librosa.util.normalize(onset_env)
        pulse = librosa.beat.plp(onset_envelope=onset_env, sr=self.RATE, win_length=self.CHUNK//2)
        beats_plp = np.flatnonzero(librosa.util.localmax(pulse))
        return normalized_onset, beats_plp
