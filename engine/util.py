from threading import Thread
import pygame
from samplerate import resample
import random
import sys

import engine.settings
import engine


class ThreadWithReturnValue(Thread):

    def __init__(self, group=None, target=None, name=None,
                 args=(), kwargs=None, Verbose=None):
        Thread.__init__(self, group, target, name, args, kwargs)
        if kwargs is None:
            kwargs = {}
        self._return = None

    def run(self):
        if self._target is not None:
            self._return = self._target(*self._args,
                                        **self._kwargs)

    def join(self, *args):
        Thread.join(self, *args)
        return self._return


# Stolen from DaFluffyPotato
def clip(surface, x, y, x_size, y_size):  # Get a part of the image
    handle_surface = surface.copy()  # Sprite that will get process later
    clip_rect = pygame.Rect(x, y, x_size, y_size)  # Part of the image
    handle_surface.set_clip(clip_rect)  # Clip or you can call cropped
    image = surface.subsurface(handle_surface.get_clip())  # Get subsurface
    return image.copy()


def play_sound(sound: pygame.mixer.Sound):
    volume = engine.settings.getConfig().getfloat("volume", "master") / 100
    sound.set_volume(volume)
    sound.play()


def get_pitched_sound(sound: pygame.mixer.Sound, pitch_mod: float):
    snd_array = pygame.sndarray.array(sound)
    snd_resample = resample(sound, pitch_mod).astype(snd_array.dtype)
    snd_out = pygame.sndarray.make_sound(snd_resample)
    return snd_out


def play_pitched_sound(sound: pygame.mixer.Sound, pitch_mod: float):
    thread = Thread(target=_play_pitched_sound, args=(sound, pitch_mod))
    engine.add_thread(thread)
    thread.daemon = True
    thread.start()


def _play_pitched_sound(sound, pitch_mod):
    play_sound(get_pitched_sound(sound, pitch_mod))


def play_randomly_pitched_sound(sound: pygame.mixer.Sound, pitch_mod_range=None):
    if pitch_mod_range is None:
        pitch_mod_range = [0.8, 1.2]
    play_pitched_sound(sound, random.uniform(*pitch_mod_range))


def draw_polygon_alpha(surface, color, points):
    lx, ly = zip(*points)
    min_x, min_y, max_x, max_y = min(lx), min(ly), max(lx), max(ly)
    target_rect = pygame.Rect(min_x, min_y, max_x - min_x, max_y - min_y)
    shape_surf = pygame.Surface(target_rect.size, pygame.SRCALPHA)
    pygame.draw.polygon(shape_surf, color, [(x - min_x, y - min_y) for x, y in points])
    surface.blit(shape_surf, target_rect)


def draw_circle_alpha(surface, color, center, radius):
    target_rect = pygame.Rect(center, (0, 0)).inflate((radius * 2, radius * 2))
    shape_surf = pygame.Surface(target_rect.size, pygame.SRCALPHA)
    pygame.draw.circle(shape_surf, color, (radius, radius), radius)
    surface.blit(shape_surf, target_rect)


def draw_rect_alpha(surface, color, rect):
    shape_surf = pygame.Surface(pygame.Rect(rect).size, pygame.SRCALPHA)
    pygame.draw.rect(shape_surf, color, shape_surf.get_rect())
    surface.blit(shape_surf, rect)