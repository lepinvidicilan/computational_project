import array
import sys
import wave

import matplotlib.pyplot as plt
import numpy as np
import scipy.fft as fft

# %matplotlib qt

# %matplotlib inline


def remove_range(min=2000, max=100000):
    for n in range(len(xf)):
        if abs(xf[n]) > min and abs(xf[n]) < max:
            yf[n] = 0


# load the sound file... must be .wav

with wave.open("./sounds/OSR_us_000_0011_8k.wav") as wav_file:
    # with wave.open("OSR_us_000_0010_8k.wav") as wav_file:

    metadata = wav_file.getparams()

    frames = wav_file.readframes(metadata.nframes)


print(metadata)

# _wave_params(

#     nchannels=1,

#     sampwidth=2,

#     framerate=44100,

#     nframes=212419,

#     comptype='NONE',

#     compname='not compressed'

# )


# >>> import array

# >>> pcm_samples = array.array("h", frames)

# >>> len(pcm_samples)

# 212419

if metadata.sampwidth == 2:
    pcm_samples = array.array("h", frames)

else:
    print("sorry I can't handle sampwidth =", metadata.sampwidth, " at the moment")

    sys.exit()

# print(frames)

# >>> frames

# b'\x01\x00\xfe\xff\x02\x00\xfe\xff\x01\x00\x01\x00\xfe\xff\x02\x00...'


# >>> len(frames)

# 424838


time = np.arange(
    0, (len(frames) / metadata.sampwidth) / metadata.framerate, 1 / metadata.framerate
)

print(len(frames), len(pcm_samples), len(time))


# sys.exit()


plt.figure()

plt.plot(time, pcm_samples)
plt.title("pure simple")

plt.show()


# yf= fft.fft(pcm_samples)

# xf=fft.fftfreq(len(pcm_samples),1/metadata.framerate)

## could use rfft and rfftfreq for signals with real data

##

yf = fft.rfft(pcm_samples)

xf = fft.rfftfreq(len(pcm_samples), 1 / metadata.framerate)


plt.figure()

plt.plot(xf, np.abs(yf))
plt.title("fft")
# plt.xrange([0,])

plt.show()


def cut(min, max):
    for n in range(len(xf)):
        if abs(xf[n]) > min and abs(xf[n]) < max:
            yf[n] = 0


cut(-1, 1000)
# cut(260, 360)

plt.figure()

plt.plot(xf, np.abs(yf))

# plt.xrange([0,])

plt.show()


# newframes = fft.ifft(yf)

newframes = fft.irfft(yf)


print(newframes)


# norm_new_sig = np.int16(new_sig * (32767 / new_sig.max()))

# write("clean.wav", SAMPLE_RATE, norm_new_sig)


norm_new_sig = np.int16(newframes * (32767 / newframes.max()))

# wave.write("cleaned.wav", metadata.framerate, norm_new_sig)


# with wave.open("output.wav", mode="wb") as wav_file:

#     wav_file.setnchannels(1)

#     wav_file.setsampwidth(1)

#     wav_file.setframerate(FRAMES_PER_SECOND)

#     wav_file.writeframes(bytes(sound_wave(440, 2.5)))

with wave.open("output.wav", mode="wb") as wav_file:
    wav_file.setnchannels(1)

    wav_file.setsampwidth(metadata.sampwidth)

    wav_file.setframerate(metadata.framerate)

    wav_file.writeframes(bytes(norm_new_sig))
