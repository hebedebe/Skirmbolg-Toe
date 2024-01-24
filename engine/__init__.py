import colorama
import pygame
import pygame_gui as gui

import engine.assetloader
from engine.main import *

colorama.init()
pygame.init()

VERSION = "0.1"
NAME = "Cicada"

monitor = get_monitors()[0]
threads = []
manager = Manager("Loading...", monitor.width, monitor.height, fps=1000, flags=pygame.SRCALPHA)
print(f"Initialised {colorama.Fore.LIGHTGREEN_EX + NAME + colorama.Fore.RESET} "
      f"v{VERSION}")

debug = False

INFINITY = float("inf")

VEC2_UP = pygame.Vector2(0, -1)
VEC2_DOWN = pygame.Vector2(0, 1)
VEC2_LEFT = pygame.Vector2(-1, 0)
VEC2_RIGHT = pygame.Vector2(1, 0)
VEC2_ZERO = pygame.Vector2(0, 0)


def add_thread(thread):
    global threads
    threads.append(thread)
    return thread


def join_thread(index, silent=True):
    global threads
    name = threads[index].name
    threads[index].join()
    if not silent:
        print(f"Joined thread {index} [{name}]")


def join_all_threads(silent=True):
    global threads
    for i, t in enumerate(threads):
        join_thread(i, silent)


def delta():
    global manager
    return manager.engine.delta


def get_asset(asset):
    global manager
    return manager.assets.get(asset)


def get_surface():
    return manager.engine.surface


def run(state, title="Untitled", debug_=False):
    global debug
    manager.change_caption(title)
    manager.ui_manager = gui.UIManager((manager.engine.surface.get_width(),
                                        manager.engine.surface.get_height()),
                                       'ui_theme.json')
    if manager.engine.do_display_scaling:
        display = manager.engine.display
        manager.ui_manager.mouse_pos_scale_factor = [
            1920 / display.get_width(),
            1920 / display.get_width()
        ]
        manager.ui_manager.mouse_offset = [
            0.0,
            0.0
        ]
    if debug_:
        manager.ui_manager.set_visual_debug_mode(True)
    debug = debug_
    manager.run(state)
    pygame.quit()
