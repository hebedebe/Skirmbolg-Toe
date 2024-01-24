from configparser import ConfigParser
import pygame

SETTINGS_PATH = "./gamedata/settings/settings.ini"

DEFAULT_CONTENTS = """
[display]
fullscreen = True

[volume]
master = 100.0
music = 50.0
"""

config = ConfigParser()

config.read(SETTINGS_PATH)

print("Settings loaded.")


def checkAndMakeSettings(default_contents=DEFAULT_CONTENTS):
    try:
        f = open(SETTINGS_PATH, "r")
        f.close()
        print("Settings file detected")
    except FileNotFoundError:
        print("Failed to detect settings file")
        with open(SETTINGS_PATH, "a") as file:
            file.write(default_contents)
            print("Settings file created")


def save():
    global config
    pygame.mixer_music.set_volume(config.getfloat("volume", "music")/100)
    with open(SETTINGS_PATH, "w") as file:
        config.write(file)


def getConfig():
    return config
