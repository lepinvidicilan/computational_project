import wave

import matplotlib.pyplot as plt
import numpy as np
import scipy
import simpleaudio as sa
from matplotlib.animation import FuncAnimation
from tqdm import tqdm


def write_file(datas, name, metadata):
    with wave.open(name, "wb") as file:
        file.setnchannels(1)
        file.setsampwidth(metadata.sampwidth)
        file.setframerate(metadata.framerate)
        file.writeframes(bytes(np.int16(datas * (32767 / datas.max()))))
        file.close()


def cut(x_fft, y_fft, min, max):
    mask = (x_fft > min) * (x_fft < max)
    y = y_fft.copy()
    y[mask] = 0
    return x_fft, y


def get_max_freq(x_fft, y_fft):
    max_intensity_freq = np.where(abs(y_fft) == abs(y_fft).max())
    return x_fft[max_intensity_freq[0]], y_fft[max_intensity_freq[0]]


def temporal_analyse(frames, metadata):
    interval = 2000
    fig, ax = plt.subplots()
    all = []

    x_fft = scipy.fft.rfftfreq(len(frames[0 : 0 + interval]), 1 / metadata.framerate)

    for frame in tqdm(range(0, len(frames) - interval - 1, interval)):
        y_fft = scipy.fft.rfft(frames[frame : frame + interval])
        all.append(y_fft)
    all = np.array(all)
    print(all.shape)

    def animate(frame):
        play_obj = sa.play_buffer(
            scipy.fft.irfft(all[frame]).astype(np.int16), 1, 2, 44100
        )
        play_obj.wait_done()
        ax.clear()
        ax.plot(x_fft, abs(all[frame]))

    anim = FuncAnimation(fig, animate, interval=0.01, frames=len(all))

    # ax.plot(x_fft, all[::], np.linspace(0, 1 / 44100, len(all)))
    plt.show()


def main(file_name):
    with wave.open("sounds/" + file_name, "rb") as file:
        metadata = file.getparams()
        frames = file.readframes(metadata.nframes)
        nframes = file.getnframes()
        rate = file.getframerate()
        file.close()

    frames = np.frombuffer(frames, dtype=np.int16)
    y_fft = scipy.fft.rfft(frames)
    x_fft = scipy.fft.rfftfreq(len(frames), 1 / metadata.framerate)

    print(frames)

    # temporal_analyse(frames, metadata)

    print(nframes)

    plt.plot(frames)
    # plt.show()

    print(x_fft[-1] / x_fft.shape[0])
    print(x_fft[-1])

    fig1, fig2, fig3, fig4, fig1p5 = (
        plt.figure(),
        plt.figure(),
        plt.figure(),
        plt.figure(),
        plt.figure(),
    )
    # fig.suptitle(file_name)
    ax, ax2, ax3, ax4, ax1p5 = (
        fig1.add_subplot(),
        fig2.add_subplot(),
        fig3.add_subplot(),
        fig4.add_subplot(),
        fig1p5.add_subplot(),
    )
    ax.plot(x_fft, abs(y_fft))
    ax.set_title("pre cut")
    f0, i = get_max_freq(x_fft, y_fft)

    fft_mask = np.zeros_like(x_fft)

    range_arround_the_fn = 40
    imax = (np.int16(x_fft[-1] / f0) + 1)[0]

    for i in range(1, imax):
        fft_mask[
            (x_fft < (f0 * i + range_arround_the_fn))
            * (x_fft > (f0 * i - range_arround_the_fn))
        ] = 1

    fft_mask = np.bool(fft_mask)

    owl_and_birds = y_fft.copy()
    owl_and_birds[fft_mask] = 0
    ax1p5.plot(x_fft, abs(owl_and_birds))
    ax1p5.set_title("without beeps")

    rest = y_fft.copy()
    rest[fft_mask] = 0

    fft_mask = np.int8(fft_mask)
    fft_mask += 1
    fft_mask[fft_mask >= 2] = 0
    fft_mask = np.bool(fft_mask)

    beeps = y_fft.copy()
    beeps[fft_mask] = 0

    y_fft[fft_mask] = 0
    # x_fft, owl_and_birds = cut(x_fft, owl_and_birds, 400, np.inf)
    #
    # x_fft, owl_and_birds = cut(x_fft, owl_and_birds, -np.inf, 20)

    for i in range(1):
        fft_mask = np.zeros_like(x_fft)
        f0, i0 = get_max_freq(x_fft, owl_and_birds)

        fft_mask[(x_fft < (f0 + 20)) * (x_fft > (f0 - 50))] = 1
        print(fft_mask)

        fft_mask = np.int8(fft_mask)
        fft_mask += 1
        fft_mask[fft_mask >= 2] = 0
        fft_mask = np.bool(fft_mask)
        owl_and_birds[fft_mask] = 0

    ax2.plot(x_fft, abs(owl_and_birds))
    ax2.set_title("Owl")
    ax2.set_xlim(f0 - 50, f0 + 20)

    ax3.plot(x_fft, abs(beeps))
    ax3.set_title("Beeps")

    fft_mask = np.int8(fft_mask)
    fft_mask += 1
    fft_mask[fft_mask >= 2] = 0
    fft_mask = np.bool(fft_mask)

    rest[fft_mask] = 0

    ax4.plot(x_fft, abs(rest))
    ax4.set_title("Rest")

    beeps = scipy.fft.irfft(beeps)
    owl_and_birds = scipy.fft.irfft(owl_and_birds)
    rest = scipy.fft.irfft(rest)

    ax.set_xlim(0, 10000)
    ax3.set_xlim(0, 10000)
    ax4.set_xlim(-500, 10000)

    fig1.savefig("figures/figure_1.png")
    fig1p5.savefig("figures/figure_1p5.png")
    fig2.savefig("figures/figure_2.png")
    fig3.savefig("figures/figure_3.png")
    fig4.savefig("figures/figure_4.png")

    # plt.show()

    write_file(beeps, "outputs/beeps.wav", metadata)
    write_file(owl_and_birds, "outputs/owl.wav", metadata)
    write_file(rest, "outputs/rest.wav", metadata)


if __name__ == "__main__":
    main("owlbeep.wav")
