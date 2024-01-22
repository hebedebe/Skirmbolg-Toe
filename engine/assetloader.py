import glob
import pygame
from colorama import Back, Fore
import time
import colorama

image_types = (".png", ".gif")
sound_types = (".ogg", ".mp3", ".wav")
font_types = (".ttf", ".otf")
font_sizes = (12, 24, 48)


class Assets:
    def __init__(self, asset_path=".\\assets\\auto\\"):
        self.asset_path = asset_path
        self.assets = {}
        self.keys = []
        self.default_image = pygame.image.load("engine/textures/default.png")
        t = time.time()
        for file in glob.glob(asset_path+"*"):
            if file.lower().endswith(image_types):
                name = (file.split("\\")[-1][0:-4]).lower()
                self.assets[name] = pygame.image.load(
                    file).convert_alpha()
                self.keys.append(name)
                print(f"Loaded asset {Fore.YELLOW}{file}{Fore.RESET} (texture) as {Fore.YELLOW}{name}{Fore.RESET}")
            elif file.lower().endswith(sound_types):
                name = (file.split("\\")[-1][0:-4]).lower()
                self.assets[name] = pygame.mixer.Sound(file)
                self.keys.append(name)
                print(f"Loaded asset {Fore.YELLOW}{file}{Fore.RESET} (audio) as {Fore.YELLOW}{name}{Fore.RESET}")
            elif file.lower().endswith(font_types):
                for s in font_sizes:
                    name = (file.split("\\")[-1][0:-4] + f"_{s}").lower()
                    self.assets[name] = pygame.font.Font(file, s)
                    self.keys.append(name)
                    print(f"Loaded asset {Fore.YELLOW}{file}{Fore.RESET} (font) as {Fore.YELLOW}{name}{Fore.RESET}")
        print(f"Finished loading assets ({(time.time()-t)*1000}ms)")

    def get(self, name):
        if name not in self.assets:
            print(f"{Fore.RED}ERROR: Could not get asset named {name}. Reason: not loaded.{Fore.RESET}")
            return self.default_image
        return self.assets[name]

    def load(self, name, asset):
        self.assets[name] = asset
        self.keys.append(name)

    def load_font(self, name, size):
        file = f"{self.asset_path}{name}"
        name = file.split("\\")[-1][0:-4] + f"_{size}"
        self.assets[name] = pygame.font.Font(file, size)
        self.keys.append(name)
        print(f"Loaded asset {Fore.YELLOW}{file}{Fore.RESET} (font) as {Fore.YELLOW}{name}{Fore.RESET}")
