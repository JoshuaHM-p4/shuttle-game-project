import pygame as pg
from pygame.locals import *
from data.sprites import *
import math

from data.booster import *
from data.tank import *

class Shuttle:
    def __init__(self, vector):
        super().__init__()
        self.default_surfaces = pg.image.load('./resources/Shuttle/shuttle_tank.png').convert_alpha()
        self.thrust_surfaces = [pg.image.load(f"./resources/Shuttle/shuttle_tank_{i}.png").convert_alpha() for i in range(1,6)]

        shuttle_only_default_surfaces = pg.image.load("./resources/Shuttle/shuttle_only_default.png").convert_alpha()
        shuttle_only_thrust_surfaces = pg.image.load("./resources/Shuttle/shuttle_only_1.png")
        rcs_left_surface = pg.image.load("./resources/Shuttle/shuttle_l.png")
        rcs_right_surfaces = pg.image.load("./resources/Shuttle/shuttle_r.png")

        self.default_frames = pg.sprite.Group()
        self.thrust_frames = pg.sprite.Group()
        self.rcs_left_frames = pg.sprite.Group()
        self.rcs_right_frames = pg.sprite.Group()

        self.shuttle_only_default_frames = pg.sprite.Group()
        self.shuttle_only_thrust_frames = pg.sprite.Group()


        default_sprite = ShuttleSprite(self.default_surfaces, vector)
        thrust_sprite = ShuttleSprite(self.thrust_surfaces, vector)
        rcs_left_sprite = ShuttleSprite(rcs_left_surface, vector)
        rcs_right_sprite = ShuttleSprite(rcs_right_surfaces, vector)
        shuttle_only_default_sprites = ShuttleSprite(shuttle_only_default_surfaces, vector)
        shuttle_only_thrust_sprites = ShuttleSprite(shuttle_only_thrust_surfaces, vector)

        self.default_frames.add(default_sprite)
        self.thrust_frames.add(thrust_sprite)
        self.rcs_left_frames.add(rcs_left_sprite)
        self.rcs_right_frames.add(rcs_right_sprite)
        self.shuttle_only_default_frames.add(shuttle_only_default_sprites)
        self.shuttle_only_thrust_frames.add(shuttle_only_thrust_sprites)
        self.current_frames = self.default_frames.copy()

        self.rect = self.get_group_rect(self.current_frames)

        screen = pg.display.get_surface()
        self.area = screen.get_rect()

        self.main_engine = pg.mixer.Sound("./resources/main_engine.wav")
        self.decouple = pg.mixer.Sound("./resources/undock.wav")
        self.decouple.set_volume(0.5)
        self.rcs_engine = pg.mixer.Sound("./resources/RCS.wav")
        self.rcs_engine.set_volume(0.5)

        ## Motion constants ##
        self.ROTATION_SPEED = 0.02 # degrees/second
        self.MAX_SPEED = 250      # pixels/seconddefault_surfaces
        self.DRAG = 0.01           # pixels/seconds
        self.THRUST_POWER = 0.25
        self.MASS = 500
        self.GROUND_LEVEL = (self.area.height - vector.y)
        self.BOOSTER_DISTANCE = 25  # Adjust the distance of the parallel lines as needed
        self.ROCKET_HEIGHT = self.rect.height

        self.acceleration = 0
        self.originpos = pg.Vector2(vector.x - self.rect.width / 2, vector.y) # Initialize initial original position
        self.position = pg.Vector2(vector.x - self.rect.width / 2, vector.y) # Initialize position (on screen)
        self.velocity = pg.Vector2() # Initialize Velocity
        self.altitude =  self.GROUND_LEVEL # Initialize altitude at Rect Bottom
        self.angle = 0
        self.angular_velocity = 0
        self.thrust = 0

        self.exhaust_line_1 = pg.Vector2()
        self.exhaust_line_2 = pg.Vector2()
        self.r_booster_pos = pg.Vector2()
        self.l_booster_pos = pg.Vector2()
        self.r_exhaust_pos = pg.Vector2()
        self.l_exhaust_pos = pg.Vector2()

        self.touchdown = True
        self.engine_fire = False
        self.rcs_fire_r = self.rcs_fire_l = False
        self.crashed = False
        self.game_crash = False
        self.booster_attached = True
        self.tank_attached = True

        for sprite in self.current_frames:
            sprite.update((vector.x - self.rect.width / 2, vector.y))
        self.calculate_booster()

    def update(self):
        for sprite in self.current_frames:
            sprite.update(self.position)

        for sprite in self.rcs_right_frames:
            sprite.update(self.position)

        for sprite in self.rcs_left_frames:
            sprite.update(self.position)

        self.rect = self.get_group_rect(self.current_frames)

    def draw(self, screen):
        if not self.crashed:
            self.current_frames.draw(screen)

        if self.rcs_fire_l:
            self.rcs_left_frames.draw(screen)

        if self.rcs_fire_r:
            self.rcs_right_frames.draw(screen)


    def calculate_booster(self):
        x1,y1  = self.exhaust_line_1
        x2,y2 = self.exhaust_line_2
        angle_rad =math.radians(self.angle)
        perpendicular_angle_rad = angle_rad + math.pi / 2  # Perpendicular angle

        # Right Booster
        x3 = x1 + self.BOOSTER_DISTANCE * math.sin(perpendicular_angle_rad)
        y3 = y1 + self.BOOSTER_DISTANCE * math.cos(perpendicular_angle_rad)
        x4 = x2 + self.BOOSTER_DISTANCE * math.sin(perpendicular_angle_rad)
        y4 = y2 + self.BOOSTER_DISTANCE * math.cos(perpendicular_angle_rad)

        # Left boosters
        x5 = x1 + -self.BOOSTER_DISTANCE * math.sin(perpendicular_angle_rad)
        y5 = y1 + -self.BOOSTER_DISTANCE * math.cos(perpendicular_angle_rad)
        x6 = x2 + -self.BOOSTER_DISTANCE * math.sin(perpendicular_angle_rad)
        y6 = y2 + -self.BOOSTER_DISTANCE * math.cos(perpendicular_angle_rad)

        # Draw the parallel lines
        self.r_booster_pos = pg.Vector2(x3,y3)
        self.l_booster_pos = pg.Vector2(x5,y5)
        self.r_exhaust_pos = pg.Vector2(x4,y4)
        self.l_exhaust_pos = pg.Vector2(x6,y6)

    def debug(self,screen, font):
        text_surface = font.render(f"Position: {self.position}", True, (255,255,255))
        screen.blit(text_surface, (self.position.x + self.rect.width, self.position.y + self.rect.height))
        pg.draw.rect(screen, (0,0,0), self.rect, 2)
        pg.draw.line(screen, (255,0,0), (0,self.area.height - self.GROUND_LEVEL), (self.area.width, self.area.height - self.GROUND_LEVEL))
        pg.draw.line(screen, (255,0,0), (self.area.width//2, 0), (self.area.width//2, self.area.height))
        pg.draw.line(screen, (255,0,0), (0, self.area.height//2), (self.area.width, self.area.height//2))
        # pg.draw.line(screen, (255,255,255), (0,self.area.height - self.altitude), (self.area.width, self.area.height - self.altitude))
        pg.draw.line(screen, (255,0,255), (0,self.position.y), (self.area.width, self.position.y))

        pg.draw.line(screen, (255, 255, 255),self.exhaust_line_1,self.exhaust_line_2, 2) # rocket line position exhaust
        # pg.draw.line(screen, (255, 255, 255),self.r_booster_pos,self.r_exhaust_pos, 2)
        # pg.draw.line(screen, (255, 255, 255),self.l_booster_pos,self.l_exhaust_pos, 2)
        pg.draw.circle(screen, (0,255,0), self.position, 3) # position of rocket
        pg.draw.circle(screen, (255,255,255), self.rect.center, 5) # center rect of rocket
        pg.draw.circle(screen, (0,255,255), self.originpos, radius = 5)

    def calc(self, gravity):
        self.rotate()

        if self.booster_attached:
            self.calculate_booster()

        if self.velocity.y <= -1 and (self.position.y - self.velocity.y) >= self.originpos.y:
            self.crashed = True

        ## Thrust Engine Fire
        Vx = Vy = 0

        if self.engine_fire:
            # Calculate trust and acceleration
            self.thrust += self.THRUST_POWER
            self.acceleration = self.thrust / self.MASS

            # Convert angle to radians
            angle_rad = math.radians(self.angle)

            # Calculate thrust components based on angle
            thrust_horizontal = math.sin(angle_rad) * self.thrust
            thrust_vertical = math.cos(angle_rad) * self.thrust

            # Calculate acceleration components
            acceleration_horizontal = thrust_horizontal / self.MASS
            acceleration_vertical = (thrust_vertical / self.MASS) - gravity

            # Update velocities based on acceleration
            Vx += acceleration_horizontal
            Vy += acceleration_vertical
        else:
            ## Horizontal Air Drag
            self.thrust = 0
            if self.velocity.x > 0:
                Vx = -self.DRAG
            else:
                Vx = self.DRAG

        # Calculate velocity
        self.velocity += pg.Vector2(Vx, Vy)

        # Restrict Position of the rocket centeron screen (Note: self.area = screen.get_rect())

        if (self.rect.centery <= self.area.height // 2 and self.velocity.y > 0):
            self.position.y += (self.area.height // 2) - (self.rect.height//2 + self.position.y)   # Center the rocket after reaching the
        elif int(self.rect.y) <= self.area.height - int(self.altitude):
            self.position.y -= self.velocity.y

        if not self.touchdown:
            self.altitude += self.velocity.y

        # Check if the rocket is at the ground level
        if self.position.y >= self.originpos.y:
            self.touchdown = True
            self.position.y = self.originpos.y # Ensure rocket stays at ground level
            self.altitude = self.GROUND_LEVEL # Reset altitude to ground level
            self.velocity.y = 0  # Stop vertical movement
        else:
            ## Force of Gravity
            self.velocity.y -= gravity

        # Update Exhaust Line
        angle_rad = math.radians(self.angle)
        line_length = self.ROCKET_HEIGHT // 2  - 20 # Adjust the line length as needed
        x1 = self.rect.centerx - line_length *  math.sin(angle_rad)
        y1 = self.rect.centery - line_length * math.cos(angle_rad)
        x2 = self.rect.centerx + line_length * math.sin(angle_rad)
        y2 = self.rect.centery + line_length * math.cos(angle_rad)
        self.exhaust_line_1 = pg.Vector2(x1,y1)
        self.exhaust_line_2 = pg.Vector2(x2,y2)

        if self.velocity.y > 0:
            self.touchdown = False


    def rotate(self):
        # Tips the rocket left or right
        if self.rcs_fire_l or self.rcs_fire_r:

            self.angular_velocity -= self.ROTATION_SPEED if self.rcs_fire_l else 0 # Increase turn right
            self.angular_velocity += self.ROTATION_SPEED if self.rcs_fire_r else 0 # Increase turn left
            self.angle -= self.angular_velocity # Apply rcs power to angle

            # Ensure angle is at Reasonable Range (0 to 360)
            self.angle %= 360

            for sprite in self.default_frames:
                sprite.rotate(self.angle)
            for sprite in self.thrust_frames:
                sprite.rotate(self.angle)
            for sprite in self.rcs_right_frames:
                sprite.rotate(self.angle)
            for sprite in self.rcs_left_frames:
                sprite.rotate(self.angle)
            for sprite in self.shuttle_only_default_frames:
                sprite.rotate(self.angle)
            for sprite in self.shuttle_only_thrust_frames:
                sprite.rotate(self.angle)

            # Center the Position
            self.position.x = self.area.width // 2 - self.rect.width//2

        else:
            self.angular_velocity = 0

    def reset(self):
        self.position = pg.Vector2(self.originpos).copy()
        self.velocity = pg.Vector2()
        self.rect = self.get_group_rect(self.current_frames)
        self.angular_velocity = self.thrust = self.angle = 0
        self.altitude = self.GROUND_LEVEL
        self.touchdown = True
        self.crashed = self.engine_fire = self.rcs_fire_l = self.rcs_fire_r = False
        self.game_crash = False
        self.booster_attached = True
        self.tank_attached = True
        for sprite in self.current_frames:
            sprite.reset()
        for sprite in self.thrust_frames:
            sprite.reset()
        for sprite in self.default_frames:
            sprite.reset()
        for sprite in self.rcs_left_frames:
            sprite.reset()
        for sprite in self.rcs_right_frames:
            sprite.reset()
        for sprite in self.shuttle_only_default_frames:
            sprite.reset()
        for sprite in self.shuttle_only_thrust_frames:
            sprite.reset()

    def input(self, key, type):
        if type == KEYDOWN:
            if key == K_UP and not self.crashed:
                self.engine_fire = True
                self.main_engine.play(loops=-1)
                self.current_frames = self.thrust_frames.copy()
            if key == K_RIGHT and not self.crashed:
                self.rcs_fire_r = True
                self.rcs_engine.play(loops=-1)
            if key == K_LEFT and not self.crashed:
                self.rcs_fire_l = True
                self.rcs_engine.play(loops=-1)
            if key == K_1:
                self.crashed = True
            if key == K_2:
                self.crashed = True
                self.game_crash = True
            if key == K_SPACE:
                if self.booster_attached:
                    self.booster_attached = False
                    self.decouple.play()
                elif self.tank_attached:
                    self.tank_attached = False
                    self.default_frames = self.shuttle_only_default_frames.copy()
                    self.thrust_frames = self.shuttle_only_thrust_frames.copy()
                    if self.engine_fire:
                        self.current_frames = self.thrust_frames.copy()
                    else:
                        self.current_frames = self.default_frames.copy()
                    self.decouple.play()
            if key == K_ESCAPE:
                self.reset()

        if type == KEYUP:
            if key == K_UP:
                self.engine_fire = False
                self.main_engine.stop()
                self.current_frames = self.default_frames.copy()
            if key == K_RIGHT:
                self.rcs_fire_r = False
                self.rcs_engine.stop()
            if key == K_LEFT:
                self.rcs_fire_l = False
                self.rcs_engine.stop()

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