import pygame as pg
from pygame.locals import *
from data.sprites import *
import math

class Tank:
    def __init__(self, shuttle):
        super().__init__()
        self.tank_surface = pg.image.load('./resources/Shuttle/tank.png').convert_alpha()
        self.tank_frames = pg.sprite.Group()
        vector = shuttle.position

        tank_sprite = ShuttleSprite(self.tank_surface, vector)

        self.tank_frames.add(tank_sprite)

        self.rect = self.get_group_rect(self.tank_frames)

        screen = pg.display.get_surface()
        self.area = screen.get_rect()

        self.main_engine = pg.mixer.Sound("./resources/main_engine.wav")
        self.rcs_engine = pg.mixer.Sound("./resources/RCS.wav")
        self.rcs_engine.set_volume(0.2)
        self.main_engine.set_volume(0.2)

        ## Motion constants ##
        self.ROTATION_SPEED = 180 # degrees/second
        self.MAX_SPEED = 250      # pixels/second
        self.DRAG = 0.01           # pixels/seconds
        self.THRUST_POWER = 0.0125
        self.MASS = 500
        self.GROUND_LEVEL = (self.area.height - vector.y)
        self.ROCKET_HEIGHT = self.rect.height
        self.ROCKET_WIDTH = self.rect.width

        self.originpos = pg.Vector2(vector.x - self.rect.width / 2, vector.y) # Initialize initial original position
        self.position = pg.Vector2(vector.x - self.rect.width / 2, vector.y) # Initialize position (on screen)
        self.originbot = shuttle.originpos.copy()
        self.midpoint = self.originbot / 2
        self.velocity = pg.Vector2() # Initialize Velocity
        self.altitude =  self.GROUND_LEVEL # Initialize altitude at Rect Bottom
        self.thrust = 0
        self.acceleration = 0
        self.angle = 0
        self.angular_velocity = 0

        self.exhaust_line_1 = pg.Vector2()
        self.exhaust_line_2 = pg.Vector2()
        self.debug_position = pg.Vector2()

        self.jettisoned = False
        self.touchdown = True
        self.attached = True
        self.engine_fire = False
        self.rcs_fire_r = self.rcs_fire_l = False
        self.crashed = False
        self.gone = False

        for sprite in self.tank_frames:
            sprite.update(self.position)

    def attach(self, shuttle):
        # Calculate the coordinates of the second endpoint
        self.angle = shuttle.angle
        self.position = shuttle.position.copy()
        self.velocity = shuttle.velocity.copy()
        self.altitude = shuttle.altitude

    def update(self):
        for sprite in self.tank_frames:
            sprite.update(self.position)
            sprite.rotate(self.angle)
        self.rect = self.get_group_rect(self.tank_frames)

    def draw(self, screen):
        if not self.crashed and not self.gone:
            self.tank_frames.draw(screen)

    def debug(self,screen, font):
        pg.draw.rect(screen, (0,0,0), self.rect, 2)
        pg.draw.circle(screen, (255,0,255), self.rect.center, radius = 5)

    def jettison(self, shuttle, gravity, direction):
        if not self.crashed and not self.gone:
            # Jettison
            self.angular_velocity += 0.02  if direction == "R" else 0 # Increase turn right
            self.angular_velocity -= 0.02 if direction == "L" else 0 # Increase turn left
            self.angle -= self.angular_velocity # Apply rcs power to angle
            self.angle %= 360 # Ensure angle is at Reasonable Range (0 to 360)
            self.jettisoned = True

            self.position += shuttle.velocity.copy()

            more_drag = 1
            if direction == "B":
                more_drag = 10

            if self.velocity.x > 0:
                Vx = -self.DRAG * more_drag
            else:
                Vx = self.DRAG * more_drag

            self.velocity.x += Vx
            self.velocity.y -= gravity
            y_scroll = (shuttle.velocity.copy()).y
            self.altitude += self.velocity.y - y_scroll

            self.position -= self.velocity

            if self.velocity.y > 0:
                self.touchdown = False

            if self.velocity.y <= -1 and  (self.position.y - self.velocity.y) >= self.originpos.y:
                self.crashed = True

    def reset(self):
        self.position = pg.Vector2(self.originpos).copy()
        self.velocity = pg.Vector2()
        self.rect = self.get_group_rect(self.tank_frames)
        self.angular_velocity = self.thrust = self.angle = 0
        self.altitude = self.GROUND_LEVEL
        self.touchdown = True
        self.crashed = False
        self.jettisoned = False
        self.gone = False
        for sprite in self.tank_frames:
            sprite.reset()

    def input(self, key, type):
        if type == KEYDOWN:
            if key == K_1:
                self.crashed = True
            if key == K_2:
                self.crashed = True
            if key == K_ESCAPE:
                self.reset()

    def get_group_rect(self,group):
        """
        Get the rect that bounds all sprites in the group.
        """
        rect = None  # Initialize as None
        for sprite in group:
            if rect is None:
                rect = sprite.rect.copy()  # Initialize rect with the first sprite's rect
            else:
                rect.union_ip(sprite.rect)  # Union the rects of all sprites in the group
        return rect