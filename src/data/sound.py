import wave
import struct


def wav(path ="/Library/Application Support/GarageBand/Instrument Library/Sampler/Sampler Files/Tuba Solo/Tuba_stac_ff1/KTU_stac_ff1_C2.wav", max_frames=8*(10**6)
):
    """ returns left and right channels of wave data from path as tuples
    only supports 2 channel 16 bit PCM """

    with wave.open(path) as f:
        width = f.getsampwidth()
        n_channels = f.getnchannels()
        n_frames = min((max_frames,f.getnframes()))

        if width != 2 or n_channels != 2:
            raise Exception("only 16 bit stereo PCM supported")

        fmt = 'hh'
        frames = struct.unpack(fmt*n_frames, f.readframes(n_frames))
        left = frames[0::2]
        right = frames[1::2]
        return left, right

def apollo_11():
    # Apollo 11 landing audio
    # https://ia801409.us.archive.org/5/items/Apollo11Audio/938-AAG.wav
    # https://archive.org/details/Apollo11Audio/938-AAG.wav
    # trimmed and converted 24->16 bit:
    # sox 938-AAG.wav -b 16 938-AAG_16bit.wav trim 5:00 15:00
    path = "data/938-AAG_16bit.wav"
    return wav(path)
