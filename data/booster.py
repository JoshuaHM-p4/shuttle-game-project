import pygame as pg
from pygame.locals import *
from data.sprites import *
import math

class Booster:
    def __init__(self, shuttle, lr):
        super().__init__()


        if lr == "R":
            self.default_surfaces = pg.image.load('./resources/Shuttle/r_booster.png').convert_alpha()
            self.thrust_surfaces = pg.image.load("./resources/Shuttle/r_booster_1.png").convert_alpha()
            self.rcs_surfaces = pg.image.load('./resources/Shuttle/r_booster_rcs.png').convert_alpha()
            vector = shuttle.r_booster_pos
        elif lr == "L":
            self.default_surfaces = pg.image.load('./resources/Shuttle/l_booster.png').convert_alpha()
            self.thrust_surfaces = pg.image.load("./resources/Shuttle/l_booster_1.png").convert_alpha()
            self.rcs_surfaces = pg.image.load('./resources/Shuttle/l_booster_rcs.png').convert_alpha()
            vector = shuttle.l_booster_pos

        self.default_frames = pg.sprite.Group()
        self.thrust_frames = pg.sprite.Group()
        self.rcs_frames = pg.sprite.Group()

        default_sprite = ShuttleSprite(self.default_surfaces, vector)
        thrust_sprite = ShuttleSprite(self.thrust_surfaces, vector)
        rcs_sprite = ShuttleSprite(self.rcs_surfaces, vector)

        self.default_frames.add(default_sprite)
        self.thrust_frames.add(thrust_sprite)
        self.rcs_frames.add(rcs_sprite)
        self.current_frames = self.default_frames.copy()

        self.rect = self.get_group_rect(self.current_frames)

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
        self.originbot = self.area.height
        self.midpoint = self.originpos / 2
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

        for sprite in self.current_frames:
            sprite.update(self.position)

    def attach(self, position, angle, velocity, altitude):
        # Calculate the coordinates of the second endpoint
        self.angle = angle

        angle_rad = math.radians(-angle)

        x2 = position[0] - self.ROCKET_HEIGHT * math.sin(angle_rad)
        y2 = position[1] + (self.ROCKET_HEIGHT) * math.cos(angle_rad)

        self.exhaust_line_1 = position
        self.exhaust_line_2 = pg.Vector2(x2,y2)

        midpoint = (self.exhaust_line_1 + self.exhaust_line_2) / 2
        self.midpoint = midpoint
        self.velocity = velocity.copy()
        self.altitude = altitude

    def update(self):
        for sprite in self.current_frames:
            sprite.update(self.midpoint, center = True)
            sprite.rotate(self.angle)
        for sprite in self.default_frames:
            sprite.update(self.midpoint, center = True)
            sprite.rotate(self.angle)
        for sprite in self.thrust_frames:
            sprite.update(self.midpoint, center = True)
            sprite.rotate(self.angle)
        for sprite in self.rcs_frames:
            sprite.update(self.midpoint, center = True)

        if self.jettisoned:
            self.current_frames = self.rcs_frames.copy()

        self.rect = self.get_group_rect(self.current_frames)

    def draw(self, screen):
        if not self.crashed and not self.gone:
            self.current_frames.draw(screen)

    def debug(self,screen, font):
        pg.draw.rect(screen, (0,0,0), self.rect, 2)

        # Draw the line inscribing the rect
        pg.draw.circle(screen, (0,255,0), self.debug_position, radius = 3)
        pg.draw.circle(screen, (255,0,255), self.rect.center, radius = 5)
        pg.draw.line(screen, (255, 255, 255),self.exhaust_line_1,self.exhaust_line_2, 2)
        pg.draw.line(screen, (255,255,0), (0,self.originbot - self.altitude), (self.area.width, self.originbot - self.altitude))
        pg.draw.line(screen, (255,255,255), (0, self.originpos.y), (self.area.width, self.originpos.y), width = 5)

    def jettison(self, shuttle, gravity, direction):
        if not self.gone and not self.crashed:
            # Jettison
            self.angular_velocity += 0.02  if direction == "R" else 0 # Increase turn right
            self.angular_velocity -= 0.02 if direction == "L" else 0 # Increase turn left
            self.angle -= self.angular_velocity # Apply rcs power to angle
            self.angle %= 360 # Ensure angle is at Reasonable Range (0 to 360)
            self.thrust = True
            self.jettisoned = True

            self.midpoint += shuttle.velocity.copy()

            if self.velocity.x > 0:
                Vx = -self.DRAG
            else:
                Vx = self.DRAG

            self.velocity.x += Vx
            self.velocity.y -= gravity
            self.altitude += self.velocity.y - shuttle.velocity.y

            self.midpoint -= self.velocity


            # Update Exhaust Line
            angle_rad = math.radians(self.angle)
            line_length = self.ROCKET_HEIGHT / 2   # Adjust the line length as needed
            x1 = self.midpoint.x - line_length  * math.sin(angle_rad)
            y1 = self.midpoint.y - line_length  * math.cos(angle_rad)
            x2 = self.midpoint.x + line_length * math.sin(angle_rad)
            y2 = self.midpoint.y + (line_length-120) * math.cos(angle_rad)
            self.exhaust_line_1 = pg.Vector2(x1,y1)
            self.exhaust_line_2 = pg.Vector2(x2,y2)

            if self.velocity.y > 0:
                self.touchdown = False

            if self.velocity.y <= -1 and  (self.position.y - self.velocity.y) >= self.originpos.y:
                self.crashed = True

    def reset(self):
        self.position = pg.Vector2(self.originpos).copy()
        self.velocity = pg.Vector2()
        self.rect = self.get_group_rect(self.current_frames)
        self.angular_velocity = self.thrust = self.angle = 0
        self.altitude = self.GROUND_LEVEL
        self.touchdown = True
        self.crashed = False
        self.gone = False
        self.jettisoned = False
        for sprite in self.current_frames:
            sprite.reset()
        for sprite in self.thrust_frames:
            sprite.reset()
        for sprite in self.default_frames:
            sprite.reset()
        for sprite in self.rcs_frames:
            sprite.reset()


    def input(self, key, type):
        if type == KEYDOWN:
            if key == K_UP and not self.crashed:
                self.engine_fire = True
                self.main_engine.play(loops=-1)
                self.current_frames = self.thrust_frames.copy()
            if key == K_1:
                self.crashed = True
            if key == K_2:
                self.crashed = True
            if key == K_ESCAPE:
                self.reset()

        if type == KEYUP:
            if key == K_UP:
                self.engine_fire = False
                self.main_engine.stop()
                self.current_frames = self.default_frames.copy()

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