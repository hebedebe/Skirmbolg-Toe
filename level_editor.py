import random
import sys

import pygame.mouse

import engine
from engine import settings
import main


class Editor(engine.State):
    def on_update(self):
        super().on_update()

    def on_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.add_object("platform creator", PlatformCreator(pygame.mouse.get_pos()))
            print("added platform creator")
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                level_name = input("Level name (x_y): ")
                level_data = {
                    "name": level_name,
                    "level": [],
                    "level_late": [],
                    "spawn_positions": {
                        "default": [500, 500]
                    }
                }
                path = f"gamedata/levels/{level_name}.json"
                for i, (k, o) in enumerate(self.objects):
                    name = o.__name__



def class_to_string():
    return


class PlatformCreator(engine.TickableEntity):
    def __init__(self, pos):
        self.pos = [*pos]
        self.width = 0
        self.height = 0
        self.enabled = True

    def update(self, *args):
        if self.enabled:
            scene = args[0]

            if pygame.mouse.get_pressed()[0]:
                mouse_pos = pygame.mouse.get_pos()
                self.width = mouse_pos[0] - self.pos[0]
                self.height = mouse_pos[1] - self.pos[1]
            else:
                scene.add_buffered_object(random.randint(0, 1000), main.Platform(self.pos, (self.width, self.height)))
                self.enabled = False

            draw_rect = pygame.Rect(self.pos, (self.width, self.height))
            pygame.draw.rect(engine.get_surface(), 'red', draw_rect, 1)


if __name__ == "__main__":
    settings.checkAndMakeSettings()
    engine.manager.make_fullscreen()
    engine.run(Editor(engine.manager), "Level Editor", debug_=("debug" in sys.argv))
