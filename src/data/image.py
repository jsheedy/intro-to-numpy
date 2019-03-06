import os

import numpy as np
from PIL import Image


DATA_DIR = os.path.join(os.path.dirname(__file__), "../../data/")

def image_path_to_numpy(path):
    img = Image.open(DATA_DIR + "earthrise.jpg")
    array = np.array(img)
    return array

def earthrise():
    """
    https://spaceflight.nasa.gov/gallery/images/apollo/apollo8/html/as08-14-2383.html
    https://spaceflight.nasa.gov/gallery/images/apollo/apollo8/hires/as08-14-2383.jpg
    photo credit: Apollo 8
    """
    return image_path_to_numpy(DATA_DIR + "earthrise.jpg")
