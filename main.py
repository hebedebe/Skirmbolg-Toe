import copy
import json
import math
import os
import pickle
import random
import sys
from array import array

import pygame
import pygame.geometry
import pygame_gui as gui
from pygame import Vector2

import engine
import engine.math
from engine import settings
from engine.util import play_randomly_pitched_sound

try:
    import pyi_splash

    pyi_splash.update_text("Loading...")
    pyi_splash.close()
except ModuleNotFoundError:
    print("Not a pyinstaller program")

TITLE = "Skirmbolg & Toe"

BACKGROUND_COLOUR = (24, 20, 37)

cached_scene = None


class MainMenu(engine.State):
    def on_init(self, *args):
        self.background_colour = (0, 0, 0)
        self.add_object("particle manager", engine.ParticleManager())

        self.add_object("background", engine.Sprite(
            "title_background",
            [0, 0]
        ))

        self.add_object("skirmbolg", engine.Animation(
            "assets/skirmbolg/idle",
            pos=[1920 / 2 - 50, 950]
        ))

        self.add_object("toe", engine.Animation(
            "assets/toe/idle",
            pos=[1920 / 2 + 50, 978]
        ))

        self.add_object("title_logo", engine.Sprite(
            "title",
            (0, 0)
        ))

    def on_focus(self):
        ui_manager = self.manager.ui_manager
        self.add_object("play button", gui.elements.UIButton(
            relative_rect=pygame.Rect(0, 0, 100, 50),
            text='Play',
            manager=ui_manager,
            anchors={'center': 'center'},

        ))
        self.add_object("settings button", gui.elements.UIButton(
            relative_rect=pygame.Rect(0, 100, 100, 50),
            text='Settings',
            manager=ui_manager,
            anchors={'center': 'center'}
        ))
        self.add_object("quit button", gui.elements.UIButton(
            relative_rect=pygame.Rect(0, 200, 100, 50),
            text='Quit',
            manager=ui_manager,
            anchors={'center': 'center'}
        ))

    def on_event(self, event):
        if event.type == gui.UI_BUTTON_PRESSED:
            if event.ui_element == self.objects["play button"]:
                self.manager.set_state(CharacterSelect(self.manager))
            elif event.ui_element == self.objects["settings button"]:
                self.manager.set_state(SettingsMenu(self.manager))
            elif event.ui_element == self.objects["quit button"]:
                self.manager.quit()
        elif event.type == gui.UI_BUTTON_ON_HOVERED:
            play_randomly_pitched_sound(engine.get_asset("button_hover"))


class PauseMenu(engine.State):
    def on_init(self, *args):
        self.background_colour = BACKGROUND_COLOUR
        self.add_object("particle manager", engine.ParticleManager())

        self.add_object("background", engine.Sprite(
            "paused_background",
            [0, 0]
        ))

    def on_focus(self):
        ui_manager = self.manager.ui_manager
        self.add_object("resume button", gui.elements.UIButton(
            relative_rect=pygame.Rect(0, 0, 100, 50),
            text='Resume',
            manager=ui_manager,
            anchors={'center': 'center'},

        ))
        self.add_object("main menu button", gui.elements.UIButton(
            relative_rect=pygame.Rect(0, 100, 100, 50),
            text='Main Menu',
            manager=ui_manager,
            anchors={'center': 'center'}
        ))
        self.add_object("quit button", gui.elements.UIButton(
            relative_rect=pygame.Rect(0, 200, 100, 50),
            text='Quit',
            manager=ui_manager,
            anchors={'center': 'center'}
        ))

    def on_event(self, event):
        global cached_scene
        if event.type == gui.UI_BUTTON_PRESSED:
            if event.ui_element == self.objects["main menu button"]:
                self.manager.set_state(MainMenu(self.manager))
            elif event.ui_element == self.objects["resume button"]:
                engine.manager.set_state(cached_scene)
            elif event.ui_element == self.objects["quit button"]:
                self.manager.quit()
        elif event.type == gui.UI_BUTTON_ON_HOVERED:
            play_randomly_pitched_sound(engine.get_asset("button_hover"))
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                engine.manager.set_state(cached_scene)

    def on_update(self):
        super().on_update()


class CharacterSelect(engine.State):
    def on_init(self, *args):
        self.background_colour = BACKGROUND_COLOUR

        self.add_object("skirmbolg_select", engine.Sprite(
            "skirmbolg_character_select"
        ))

        self.add_object("toe_select", engine.Sprite(
            "toe_character_select",
            [960, 0]
        ))

        self.add_object("background", engine.Sprite(
            "character_select_background"
        ))

    def on_focus(self):
        ui_manager = self.manager.ui_manager
        self.add_object("skirmbolg button", gui.elements.UIButton(
            relative_rect=pygame.Rect(-150, 0, 100, 50),
            text='Skirmbolg',
            manager=ui_manager,
            anchors={'center': 'center'}
        ))

        self.add_object("toe button", gui.elements.UIButton(
            relative_rect=pygame.Rect(150, 0, 100, 50),
            text='Toe',
            manager=ui_manager,
            anchors={'center': 'center'}
        ))

        self.add_object("back button", gui.elements.UIButton(
            relative_rect=pygame.Rect(0, 100, 100, 50),
            text='Back',
            manager=ui_manager,
            anchors={'center': 'center'}
        ))

        self.add_object("quit button", gui.elements.UIButton(
            relative_rect=pygame.Rect(0, 200, 100, 50),
            text='Quit',
            manager=ui_manager,
            anchors={'center': 'center'}
        ))

    def on_update(self):
        super().on_update()
        toe_sprite: engine.Sprite = self.objects["toe_select"]
        skirmbolg_sprite: engine.Sprite = self.objects["skirmbolg_select"]

        mouse_pos = Vector2(pygame.mouse.get_pos())
        surf_center = engine.get_surface().get_width() / 2

        if mouse_pos.x > surf_center + 80:
            toe_sprite.image = "toe_character_select_hovered"
            skirmbolg_sprite.image = "skirmbolg_character_select"
        elif mouse_pos.x < surf_center - 80:
            skirmbolg_sprite.image = "skirmbolg_character_select_hovered"
            toe_sprite.image = "toe_character_select"
        else:
            toe_sprite.image = "toe_character_select"
            skirmbolg_sprite.image = "skirmbolg_character_select"

    def on_event(self, event):
        if event.type == gui.UI_BUTTON_PRESSED:
            if event.ui_element == self.objects["skirmbolg button"]:
                engine.manager.globals["player type"] = 0
                start_level = load_json_level("gamedata/levels/level/10_10.json")
                self.manager.set_state(start_level)
            elif event.ui_element == self.objects["toe button"]:
                engine.manager.globals["player type"] = 1
                start_level = load_json_level("gamedata/levels/level/10_10.json")
                self.manager.set_state(start_level)
            elif event.ui_element == self.objects["back button"]:
                self.manager.set_state(MainMenu(self.manager))
            elif event.ui_element == self.objects["quit button"]:
                self.manager.quit()
        elif event.type == gui.UI_BUTTON_ON_HOVERED:
            play_randomly_pitched_sound(engine.get_asset("button_hover"))


class SettingsMenu(engine.State):
    def on_init(self, *args):
        self.background_colour = BACKGROUND_COLOUR
        self.add_object("titles", engine.Sprite(
            "settings",
            [0, 0]
        ))

    def on_focus(self):
        ui_manager = self.manager.ui_manager
        self.add_object(
            "master volume slider",
            gui.elements.UIHorizontalSlider(
                relative_rect=pygame.Rect(0, -135, 300, 30),
                start_value=settings.getConfig().getfloat("volume", "master"),
                value_range=(0, 100),
                manager=ui_manager,
                anchors={'center': 'center'}
            )
        )

        self.add_object(
            "music volume slider",
            gui.elements.UIHorizontalSlider(
                relative_rect=pygame.Rect(0, 10, 300, 30),
                start_value=settings.getConfig().getfloat("volume", "music"),
                value_range=(0, 100),
                manager=ui_manager,
                anchors={'center': 'center'}
            )
        )

        self.add_object("back button", gui.elements.UIButton(
            relative_rect=pygame.Rect(0, 100, 100, 50),
            text='Back',
            manager=ui_manager,
            anchors={'center': 'center'}
        ))

        self.add_object("quit button", gui.elements.UIButton(
            relative_rect=pygame.Rect(0, 200, 100, 50),
            text='Quit',
            manager=ui_manager,
            anchors={'center': 'center'}
        ))

    def on_update(self):
        super().on_update()
        settings.getConfig().set("volume", "master",
                                 str(self.objects["master volume slider"].get_current_value()))
        settings.getConfig().set("volume", "music",
                                 str(self.objects["music volume slider"].get_current_value()))
        pygame.mixer_music.set_volume(engine.settings.getConfig().getfloat("volume", "music") / 100)

    def on_leave(self):
        settings.save()
        self.cleanup()

    def on_event(self, event):
        if event.type == gui.UI_BUTTON_PRESSED:
            if event.ui_element == self.objects["back button"]:
                self.manager.set_state(MainMenu(self.manager))
            elif event.ui_element == self.objects["quit button"]:
                self.manager.quit()
        elif event.type == gui.UI_BUTTON_ON_HOVERED:
            play_randomly_pitched_sound(engine.get_asset("button_hover"))


class Level(engine.State):
    def __init__(self, manager):
        self.spawn_positions = {}
        self.position = None
        super().__init__(manager)
        self.add_object("background", engine.Sprite("background1", (0, 0)))
        self.add_object("particle manager", engine.ParticleManager())

    def addPlayer(self, selection, pos=(500, 500)):
        match selection:
            case 0:  # Skirmbolg
                player = Player(pos)
                player.pos[1] -= player.size[1]
                self.add_phys_object("player", player)
            case 1:  # Toe
                player = Player(pos, (33, 49))
                player.pos[1] -= player.size[1]
                player.idle_anim_left = engine.Animation("assets/toe/idle").flip()
                player.idle_anim_right = engine.Animation("assets/toe/idle")
                player.walk_anim_left = engine.Animation("assets/toe/walk").flip()
                player.walk_anim_right = engine.Animation("assets/toe/walk")
                player.jump_anim = engine.Animation("assets/toe/jump")
                player.fall_anim = engine.Animation("assets/toe/fall")
                self.add_phys_object("player", player)

    def on_event(self, event):
        global cached_scene
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                cached_scene = self
                pause_menu = PauseMenu(engine.manager)
                engine.manager.set_state(pause_menu, clear_threads=True)


class PhysicsObject(engine.TickableEntity):
    def __init__(self, pos, size, animation=None, animation_pos=Vector2()):
        self.pos = Vector2(pos)
        self.vel = Vector2()
        self.size = Vector2(size)

        self.animation = engine.Animation(*animation) if type(animation) is list else engine.Animation(animation)
        self.animation_pos = Vector2(animation_pos)

        self.hitbox_depth = 4

        self.rect = None
        self.check_box_bottom = None
        self.check_box_right = None
        self.check_box_left = None
        self.check_box_top = None

        self.updateBoundingPoints()

        self.touching_top = False
        self.touching_bottom = False
        self.touching_right = False
        self.touching_left = False

        self.gravity = 1500
        self.drag = 10

    def serialize(self):
        self.animation.serialize()

    def updateBoundingPoints(self):
        self.rect = pygame.Rect(self.pos, (self.size.x, self.size.y))
        self.check_box_bottom = pygame.Rect(self.pos + (0, self.size.y), (self.size.x, self.hitbox_depth))
        self.check_box_right = pygame.Rect(self.pos + (self.size.x, 0), (self.hitbox_depth, self.size.y))
        self.check_box_left = pygame.Rect(self.pos + (-self.hitbox_depth, 0), (self.hitbox_depth, self.size.y))
        self.check_box_top = pygame.Rect(self.pos + (0, -self.hitbox_depth), (self.size.x, self.hitbox_depth))

    def update(self, *args):
        # Physics and collisions
        scene: engine.State = args[0]

        self.touching_top = False
        self.touching_bottom = False
        self.touching_right = False
        self.touching_left = False

        self.vel.x = engine.math.lerp(self.vel.x, 0, self.drag * engine.delta())

        temp_vel = self.vel + (0, self.gravity * engine.delta())

        # Check bottom for collisions
        self.updateBoundingPoints()
        col = check_collision(self.check_box_bottom, scene.physics_objects)
        if col:
            temp_vel.y = min(temp_vel.y, 0)
            self.pos.y -= self.check_box_bottom.y - col.rect.y
            self.touching_bottom = col

        # Check top for collisions
        self.updateBoundingPoints()
        col = check_collision(self.check_box_top, scene.physics_objects)
        if col:
            temp_vel.y = max(temp_vel.y, 0)
            self.touching_top = col

        # Check left for collisions
        self.updateBoundingPoints()
        col = check_collision(self.check_box_left, scene.physics_objects)
        if col:
            temp_vel.x = max(temp_vel.x, 0)
            self.touching_left = col

        # Check right for collisions
        self.updateBoundingPoints()
        col = check_collision(self.check_box_right, scene.physics_objects)
        if col:
            temp_vel.x = min(temp_vel.x, 0)
            self.touching_right = col

        self.vel = temp_vel
        self.pos = self.pos + self.vel * engine.delta()
        self.updateBoundingPoints()

        # Rendering
        if self.animation is None:
            pygame.draw.rect(engine.get_surface(), (255, 0, 68), self.rect)
        else:
            engine.manager.blit(self.animation.update_animation(), self.pos + self.animation_pos)

        if engine.debug:
            pygame.draw.rect(engine.get_surface(), (255, 0, 0), self.rect, 1)
            pygame.draw.rect(engine.get_surface(),
                             (255, 255, 204) if not self.touching_bottom else (0, 255, 0),
                             self.check_box_bottom, 1)
            pygame.draw.rect(engine.get_surface(), (255, 255, 204) if not self.touching_right else (0, 255, 0),
                             self.check_box_right, 1)
            pygame.draw.rect(engine.get_surface(), (255, 255, 204) if not self.touching_left else (0, 255, 0),
                             self.check_box_left, 1)
            pygame.draw.rect(engine.get_surface(), (255, 255, 204) if not self.touching_top else (0, 255, 0),
                             self.check_box_top, 1)


class PushablePhysicsObject(PhysicsObject):
    def __init__(self, *args):
        super().__init__(*args)
        self.push_speed = 3500
        self.push_classes = Player, PushablePhysicsObject

    def update(self, *args):
        super().update(*args)
        if type(self.touching_left) in self.push_classes:
            self.vel.x += self.push_speed * engine.delta()
        if type(self.touching_right) in self.push_classes:
            self.vel.x -= self.push_speed * engine.delta()


class Player(engine.TickableEntity):
    def __init__(self, pos, size=(52, 113)):
        self.pos = Vector2(pos)
        self.vel = Vector2()
        self.controlled_vel = Vector2()
        self.direction = 0
        self.size = Vector2(size)

        self.speed = 400
        self.speed_func = lambda x: math.sin(x * (math.pi / 2)) * self.speed
        self.jump_power = -750
        self.horizontal = 0
        self.acceleration = 10
        self.coyote_time = 0.1
        self.coyote_time_timer = 0.02

        self.left_key = pygame.K_LEFT
        self.right_key = pygame.K_RIGHT
        self.jump_key = pygame.K_UP
        self.interact_key = pygame.K_x
        self.attack_key = pygame.K_z  # currently unused

        self.hitbox_depth = 4

        self.rect = pygame.Rect(self.pos, self.size)
        self.check_box_bottom = pygame.Rect(self.pos + (0, self.size.y), (self.size.x, self.hitbox_depth))
        self.check_box_right = pygame.Rect(self.pos + (self.size.x, 0), (self.hitbox_depth, self.size.y))
        self.check_box_left = pygame.Rect(self.pos - (self.hitbox_depth, 0), (self.hitbox_depth, self.size.y))
        self.check_box_top = pygame.Rect(self.pos - (0, self.hitbox_depth), (self.size.x, self.hitbox_depth))

        self.touching_top = False
        self.touching_bottom = False
        self.touching_right = False
        self.touching_left = False

        self.ground_particle_position = self.pos + (self.size.x / 2, self.size.y)

        self.walk_anim_left = engine.Animation("assets/skirmbolg/walk", 0.075)
        self.walk_anim_right = engine.Animation("assets/skirmbolg/walk", 0.075).flip()
        self.idle_anim_left = engine.Animation("assets/skirmbolg/idle", 0.075)
        self.idle_anim_right = engine.Animation("assets/skirmbolg/idle", 0.075).flip()
        self.jump_anim = engine.Animation("assets/skirmbolg/jump", 0.075)
        self.fall_anim = engine.Animation("assets/skirmbolg/fall", 0.075)

        self.animation = self.idle_anim_left

        self.footstep_timer = engine.Timer(0.085)

        self.gravity = Vector2(0, 2400)
        self.drag = 10

        self.allow_movement = True

    def updateBoundingPoints(self):
        self.rect = pygame.Rect(self.pos, self.size)
        self.check_box_bottom = pygame.Rect(self.pos + (0, self.size.y), (self.size.x, self.hitbox_depth))
        self.check_box_right = pygame.Rect(self.pos + (self.size.x, 0), (self.hitbox_depth, self.size.y))
        self.check_box_left = pygame.Rect(self.pos - (self.hitbox_depth, 0), (self.hitbox_depth, self.size.y))
        self.check_box_top = pygame.Rect(self.pos - (0, self.hitbox_depth), (self.size.x, self.hitbox_depth))

        self.ground_particle_position = self.pos + (self.size.x / 2, self.size.y)

    def update(self, *args):
        # Physics and collisions
        scene: engine.State = args[0]

        self.touching_top = False
        self.touching_bottom = False
        self.touching_right = False
        self.touching_left = False

        # Apply drag
        self.vel.x = engine.math.lerp(self.vel.x, 0, self.drag * engine.delta())

        # Calculate velocity for collision checks
        temp_vel = self.vel + self.gravity * engine.delta()

        # Check bottom for collisions
        self.updateBoundingPoints()
        col = check_collision(self.check_box_bottom, scene.physics_objects)
        if col:
            temp_vel.y = min(temp_vel.y, 0)
            if self.vel.y > 0:
                self.pos.y -= self.check_box_bottom.y - col.rect.y
            self.touching_bottom = True

        # Check top for collisions
        self.updateBoundingPoints()
        col = check_collision(self.check_box_top, scene.physics_objects)
        if col:
            temp_vel.y = max(temp_vel.y, 0)
            self.touching_top = True

        # Check left for collisions
        self.updateBoundingPoints()
        col = check_collision(self.check_box_left, scene.physics_objects)
        if col:
            temp_vel.x = max(temp_vel.x, 0)
            self.controlled_vel.x = max(self.controlled_vel.x, 0)
            self.touching_left = True

        # Check right for collisions
        self.updateBoundingPoints()
        col = check_collision(self.check_box_right, scene.physics_objects)
        if col:
            temp_vel.x = min(temp_vel.x, 0)
            self.controlled_vel.x = min(self.controlled_vel.x, 0)
            self.touching_right = True

        self.vel = temp_vel
        self.pos = self.pos + (self.vel + self.controlled_vel) * engine.delta()
        self.updateBoundingPoints()
        engine.manager.blit(self.animation.update_animation(), self.pos)

        # Player input & movement
        self.coyote_time_timer -= engine.delta()
        if self.touching_bottom:
            self.coyote_time_timer = self.coyote_time

        keys = pygame.key.get_pressed()

        self.horizontal += self.acceleration * engine.delta() if (
                keys[self.left_key] or keys[self.right_key]) else -self.horizontal * 0.1
        self.horizontal = engine.math.clamp(self.horizontal, 0, 1)

        if self.allow_movement:
            if keys[self.jump_key] and self.coyote_time_timer > 0:
                self.coyote_time_timer = 0
                self.vel[1] = self.jump_power
                play_randomly_pitched_sound(engine.get_asset("jump"))
                for p in range(20):
                    addParticle(self.ground_particle_position, scene)

            if keys[self.left_key]:
                if self.direction != -1:
                    if self.touching_bottom and abs(self.vel[0]) < 1:
                        for p in range(20):
                            addParticle(self.ground_particle_position, scene, "dust_particle")
                    self.vel[0] += self.controlled_vel[0]
                    self.controlled_vel[0] = 0
                self.direction = -1
            elif keys[self.right_key]:

                if self.direction != 1:
                    if self.touching_bottom and abs(self.vel[0]) < 1:
                        for p in range(20):
                            addParticle(self.ground_particle_position, scene, "dust_particle")
                    self.vel[0] += self.controlled_vel[0]
                    self.controlled_vel[0] = 0
                self.direction = 1

            if self.touching_bottom and self.footstep_timer.update() and (keys[self.right_key] or keys[self.left_key]):
                play_randomly_pitched_sound(engine.get_asset("footstep_1"))
                self.footstep_timer.reset()

        self.controlled_vel[0] = self.speed_func(self.horizontal) * self.direction

        # Animations and other fx
        if self.vel[1] < 0:
            self.animation = self.jump_anim
        elif self.vel[1] > 0:
            self.animation = self.fall_anim
        elif keys[self.left_key]:
            self.animation = self.walk_anim_left
            if self.touching_bottom:
                addParticle(self.ground_particle_position, scene)
        elif keys[self.right_key]:
            self.animation = self.walk_anim_right
            if self.touching_bottom:
                addParticle(self.ground_particle_position, scene)
        else:
            if self.direction == 1:
                self.animation = self.idle_anim_right
            else:
                self.animation = self.idle_anim_left

        # Debug utils
        if engine.debug:
            if pygame.mouse.get_pressed()[0]:
                self.vel = Vector2()
                self.pos = Vector2(pygame.mouse.get_pos())

            pygame.draw.rect(engine.get_surface(), (255, 0, 0), self.rect, 1)
            pygame.draw.rect(engine.get_surface(),
                             (255, 255, 204) if not self.touching_bottom else (0, 255, 0),
                             self.check_box_bottom, 1)
            pygame.draw.rect(engine.get_surface(), (255, 255, 204) if not self.touching_right else (0, 255, 0),
                             self.check_box_right, 1)
            pygame.draw.rect(engine.get_surface(), (255, 255, 204) if not self.touching_left else (0, 255, 0),
                             self.check_box_left, 1)
            pygame.draw.rect(engine.get_surface(), (255, 255, 204) if not self.touching_top else (0, 255, 0),
                             self.check_box_top, 1)
            pygame.draw.circle(engine.get_surface(), (0, 0, 255), self.ground_particle_position, 5)


class Platform(engine.TickableEntity):
    def __init__(self, pos, size, image=None, draw=True):
        self.pos = Vector2(pos)
        self.size = Vector2(size)
        self.rect = pygame.Rect(self.pos, self.size)
        self.draw = draw
        self.draw_rect = self.rect
        self.image = image

    def update(self, *args):
        if self.draw:
            pygame.draw.rect(engine.get_surface(), (24, 20, 37), self.draw_rect)
        elif self.image is not None:
            engine.manager.blit(engine.get_asset(self.image), self.pos)
        if engine.debug:
            pygame.draw.rect(engine.get_surface(), (255, 0, 0), self.rect, 1)


class PassablePlatform(Platform):
    def __init__(self, *args):
        super().__init__(*args)
        self.perma_rect = copy.deepcopy(self.rect)
        self.draw_rect = self.perma_rect

    def update(self, *args):
        scene = args[0]
        player = scene.objects["player"]
        if player.pos.y + player.size.y - player.hitbox_depth < self.pos.y:
            self.rect = self.perma_rect
        else:
            self.rect = pygame.Rect(0, 0, 0, 0)
        super().update(*args)


class LevelTrigger(engine.TickableEntity):
    def __init__(self, pos, level_name, spawn_side):
        self.level_name = level_name
        self.spawn_side = spawn_side
        self.rect = pygame.Rect(pos, (10, 132))

    def update(self, *args):
        scene: Level = args[0]
        if not scene.objects["player"]:
            return
        player_rect = scene.objects["player"].rect
        if self.rect.colliderect(player_rect):
            pack_json_level(scene)
            level = load_json_level(f"gamedata/levels/level/{self.level_name}.json", self.spawn_side)
            engine.manager.set_state(level)
            scene.cleanup()

        if engine.debug:
            pygame.draw.rect(engine.get_surface(), (255, 255, 200), self.rect, 1)


class BouncePad(engine.TickableEntity):
    def __init__(self, pos):
        self.pos = Vector2(pos)
        self.trigger_rect = pygame.Rect(self.pos, (50, 50))

        self.particle_position = self.pos + (25, 15)

        self.bounce_force = -1200

        self.animation = None
        self.idle_anim = engine.Animation("assets/bounce_pad/idle")
        self.bounce_anim = engine.Animation("assets/bounce_pad/bounce", 0.05)

        self.anim_timer = engine.Timer(len(self.bounce_anim.frames) * self.bounce_anim.frame_delay)

    def serialize(self):
        self.idle_anim.serialize()
        self.bounce_anim.serialize()

    def addParticle(self, scene, particle_img="mushroom_particle"):
        particle = scene.objects["particle manager"].addDefinedParticle(engine.Particle(
            engine.get_asset(particle_img),
            self.particle_position,
            [random.randint(-100, 100), random.randint(-100, 100)]
        ))
        particle.rotation_per_second = random.randint(-90, 90)
        particle.scale_per_second = random.randint(-9, -2)

    def update(self, *args):
        scene = args[0]
        player = scene.objects["player"]

        if self.animation not in [self.idle_anim, self.bounce_anim]:
            self.animation = self.idle_anim

        if player.vel.y > 0 and self.trigger_rect.colliderect(player.rect):
            player.vel.y = self.bounce_force
            for p in range(20):
                self.addParticle(scene)
            self.bounce_anim.reset()
            self.animation = self.bounce_anim
            self.anim_timer.reset()
            play_randomly_pitched_sound(engine.get_asset("boing"))

        if self.anim_timer.update():
            self.idle_anim.reset()
            self.animation = self.idle_anim

        anim = self.animation.update_animation()
        engine.manager.blit(anim, self.pos)

        if engine.debug:
            surf = engine.get_surface()
            pygame.draw.rect(surf, (255, 255, 200), self.trigger_rect, 1)
            pygame.draw.circle(surf, (0, 0, 255), self.particle_position, 5)


class PushableBouncePad(BouncePad):
    def __init__(self, pos, hitbox_offset=Vector2(0, 15), hitbox_size=Vector2(50, 35)):
        self.hitbox_offset = hitbox_offset
        self.size = hitbox_size

        super().__init__(pos)

        self.vel = Vector2()

        self.hitbox_depth = 4

        self.rect = None
        self.check_box_bottom = None
        self.check_box_right = None
        self.check_box_left = None
        self.check_box_top = None

        self.updateBoundingPoints()

        self.touching_top = False
        self.touching_bottom = False
        self.touching_right = False
        self.touching_left = False

        self.gravity = 1500
        self.drag = 10

        self.idle_anim = engine.Animation("assets/pushable_bounce_pad/idle")
        self.bounce_anim = engine.Animation("assets/pushable_bounce_pad/bounce", 0.05)

        self.push_speed = 3500
        self.push_classes = Player, PushablePhysicsObject

    def updateBoundingPoints(self):
        self.trigger_rect = pygame.Rect(self.pos, (50, 50))
        self.particle_position = add_tuples(self.pos, (25, 15))
        self.rect = pygame.Rect(self.pos + self.hitbox_offset, (self.size.x, self.size.y))
        self.check_box_bottom = pygame.Rect(self.pos + self.hitbox_offset + (0, self.size.y),
                                            (self.size.x, self.hitbox_depth))
        self.check_box_right = pygame.Rect(self.pos + self.hitbox_offset + (self.size.x, 0),
                                           (self.hitbox_depth, self.size.y))
        self.check_box_left = pygame.Rect(self.pos + self.hitbox_offset + (-self.hitbox_depth, 0),
                                          (self.hitbox_depth, self.size.y))
        self.check_box_top = pygame.Rect(self.pos + self.hitbox_offset + (0, -self.hitbox_depth),
                                         (self.size.x, self.hitbox_depth))

    def update(self, *args):
        scene: engine.State = args[0]

        self.touching_top = False
        self.touching_bottom = False
        self.touching_right = False
        self.touching_left = False

        self.vel.x = engine.math.lerp(self.vel.x, 0, self.drag * engine.delta())

        temp_vel = self.vel + (0, self.gravity * engine.delta())

        # Check bottom for collisions
        self.updateBoundingPoints()
        col = check_collision(self.check_box_bottom, scene.physics_objects)
        if col:
            temp_vel.y = min(temp_vel.y, 0)
            self.pos.y -= self.check_box_bottom.y - col.rect.y
            self.touching_bottom = col

        # Check top for collisions
        self.updateBoundingPoints()
        col = check_collision(self.check_box_top, scene.physics_objects)
        if col:
            temp_vel.y = max(temp_vel.y, 0)
            self.touching_top = col

        # Check left for collisions
        self.updateBoundingPoints()
        col = check_collision(self.check_box_left, scene.physics_objects)
        if col:
            temp_vel.x = max(temp_vel.x, 0)
            self.touching_left = col

        # Check right for collisions
        self.updateBoundingPoints()
        col = check_collision(self.check_box_right, scene.physics_objects)
        if col:
            temp_vel.x = min(temp_vel.x, 0)
            self.touching_right = col

        self.vel = temp_vel
        self.pos = self.pos + self.vel * engine.delta()
        self.updateBoundingPoints()

        super().update(*args)

        if type(self.touching_left) in self.push_classes:
            self.vel.x += self.push_speed * engine.delta()
        if type(self.touching_right) in self.push_classes:
            self.vel.x -= self.push_speed * engine.delta()
        if engine.debug:
            pygame.draw.rect(engine.get_surface(), (255, 0, 0), self.rect, 1)
            pygame.draw.rect(engine.get_surface(),
                             (255, 255, 204) if not self.touching_bottom else (0, 255, 0),
                             self.check_box_bottom, 1)
            pygame.draw.rect(engine.get_surface(), (255, 255, 204) if not self.touching_right else (0, 255, 0),
                             self.check_box_right, 1)
            pygame.draw.rect(engine.get_surface(), (255, 255, 204) if not self.touching_left else (0, 255, 0),
                             self.check_box_left, 1)
            pygame.draw.rect(engine.get_surface(), (255, 255, 204) if not self.touching_top else (0, 255, 0),
                             self.check_box_top, 1)


class BouncePuff(engine.TickableEntity):
    def __init__(self, pos, stalk_pos):
        self.pos = Vector2(pos)
        self.stalk_pos = Vector2(stalk_pos)

        self.radius = 26
        self.hitbox = (self.pos, self.radius)  # Not really a "box" but close enough probably

        self.head_animation = None
        self.stalk_animation = None

        self.head_idle_anim = engine.Animation("assets/bounce_puff/head/idle")
        self.head_bounce_anim = engine.Animation("assets/bounce_puff/head/bounce", 0.05)

        self.stalk_idle_anim = engine.Animation("assets/bounce_puff/stalk/idle")

        self.anim_timer = engine.Timer(len(self.head_bounce_anim.frames) * self.head_bounce_anim.frame_delay)

        # x value needs to be higher since there's no drag calculation on the player's y velocity
        self.bounce_force = Vector2(-2500, -1000)

    def serialize(self):
        self.head_idle_anim.serialize()
        self.head_bounce_anim.serialize()
        self.stalk_idle_anim.serialize()

    def update(self, *args):
        scene = args[0]
        player = scene.objects["player"]
        player_center = player.rect.center

        hitbox = pygame.geometry.Circle(*self.hitbox)

        if hitbox.colliderect(player.rect):
            direction = (self.pos - player_center).normalize()
            bounce_vector = Vector2(direction.x * self.bounce_force.x, direction.y * self.bounce_force.y)
            player.vel = Vector2(bounce_vector)
            for p in range(20):
                particle = scene.objects["particle manager"].addDefinedParticle(engine.Particle(
                    engine.get_asset("puff_particle"),
                    self.pos, [random.randint(-200, 200), random.randint(-200, 200)]
                ))
                particle.rotation_per_second = random.randint(-90, 90)
                particle.scale_per_second = random.randint(-2, -1)
                particle.gravity = Vector2(0, random.randint(200, 500))
            play_randomly_pitched_sound(engine.get_asset("puff"))
            self.head_animation = self.head_bounce_anim
            self.anim_timer.reset()

        if self.anim_timer.update():
            self.head_idle_anim.reset()
            self.head_animation = self.head_idle_anim

        if self.head_animation not in [self.head_idle_anim, self.head_bounce_anim]:
            self.head_animation = self.head_idle_anim

        if self.stalk_animation not in [self.stalk_idle_anim]:
            self.stalk_animation = self.stalk_idle_anim

        head_anim = self.head_animation.update_animation()

        stalk_anim = self.stalk_animation.update_animation()

        stalk_height = abs(self.stalk_pos.y - self.pos.y)

        stalk_surf = pygame.Surface((20, stalk_height), pygame.SRCALPHA, 32)
        num_stalks = math.ceil(stalk_height / 50)

        for s in range(num_stalks):
            stalk_surf.blit(stalk_anim, (0, s * 50))

        engine.manager.blit_center(stalk_surf, self.pos + (0, stalk_height / 2))
        engine.manager.blit_center(head_anim, self.pos)

        if engine.debug:
            surface = engine.get_surface()
            pygame.draw.circle(surface, (255, 255, 200), self.pos, hitbox.radius, 1)
            if self.stalk_pos:
                pygame.draw.line(surface, (255, 255, 200), self.pos, self.stalk_pos)


class Npc(engine.TickableEntity):
    def __init__(self, path, pos):
        self.pos = Vector2(pos)

        with open(path) as file:
            data = json.loads(file.read())
        self.name = data["name"]

        self.animation = None

        self.idle_animation = engine.Animation(data["idle_animation"]["path"],
                                               data["idle_animation"]["frame_delay"])
        self.talking_animation = engine.Animation(data["talking_animation"]["path"],
                                                  data["talking_animation"]["frame_delay"])

        self.dialogue_idle_animation = engine.Animation(data["dialogue_idle_animation"]["path"],
                                                        data["dialogue_idle_animation"]["frame_delay"])
        self.dialogue_talking_animation = engine.Animation(data["dialogue_talking_animation"]["path"],
                                                           data["dialogue_talking_animation"]["frame_delay"])

    def serialize(self):
        self.idle_animation.serialize()
        self.talking_animation.serialize()
        self.dialogue_idle_animation.serialize()
        self.dialogue_talking_animation.serialize()

    def update(self, *args):
        if self.animation not in [self.idle_animation, self.talking_animation]:
            self.animation = self.idle_animation

        anim = self.animation.update_animation()
        engine.manager.blit(anim, self.pos)


class Spring:
    def __init__(self, pos, strength=20, dampening=0.2):  # Use hooke's law to calculate force (F = Kx)
        self.pos = Vector2(pos)
        self.target_pos = Vector2(pos)
        self.vel = Vector2()

        self.strength = strength
        self.dampening = dampening

        self.gravity = Vector2(0, 0)

    def update_vel(self, target_pos: pygame.Vector2 = None):
        if target_pos is None:
            target_pos = self.target_pos
        distance = target_pos - self.pos
        force = distance * self.strength
        force_delta = force * engine.delta()

        self.vel = self.vel + force_delta + (self.gravity * engine.delta())
        self.vel = self.vel.lerp(Vector2(0, 0), engine.math.clamp(self.dampening * engine.delta(), 0, 1))

    def update(self):
        self.pos = self.pos + self.vel * engine.delta()

        if engine.debug:
            surface = engine.get_surface()
            pygame.draw.circle(surface, (255, 255, 200), self.pos, 5, 1)


class RotationSpring:
    def __init__(self, rotation, target_rotation, strength=1, dampening=1):
        self.rotation = rotation
        self.target_rotation = target_rotation
        self.angular_velocity = 0

        self.strength = strength
        self.dampening = dampening

    def update(self):
        self.angular_velocity += (self.target_rotation - self.rotation) * engine.delta() * self.strength
        self.angular_velocity = engine.math.lerp(self.angular_velocity, 0, self.dampening * engine.delta())

        self.rotation += self.angular_velocity


class GrassPatch(engine.TickableEntity):
    def __init__(self, pos, width):
        self.pos = Vector2(pos)
        self.width = width

        self.interval = 3 if engine.settings.getConfig().getboolean("graphics", "fancy_grass") else 4

        self.grass = [Grass(self.pos + (x * self.interval, 0)) for x in range(int(self.width / self.interval))]
        random.shuffle(self.grass)

    def update(self, *args):
        if engine.settings.getConfig().getboolean("graphics", "grass"):
            for g in self.grass:
                g.update(*args)


class Grass(engine.TickableEntity):
    def __init__(self, pos):
        self.pos = Vector2(pos)
        self.pos.x += random.randint(-1, 1)

        self.influence = 0.07
        self.wind_strength = random.randint(7, 12)

        self.width = random.randint(1, 2)
        self.height = random.randint(5, 20)
        self.trigger_rect = pygame.Rect(0, 0, self.width, self.height)
        self.trigger_rect.midbottom = self.pos

        self.damp = random.uniform(0.7, 1.5)
        self.strength = random.uniform(0.7, 1.5)

        self.rot_spring = RotationSpring(0, 0, self.strength, self.damp)

        self.colour = random.choice((
            (25, 60, 62),
            (38, 92, 66),
            (62, 137, 72)
        ))

    def update(self, *args):
        scene = args[0]
        player = scene.objects["player"]

        self.rot_spring.angular_velocity -= (math.sin(engine.manager.engine.time) *
                                             self.wind_strength * engine.delta())

        if self.trigger_rect.colliderect(player.rect):
            self.rot_spring.angular_velocity += ((player.vel.x + player.controlled_vel.x) *
                                                 self.influence * engine.delta())

        self.rot_spring.update()

        grass_tip = self.pos + engine.VEC2_UP.rotate(self.rot_spring.rotation) * self.height

        surface = engine.get_surface()
        points = [self.pos - (self.width, 0), self.pos + (self.width, 0), grass_tip]

        pygame.draw.polygon(surface, self.colour, points)
        pygame.draw.lines(surface, self.colour, False, points, 3)

        if engine.settings.getConfig().getboolean("graphics", "fancy_grass"):
            for p in points:
                pygame.draw.circle(surface, self.colour, p, 1.5)

        if engine.debug:
            pygame.draw.line(surface, (0, 0, 255), self.pos, grass_tip, 1)


class Water(engine.TickableEntity):
    def __init__(self, anchors):
        self.anchors = [Vector2(anchor) for anchor in anchors]

        self.influence = 2

        self.springs = []

        self.step_size = 10
        self.width = self.anchors[1].x - self.anchors[0].x
        self.height = self.anchors[3].y - self.anchors[0].y
        y = self.anchors[0].y
        start_x = self.anchors[0].x
        for x in range(round(self.width / self.step_size) + 1):
            x_ = x * self.step_size
            self.springs.append(Spring([start_x + x_, y]))
        self.springs[-1].target_pos.x = self.anchors[1].x
        self.springs[-1].pos.x = self.anchors[1].x

    def update(self, *args):
        scene = args[0]

        player = scene.objects["player"]

        if not player:
            return

        points = []
        for i, s in enumerate(self.springs):
            col_circle = pygame.geometry.Circle(s.pos, self.step_size)

            if col_circle.colliderect(player.rect):
                s.vel.y += player.vel.y * self.influence * engine.delta()

            if i > 0:
                pos = Vector2(
                    s.pos.x,
                    self.springs[i - 1].pos.y
                )
                s.update_vel(pos)
                s.update_vel(pos)
            if i < len(self.springs) - 1:
                pos = Vector2(
                    s.pos.x,
                    self.springs[i + 1].pos.y
                )
                s.update_vel(pos)
                s.update_vel(pos)
            s.update_vel()
            s.update()
            points.append(s.pos)

        surface = engine.get_surface()

        engine.util.draw_polygon_alpha(surface, (0, 149, 233, 150), [*points, self.anchors[2], self.anchors[3]])
        pygame.draw.lines(surface, (255, 255, 255), False, points, 5)

        if engine.debug:
            pygame.draw.lines(surface, (255, 255, 200), False, points, 1)
            pygame.draw.polygon(surface, (0, 0, 255), self.anchors, 1)
            for p in points:
                pygame.draw.circle(surface, (255, 255, 200), p, 3)
            for a in self.anchors:
                pygame.draw.circle(surface, (0, 0, 255), a, 3)


class Light(engine.TickableEntity):
    def __init__(self, pos, radius):
        self.pos = Vector2(pos)
        self.radius = radius
        self.angle_step_size = 0  # Angle between each ray (in degrees)
        match engine.settings.getConfig().get("graphics", "light_quality"):
            case "insane":
                self.angle_step_size = 0.25
            case "ultra":
                self.angle_step_size = 0.5
            case "high":
                self.angle_step_size = 1
            case "medium":
                self.angle_step_size = 2
            case "low":
                self.angle_step_size = 3
            case "very low":
                self.angle_step_size = 4
        self.touched_objects = []

    def update(self, *args):
        scene = args[0]

        touched_objects = []

        collidable_objects = [*scene.physics_objects]

        collision_points = []

        for s_ in range(int(360 / self.angle_step_size)):
            s = s_ * self.angle_step_size
            direction = Vector2(0, 1).rotate(s)
            pos = Vector2(self.pos)

            collision_point, collided_object = engine.linecast(pos, direction, self.radius, collidable_objects)

            collision_points.append(collision_point)
            touched_objects.append(collided_object)

        surface = engine.get_surface()
        engine.util.draw_polygon_alpha(surface, (255, 255, 200, 50), collision_points)

        if engine.debug:
            pygame.draw.lines(surface, (0, 0, 255), True, collision_points, 1)
            for c in collision_points:
                pygame.draw.line(surface, (255, 0, 0), self.pos, c, 1)
            pygame.draw.circle(surface, (0, 0, 255), self.pos, 5)


class Collectible(engine.TickableEntity):
    def __init__(self, pos):
        self.pos = Vector2(pos)
        self.animation = engine.Animation("assets/collectible/idle")
        self.trigger_rect = pygame.Rect(self.pos, (50, 50))
        self.enabled = True

    def serialize(self):
        self.animation.serialize()

    def update(self, *args):
        if not self.enabled:
            return

        scene: Level = args[0]
        player = scene.objects["player"]

        if self.trigger_rect.colliderect(player.rect):
            self.enabled = False
            save_data.global_save["hats_collected"] += 1
            scene.add_buffered_object("hat_collected_animation", engine.Animation(
                "assets/collectible/collected",
                0.025,
                self.trigger_rect.center,
                True
            ))

            play_randomly_pitched_sound(engine.get_asset("collectible"))

            for p in range(20):
                addParticle(self.trigger_rect.center, scene, "spark")

            for p in range(20):
                addParticle(self.trigger_rect.center, scene, "spark_purple")

        anim = self.animation.update_animation()

        engine.manager.blit(anim, self.pos)

        if engine.debug:
            surface = engine.get_surface()
            pygame.draw.rect(surface, (255, 255, 200), self.trigger_rect, 1)


class SaveData:
    def __init__(self):
        self.global_save = {
            "hats_collected": 0
        }
        self.player_saves = [
            {
                "room": "10_10"
            } for _ in range(2)
        ]

    def save(self, path="gamedata/savedata/save.pickle"):
        data = pickle.dumps(self)
        with open(path, "wb") as file:
            file.write(data)
        print("Game saved!")


def addParticle(position, scene, particle_img="ground_particle"):
    particle = scene.objects["particle manager"].addDefinedParticle(engine.Particle(
        engine.get_asset(particle_img),
        position,
        [random.randint(-100, 100), random.randint(-100, 100)]
    ))
    particle.rotation_per_second = random.randint(-90, 90)
    particle.scale_per_second = random.randint(-9, -2)


def add_tuples(t1: tuple, t2: tuple):
    return Vector2(t1[0] + t2[0], t1[1] + t2[1])


def check_collision(rect, physics_objects):
    for o in physics_objects:
        if rect.colliderect(o.rect):
            return o
    return None


def load_json_level(path, spawn_side="default"):
    print(f"Loading level from [{path}]")

    save_location = "gamedata/savedata/" + path.split("/")[-1]
    print(f"Checking for existing level save data at {save_location}")

    if os.path.exists(save_location):
        print("Found level save data")
        print("Loading save data")
        with open(save_location, "rb") as file:
            level = pickle.loads(file.read())
            spawn_pos = level.spawn_positions[spawn_side]
            print(f"Spawning player at {spawn_pos}")
            level.addPlayer(engine.manager.globals["player type"], spawn_pos)
            for o in level.objects.values():
                if getattr(o, "deserialize", False):
                    o.deserialize()
            return level

    else:
        print("Could not find level save data")

    with open(path) as file:
        level_data = json.load(file)
        print("Loaded level data")
    objects = []
    for o in level_data["level"]:
        print(f"Found object '{o['name']}' of type '{o['type']}'")
        o_type = str_to_class(o["type"])
        for o_ in objects:
            if o_[0] == o["name"]:
                print(f"Object with name already exists. Modifying object name.")
                o["name"] = o["name"] + "_name-duplicated"
        objects.append([o["name"], o["is_physics"], o_type(*[*o.values()][3:])])

    level = Level(engine.manager)
    print("Instanced level class")
    level.position = level_data["position"]
    print("Set level position")
    level.spawn_positions = level_data["spawn_positions"]
    print("Set level spawn positions")

    for o in objects:
        if o[1]:
            level.add_phys_object(o[0], o[2])
        else:
            level.add_object(o[0], o[2])
        print(f"Added object {o}")

    spawn_pos = level.spawn_positions[spawn_side]

    print(f"Spawning player at {spawn_pos}")
    level.addPlayer(engine.manager.globals["player type"], spawn_pos)

    if "level_late" in level_data:
        late_objects = []

        for o in level_data["level_late"]:
            print(f"Found late object '{o['name']}' of type '{o['type']}'")
            o_type = str_to_class(o["type"])
            for o_ in late_objects:
                if o_[0] == o["name"]:
                    print(f"Object with name already exists. Modifying object name.")
                    o["name"] = o["name"] + "_name-duplicated"
            late_objects.append([o["name"], o["is_physics"], o_type(*[*o.values()][3:])])

        for o in late_objects:
            if o[1]:
                level.add_phys_object(o[0], o[2])
            else:
                level.add_object(o[0], o[2])
            print(f"Added late object {o}")

    print("Level loading complete")
    return level


def pack_json_level(level):
    print("Saving level...")
    if not engine.settings.getConfig().getboolean("debug", "do_saving"):
        print("Saving is disabled.")
        return None
    try:
        level.physics_objects.remove(level.objects["player"])
        level.objects["player"] = None
        print("Removed player from level data")
    except Exception as e:
        print("An error occurred while removing player from level data")
        print(e)
    for o in level.objects.values():
        if getattr(o, "serialize", False):
            o.serialize()
    print("Prepared objects for serialization")
    level.manager = None
    print("Set level manager to none")
    serialized_level_data = pickle.dumps(level)
    print("Serialized level data")
    with open(f"gamedata/savedata/{level.position}.json", "wb") as file:
        file.write(serialized_level_data)
        print("Level saved")


def load_save(path="gamedata/savedata/save.pickle"):
    try:
        with open(path, "rb") as file:
            save = pickle.loads(file.read())
    except FileNotFoundError:
        save = SaveData()
    return save


def str_to_class(class_name):
    if type(class_name) == list:
        return getattr(sys.modules[class_name[0]], class_name[1])
    return getattr(sys.modules[__name__], class_name)


save_data = load_save()

if __name__ == "__main__":
    settings.checkAndMakeSettings()
    engine.manager.make_fullscreen()
    pygame.mixer_music.set_volume(engine.settings.getConfig().getfloat("volume", "music") / 100)
    pygame.mixer_music.load("assets/moth_camiidae.mp3")
    pygame.mixer_music.play(-1)
    engine.run(MainMenu(engine.manager), TITLE, debug_=("debug" in sys.argv))
