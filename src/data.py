
import os

import numpy as np
from PIL import Image


DATA_DIR = os.path.join(os.path.dirname(__file__), "../data/")


def earthrise():
    """
    https://spaceflight.nasa.gov/gallery/images/apollo/apollo8/html/as08-14-2383.html
    https://spaceflight.nasa.gov/gallery/images/apollo/apollo8/hires/as08-14-2383.jpg
    photo credit: Apollo 8
    """
    img = Image.open(DATA_DIR + "earthrise.jpg")
    scaled = img.thumbnail((1000,1000),Image.ANTIALIAS)
    array = np.array(scaled)
    return array

def tuba():
    path = "/Library/Application\ Support/GarageBand/Instrument\ Library/Sampler/Sampler\ Files/Tuba\ Solo/Tuba_stac_ff1/KTU_stac_ff1_C2.wav"
