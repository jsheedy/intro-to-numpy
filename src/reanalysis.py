"""
SDL NCEP Reanalysis browser
joseph.sheedy@gmail.com

data from
ftp://ftp.cdc.noaa.gov/Datasets/ncep.reanalysis/pressure/
https://www.esrl.noaa.gov/psd/data/gridded/data.ncep.reanalysis.html
ftp://ftp.cdc.noaa.gov/Datasets/ncep.reanalysis/pressure/hgt.2018.nc
"""

import ctypes
import functools
import os
import sys
from types import SimpleNamespace

import cartopy
import matplotlib
import numpy as np
import sdl2.ext
import xarray


LON, LAT = 144,73
SCALE = 10
WIDTH = LON * SCALE
HEIGHT = LAT * SCALE


def project(coords):
    """ 💕 equirectangular """
    lon = coords[:, 0]
    lat = coords[:, 1]
    xy = np.zeros(coords.shape, dtype=np.int32)
    x = ((lon + 180) / 360) * (WIDTH-1)
    y = (HEIGHT-1) - ((lat + 90) / 180) * (HEIGHT-1)
    xy[:,0] = x
    xy[:,1] = y
    return xy


@functools.lru_cache()
def overlay():
    lines = []
    for mls in cartopy.feature.COASTLINE.geometries():
        for geom in mls.geoms:
            coords = geom.coords
            xy = project(np.array(coords))
            geom_lines = np.hstack((xy[:-1],xy[1:])).flatten()
            lines.append(geom_lines.tolist())
    return lines


def draw_coastline(renderer):
    for lines in overlay():
        renderer.draw_line(lines)


def normalize(grid):
    """ normalize grid to (0,1) """
    field = grid.T.values
    min_h, max_h = field.min(), field.max()
    return (field - min_h) / (max_h - min_h)


def print_status(t, value, level):

    ts = str(ds.time[t].values)[:16]
    rows, _columns = map(int, os.popen('stty size', 'r').read().split())
    row = rows
    column = 1
    sys.stdout.write(
        "\x1b[s" +  # save Cursor Position
        f"\x1b[{row};{column}H" + # CUP - Cursor Position
        f"\x1b[38;2;{255};{255};{255}m" + #foreground
        f"\x1b[48;2;{25};{25};{0}m" + #background
        f"{ts} Geopotential Height: {value}m Level: {level}mb    " +   # restore Cursor Position
        "\x1b[u"
    )
    sys.stdout.flush()


@functools.lru_cache()
def canvas(shape):
    return np.ones(shape=(shape + (3,)))


def draw(pixels, renderer, grid):
    hsv = canvas(grid.shape)
    hsv[:,:, 0] = grid  # set hue
    rgb = matplotlib.colors.hsv_to_rgb(hsv)
    rgb = (rgb * 255).astype(np.uint32)
    r,g,b = rgb[:,:,0], rgb[:,:,1], rgb[:,:,2]

    # convert to SDL color 32bit BGRA format
    x = 0xff000000 | (r << 16) | (g << 8) | b
    # scale up to window size
    x = np.repeat(x, SCALE, axis=1)
    x = np.repeat(x, SCALE, axis=0)
    pixels[:,:] = x


def handle_events(state):
    events = sdl2.ext.get_events()
    for event in events:
        if event.type == sdl2.SDL_KEYDOWN:
            if event.key.keysym.sym == 32:  # space
                state.paused = not state.paused
            elif event.key.keysym.sym == 61:  # +
                if state.speed < 0.001:
                    state.speed += 0.0000025
            elif event.key.keysym.sym == 45:  # -
                state.speed -= 0.0000025
                if state.speed < 0:
                    state.speed = 0
            elif event.key.keysym.sym == 113:  # q
                state.running = False

        elif event.type == sdl2.SDL_MOUSEMOTION:
            x, y = ctypes.c_int(0), ctypes.c_int(0) # Create two ctypes values
            _buttonstate = sdl2.mouse.SDL_GetMouseState(ctypes.byref(x), ctypes.byref(y))
            state.joystick.y = y.value / HEIGHT
            state.joystick.x = x.value / WIDTH
            if not state.paused:
                state.t = state.joystick.y

        elif event.type == sdl2.SDL_QUIT:
            state.running = False
            break


def sdl_init():
    sdl2.ext.init()
    window = sdl2.ext.Window("reanalyis", size=(WIDTH, HEIGHT))
    window.show()
    surface = window.get_surface()
    pixels = sdl2.ext.pixels2d(surface)
    renderer = sdl2.ext.Renderer(surface, flags=sdl2.SDL_RENDERER_ACCELERATED)
    renderer.blendmode = sdl2.SDL_BLENDMODE_MOD
    return window, renderer, pixels


def render(ds):

    window, renderer, pixels = sdl_init()

    pixels[:,:] = 0xffffffff
    draw_coastline(renderer)
    coastline_mask = pixels < 0xffffffff

    state = SimpleNamespace(
        running=True,
        paused=True,
        speed=0.000005,
        t=0,
        l=0,
        joystick = SimpleNamespace(
            x=0,
            y=0
        )
    )

    while state.running:
        handle_events(state)
        if not state.paused:
            state.t += state.speed
            state.t = state.t % 1

        state.l = int(state.joystick.x * len(ds.level))
        t = int(state.t * len(ds.time))
        grid = ds['hgt'][t,state.l]
        normalized_grid = normalize(grid)
        draw(pixels, renderer, normalized_grid)
        pixels[coastline_mask] = 0xff000000
        window.refresh()

        i = int(state.joystick.y * LAT)
        j = int(state.joystick.x * LON)
        height = int(grid[i, j].values)
        level = int(ds['level'][state.l].values)
        print_status(t, height, level)
        sdl2.SDL_Delay(5)

    sdl2.ext.quit()


if __name__ == "__main__":
    ds = xarray.open_dataset('../../data/reanalysis.hgt.1948-2019.nc', chunks={'time': 10000})
    render(ds)
