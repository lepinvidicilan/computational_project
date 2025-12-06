import wave

import matplotlib.pyplot as plt
import numpy as np
import scipy


def cut(x_fft, y_fft, min, max):
    mask = (x_fft > min) * (x_fft < max)
    y = y_fft.copy()
    y[mask] = 0
    return x_fft, y


def get_max_freq(x_fft, y_fft):
    max_intensity_freq = np.where(abs(y_fft) == abs(y_fft).max())
    print(max_intensity_freq)
    return x_fft[max_intensity_freq[0]], y_fft[max_intensity_freq[0]]


def owlbeep_treatment(file_name):
    with wave.open("sounds/" + file_name, "rb") as file:
        metadata = file.getparams()
        frames = file.readframes(metadata.nframes)
        file.close()

    frames = np.frombuffer(frames, dtype=np.int16)
    y_fft = scipy.fft.rfft(frames)
    x_fft = scipy.fft.rfftfreq(len(frames), 1 / metadata.framerate)

    fig = plt.figure()
    fig.suptitle(file_name)
    ax, ax2 = fig.subplots(1, 2)
    ax.plot(x_fft, abs(y_fft))
    ax.set_title("pre cut")
    f0, i0 = get_max_freq(x_fft, y_fft)

    fft_mask = np.zeros_like(x_fft)

    range_arround_the_fn = 30

    for i in range(1, 1000):
        fft_mask[
            (x_fft < (f0 * i + range_arround_the_fn))
            * (x_fft > (f0 * i - range_arround_the_fn))
        ] = 1

    fft_mask = np.bool(fft_mask)

    owl_and_birds = y_fft.copy()
    owl_and_birds[fft_mask] = 0

    fft_mask = np.int8(fft_mask)
    fft_mask += 1
    fft_mask[fft_mask >= 2] = 0
    fft_mask = np.bool(fft_mask)

    beeps = y_fft.copy()
    beeps[fft_mask] = 0

    y_fft[fft_mask] = 0

    ax2.plot(x_fft, abs(beeps))
    ax2.set_title("post cut")

    beeps = scipy.fft.irfft(beeps)
    owl_and_birds = scipy.fft.irfft(owl_and_birds)

    plt.show()

    with wave.open("outputs/beeps.wav", "wb") as file:
        file.setnchannels(1)
        file.setsampwidth(metadata.sampwidth)
        file.setframerate(metadata.framerate)
        file.writeframes(bytes(np.int16(beeps * (32767 / beeps.max()))))
        file.close()

    with wave.open("outputs/owl_and_birds", "wb") as file:
        file.setnchannels(1)
        file.setsampwidth(metadata.sampwidth)
        file.setframerate(metadata.framerate)
        file.writeframes(bytes(np.int16(owl_and_birds * (32767 / owl_and_birds.max()))))
        file.close()


def main(file_name):
    with wave.open("sounds/" + file_name, "rb") as file:
        metadata = file.getparams()
        frames = file.readframes(metadata.nframes)
        file.close()

    with wave.open("outputs/" + file_name, "wb") as file:
        file.setnchannels(1)
        file.setsampwidth(metadata.sampwidth)
        file.setframerate(metadata.framerate)
        # file.writeframes(bytes(np.int16(output_fft * (32767 / output_fft.max()))))
        file.close()


if __name__ == "__main__":
    owlbeep_treatment("owlbeep.wav")
    # for file in os.listdir("sounds/"):
    #     main(file)
