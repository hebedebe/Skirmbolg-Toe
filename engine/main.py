import pygame
import moderngl
from array import array
from screeninfo import get_monitors
from glob import glob

import engine
import engine.settings
from engine.assetloader import Assets
import engine.util


class State:
    def __init__(self, manager):
        self.manager = manager
        self.objects = {}
        self.physics_objects = []
        self.background_colour = (0, 0, 0)

        self.buffered_objects = {}

    def add_object(self, name, obj):
        self.objects[name] = obj

    def add_buffered_object(self, name, obj):
        self.buffered_objects[name] = obj

    def add_phys_object(self, name, obj):
        self.objects[name] = obj
        self.physics_objects.append(obj)

    def on_focus(self):
        ...

    def on_leave(self):
        self.cleanup()

    def cleanup(self):
        for o in self.objects.values():
            try:
                o.kill()  # If the object is a ui element setting it to None will not remove it
            except AttributeError:
                continue

    def on_init(self, *args):
        ...

    def on_draw(self, surface):
        surface.fill(self.background_colour)

    def on_event(self, event):
        ...

    def on_update(self):
        for i, (k, v) in enumerate(self.buffered_objects.items()):
            self.add_object(k, v)

        if self.objects:
            for o in self.objects.values():
                if issubclass(type(o), engine.TickableEntity):
                    o.update(self)

    def on_quit(self):
        self.cleanup()
        self.objects = None
        self.physics_objects = None
        self.manager.quit()


class StateMachine:
    def __init__(self, manager):
        self.state = None
        self.manager = manager
        self.next_state = None

    def __call__(self):
        self.update()
        if self.state:
            return self.state
        else:
            State(self.manager)

    def set(self, state):
        if state:
            if self.state is None:
                state.on_focus()
                self.state = state
            else:
                self.next_state = state

    def update(self):
        if self.next_state:
            if self.state:
                self.state.on_leave()

            self.state = self.next_state
            self.state.on_focus()
            self.next_state = None


class DisplayEngine:
    def __init__(self, manager, caption, width, height, fps, flags):
        pygame.display.set_caption(caption)
        self.shaders = engine.settings.getConfig().getboolean("graphics", "shaders")
        self.display = None
        if (width, height) != (1920, 1080):
            self.do_display_scaling = True
            if self.shaders:
                self.display = pygame.display.set_mode((width, height), flags, 32)
            else:
                self.display = pygame.display.set_mode((width, height), flags | pygame.OPENGL | pygame.DOUBLEBUF, 32)
            self.surface = pygame.Surface((1920, 1080), flags, 32)
        else:
            self.do_display_scaling = False
            if self.shaders:
                self.display = pygame.display.set_mode((width, height), flags | pygame.OPENGL | pygame.DOUBLEBUF, 32)
                self.surface = pygame.Surface((width, height), flags, 32)
            else:
                self.surface = pygame.display.set_mode((width, height), flags, 32)

        if self.shaders:
            self.ctx = moderngl.create_context()
            self.quad_buffer = self.ctx.buffer(data=array('f', [
                # position (x, y), uv coords (x, y)
                -1.0, 1.0, 0.0, 0.0,  # top left
                1.0, 1.0, 1.0, 0.0,  # top right
                -1.0, -1.0, 0.0, 1.0,  # bottom left
                1.0, -1.0, 1.0, 1.0,  # bottom right
            ]))
            self.program = self.loadShader("shaders/vertex.glsl", "shaders/fragment.glsl")
            self.render_object = self.ctx.vertex_array(self.program, [(self.quad_buffer, '2f 2f', 'vert', 'texcoord')])

        self.rect = self.surface.get_rect()
        if self.shaders:
            self.flags = flags | pygame.OPENGL | pygame.DOUBLEBUF
        else:
            self.flags = flags
        self.clock = pygame.time.Clock()
        self.running = False
        self.delta = 0
        self.time = 0
        self.fps = fps
        self.fps_counter = engine.Text((0, 20), "FPS: error", 24)
        self.manager = manager

        self.state_machine = StateMachine(manager)

    def loadShader(self, vert_path, frag_path):
        with open(vert_path, "r") as vert_file:
            vert = vert_file.read()
        with open(frag_path, "r") as frag_file:
            frag = frag_file.read()
        return self.ctx.program(vertex_shader=vert, fragment_shader=frag)

    def surf_to_texture(self, surf: pygame.Surface):
        tex = self.ctx.texture(surf.get_size(), 4)
        tex.filter = (moderngl.NEAREST, moderngl.NEAREST)
        tex.swizzle = 'BGRA'
        tex.write(surf.get_view('1'))
        return tex

    def loop(self, state=None):
        self.running = True
        self.state_machine.set(state)

        while self.running:
            state = self.state_machine()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    state.on_quit()
                else:
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_BACKQUOTE:
                            engine.debug = not engine.debug
                    state.on_event(event)
                    self.manager.ui_manager.process_events(event)

            state.on_draw(self.surface)
            state.on_update()
            self.manager.ui_manager.update(self.delta)
            self.manager.ui_manager.draw_ui(self.surface)

            self.time += self.delta

            if engine.debug:
                self.fps_counter.text = f"FPS: {int(self.clock.get_fps())}"
                self.fps_counter.update()
            if self.do_display_scaling:
                scaled_surf = pygame.transform.scale_by(self.surface, self.display.get_width() / 1920)
                self.display.blit(scaled_surf, (0, (self.display.get_height() - scaled_surf.get_height()) / 2))
            elif self.shaders:
                frame_tex = self.surf_to_texture(self.surface)
                frame_tex.use(0)
                self.program['tex'] = 0
                self.program['colour_correction'] = (1, 1, 0.9)
                self.render_object.render(mode=moderngl.TRIANGLE_STRIP)

            pygame.display.flip()

            if self.shaders:
                frame_tex.release()

            self.delta = (self.clock.tick(self.fps) / 1000)

        engine.join_all_threads()


class StateControl:
    def __init__(self, state, *args):
        self.active = isinstance(state, State)
        self.state = state
        self.args = args

    def get(self, manager, *args):
        if not self.active:
            return self.state(manager, *self.args)

        return self.state


# Store what to be share across all states
class Manager:
    def __init__(self, caption, width, height, fps=60, flags=0):
        self.engine = DisplayEngine(self, caption, width, height, fps, flags)
        self.ui_manager = None
        self.controls = {}
        self.camera = pygame.Vector2()
        self.assets = Assets()
        self.globals = {}

    def delta(self):
        return self.engine.delta

    def blit(self, surf, pos):
        self.engine.surface.blit(surf, pos + self.camera)

    def blit_center(self, surf, pos):
        self.engine.surface.blit(surf,
                                 (pos.x - surf.get_width() / 2 + self.camera.x,
                                  pos.y - surf.get_height() / 2 + self.camera.y))

    @staticmethod
    def change_caption(caption):
        pygame.display.set_caption(caption)

    def change_resolution(self, width, height):
        pygame.display.set_mode((width, height), self.engine.flags)
        self.ui_manager.set_window_resolution((width, height))

    def make_fullscreen(self):
        monitor = get_monitors()[0]
        print(f"Detected monitor {monitor}")
        pygame.display.set_mode((monitor.width, monitor.height),
                                self.engine.flags)

    def add_state(self, key, state, *args):
        self.controls[key] = StateControl(state, *args)

    def run(self, state=None):
        state.on_init()
        self.engine.loop(state)

    def set_state(self, state, *args, clear_threads=True):
        if clear_threads:
            engine.join_all_threads()
        if isinstance(state, State):
            state.on_init(*args)
            self.engine.state_machine.next_state = state
        elif isinstance(state, (int, str)):
            self.engine.state_machine.next_state = self.controls[state].get(self, *args)
        else:
            print("Must be state or state key")

    def quit(self):
        self.engine.running = False


class TickableEntity:
    def update(self, *args): ...

    def kill(self): ...


class Sprite(TickableEntity):
    def __init__(self, image, pos=None):
        if pos is None:  # Prevents mutable default argument
            pos = pygame.Vector2()
        self.image = image
        self.pos = pygame.Vector2(pos)

    def update(self, *args):
        engine.manager.blit(engine.manager.assets.get(self.image), self.pos)


class ParticleManager(TickableEntity):
    def __init__(self):
        self.particles = []

    def serialize(self):
        self.particles = []

    def addParticle(self, *args):
        particle = Particle(*args)
        self.particles.append(particle)
        return particle

    def addDefinedParticle(self, particle):
        self.particles.append(particle)
        return particle

    def update(self, *args):
        kill_list = []
        for p in self.particles:
            p.update()
            if p.kill:
                kill_list.append(p)

        for p in kill_list:  # particles added to separate list to delete to prevent flickering.
            self.particles.remove(p)


class Particle:
    def __init__(self, image, pos, vel=(0, 0), scale=1):
        self.image = image
        self.pos = pygame.Vector2(pos)
        self.scale = scale
        self.rotation = 0
        self.vel = pygame.Vector2(vel)
        self.scale_per_second = 0
        self.rotation_per_second = 0
        self.gravity = pygame.Vector2()

        self.kill = False

    def update(self):
        self.rotation += self.rotation_per_second * engine.manager.engine.delta
        self.scale += self.scale_per_second * engine.manager.engine.delta
        if self.scale <= 0:
            self.scale = 0.001
            self.kill = True
        image = pygame.transform.scale_by(self.image, self.scale)
        image = pygame.transform.rotate(image, self.rotation)
        engine.manager.blit_center(image, self.pos)
        self.vel += self.gravity * engine.delta()
        self.pos += self.vel * engine.delta()
        if self.pos.y > engine.manager.engine.surface.get_height() + image.get_height() / 2:
            self.kill = True


class Animation(TickableEntity):
    def __init__(self, path, frame_delay=0.075, pos=None, kill_on_finish=False):
        if pos is None:  # Prevents mutable default argument
            pos = pygame.Vector2()
        if path in ["", None]:
            return
        self.frames = []
        self.pos = pygame.Vector2(pos)
        self.path = path
        try:
            for g in glob(f"{path}/*"):
                self.frames.append(pygame.image.load(g).convert_alpha())
        except FileNotFoundError:
            print(f"Could not find file at [{path}] while loading animation")
        self.frame_delay = frame_delay
        self.timer = 0
        self.current_frame = 0

        self.kill_on_finish = kill_on_finish
        self.enabled = True

    def reset(self):
        self.timer = 0
        self.current_frame = 0

    def serialize(self):
        self.frames = []

    def flip(self):
        temp_frames = []
        for f in self.frames:
            temp_frames.append(pygame.transform.flip(f, flip_x=True, flip_y=False))
        self.frames = temp_frames
        return self

    def update_animation(self) -> pygame.surface:
        if not self.frames:
            for g in glob(f"{self.path}/*"):
                self.frames.append(pygame.image.load(g).convert_alpha())
        self.timer += engine.manager.engine.delta
        if self.timer > self.frame_delay:
            self.timer = 0
            self.current_frame += 1
        if self.current_frame > len(self.frames) - 1:
            self.current_frame = 0
            if self.kill_on_finish:
                self.enabled = False
        return self.frames[self.current_frame]

    def update(self, *args):
        frame = self.update_animation()
        if not self.enabled:
            return
        engine.manager.blit_center(frame, self.pos)


class Timer(TickableEntity):
    def __init__(self, delay, events=None):
        if events is None:  # Prevents mutable default argument
            events = []
        self.delay = delay
        self.timer = 0
        self.events = events

    def reset(self):
        self.timer = 0

    def update(self, *args) -> bool:
        self.timer += engine.manager.engine.delta
        if self.timer >= self.delay:
            self.timer = 0
            for e in self.events:
                e()
            return True
        return False


class Text(TickableEntity):
    def __init__(self, pos, text, size, font="times new roman"):
        self.pos = pygame.Vector2(pos)
        self.font: pygame.Font = pygame.font.SysFont(font, size)
        self.text = text
        self.rendered_text = self.font.render(self.text, False, (255, 255, 255))

    def update(self, *args):
        surf = engine.manager.engine.surface
        self.rendered_text = self.font.render(self.text, False, (255, 255, 255))
        surf.blit(self.rendered_text, self.pos)


class SliceSprite(pygame.sprite.Sprite):  # Stolen from the internet
    """
    SliceSprite extends pygame.sprite.Sprite to allow for 9-slicing of its contents.
    Slicing of its image property is set using a slicing tuple (left, right, top, bottom).
    Values for (left, right, top, bottom) are distances from the image edges.
    """
    width_error = ValueError("SliceSprite width cannot be less than (left + right) slicing")
    height_error = ValueError("SliceSprite height cannot be less than (top + bottom) slicing")

    def __init__(self, image, slicing=(0, 0, 0, 0)):
        """
        Creates a SliceSprite object.
        _sliced_image is generated in _generate_slices() only when _regenerate_slices is True.
        This avoids recomputing the sliced image whenever each SliceSprite parameter is changed
        unless absolutely necessary! Additionally, _rect does not have direct @property access
        since updating properties of the rect would not be trigger _regenerate_slices.

        Args:
            image (pygame.Surface): the original surface to be sliced
            slicing (tuple(left, right, top, bottom): the 9-slicing margins relative to image edges
        """
        pygame.sprite.Sprite.__init__(self)
        self._image = image
        self._sliced_image = None
        self._rect = self.image.get_rect()
        self._slicing = slicing
        self._regenerate_slices = True

    @property
    def image(self):
        return self._image

    @image.setter
    def image(self, new_image):
        self._image = new_image
        self._regenerate_slices = True

    @property
    def width(self):
        return self._rect.width

    @width.setter
    def width(self, new_width):
        self._rect.width = new_width
        self._regenerate_slices = True

    @property
    def height(self):
        return self._rect.height

    @height.setter
    def height(self, new_height):
        self._rect.height = new_height
        self._regenerate_slices = True

    @property
    def x(self):
        return self._rect.x

    @x.setter
    def x(self, new_x):
        self._rect.x = new_x
        self._regenerate_slices = True

    @property
    def y(self):
        return self._rect.y

    @y.setter
    def y(self, new_y):
        self._rect.y = new_y
        self._regenerate_slices = True

    @property
    def slicing(self):
        return self._slicing

    @slicing.setter
    def slicing(self, new_slicing=(0, 0, 0, 0)):
        self._slicing = new_slicing
        self._regenerate_slices = True

    def get_rect(self):
        return self._rect

    def set_rect(self, new_rect):
        self._rect = new_rect
        self._regenerate_slices = True

    def _generate_slices(self):
        """
        Internal method required to generate _sliced_image property.
        This first creates nine subsurfaces of the original image (corners, edges, and center).
        Next, each subsurface is appropriately scaled using pygame.transform.smoothscale.
        Finally, each subsurface is translated in "relative coordinates."
        Raises appropriate errors if rect cannot fit the center of the original image.
        """
        num_slices = 9
        x, y, w, h = self._image.get_rect()
        l, r, t, b = self._slicing
        mw = w - l - r
        mh = h - t - b
        wr = w - r
        hb = h - b

        rect_data = [
            (0, 0, l, t), (l, 0, mw, t), (wr, 0, r, t),
            (0, t, l, mh), (l, t, mw, mh), (wr, t, r, mh),
            (0, hb, l, b), (l, hb, mw, b), (wr, hb, r, b),
        ]

        x, y, w, h = self._rect
        mw = w - l - r
        mh = h - t - b
        if mw < 0:
            raise SliceSprite.width_error
        if mh < 0:
            raise SliceSprite.height_error

        scales = [
            (l, t), (mw, t), (r, t),
            (l, mh), (mw, mh), (r, mh),
            (l, b), (mw, b), (r, b),
        ]

        translations = [
            (0, 0), (l, 0), (l + mw, 0),
            (0, t), (l, t), (l + mw, t),
            (0, t + mh), (l, t + mh), (l + mw, t + mh),
        ]

        self._sliced_image = pygame.Surface((w, h))
        for i in range(num_slices):
            rect = pygame.rect.Rect(rect_data[i])
            surf_slice = self.image.subsurface(rect)
            stretched_slice = pygame.transform.smoothscale(surf_slice, scales[i])
            self._sliced_image.blit(stretched_slice, translations[i])

    def draw(self, surface):
        """
        Draws the SliceSprite onto the desired surface.
        Calls _generate_slices only at draw time only if necessary.
        Note that the final translation occurs here in "absolute coordinates."

        Args:
            surface (pygame.Surface): the parent surface for blitting SliceSprite
        """
        x, y, w, h, = self._rect
        if self._regenerate_slices:
            self._generate_slices()
            self._regenerate_slices = False
        surface.blit(self._sliced_image, (x, y))


def linecast(start_pos, direction, distance, collidable_objects, distance_threshold=1):
    direction.normalize_ip()
    pos = pygame.Vector2(start_pos)
    distance_marched = 0

    collided_objects = []

    is_marching = True
    while is_marching:
        circle_collider = pygame.geometry.Circle(pos, distance)
        final_collision = False
        for c in collidable_objects:
            while circle_collider.colliderect(c.rect):
                circle_collider.radius /= 2
                if circle_collider.radius <= distance_threshold:
                    final_collision = True
                    collided_objects.append(c)
                    break
        pos += direction * circle_collider.radius
        distance_marched += circle_collider.radius
        if distance_marched >= distance - distance_threshold or final_collision:
            is_marching = False
            if (pos - start_pos).magnitude() > distance:
                pos -= start_pos
                pos.normalize_ip()
                pos *= distance
                pos += start_pos
    return pos, collided_objects
