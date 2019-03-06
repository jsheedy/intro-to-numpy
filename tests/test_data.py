from src.data import image
from src.data import sound

def test_earthrise():
    img = image.earthrise()
    assert len(img)

def test_wav():
    left, right = sound.wav()
    assert left
    assert right

def test_apollo11():
    stereo = sound.apollo_11()
    assert stereo
