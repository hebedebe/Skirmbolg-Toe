import pygame
from pygame import Vector2
import sys

import engine
from engine import settings
import main


class Editor(engine.State):
    def on_update(self):
        super().on_update()

    def on_event(self, event):
        global start_pos
        if event.type == pygame.MOUSEBUTTONDOWN:
            start_pos = pygame.mouse.get_pos()


selected_type = main.Platform
start_pos = Vector2(0, 0)

if __name__ == "__main__":
    settings.checkAndMakeSettings()
    engine.manager.make_fullscreen()
    engine.run(Editor(engine.manager), "Level Editor", debug_=("debug" in sys.argv))
