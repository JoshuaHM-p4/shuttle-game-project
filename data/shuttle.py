import pygame as pg
from pygame.locals import *
from data.sprites import *
import math

class Shuttle:
    def __init__(self, vector):
        super().__init__()
        self.default_surfaces = pg.image.load('./resources/Shuttle/Shuttle.png').convert_alpha()
        self.thrust_surfaces = [pg.image.load(f"./resources/Shuttle/Shuttle{i}.png").convert_alpha() for i in range(1,3)]

        self.default_frames = pg.sprite.Group()
        self.thrust_frames = pg.sprite.Group()

        default_sprite = ShuttleSprite(self.default_surfaces, vector)
        thrust_sprite = ShuttleSprite(self.thrust_surfaces, vector)
        # explosion_sprites = pg.sprite.Sprite(self.explosion_surfaces, vector)

        self.default_frames.add(default_sprite)
        self.thrust_frames.add(thrust_sprite)
        self.current_frames = self.default_frames.copy()

        self.rect = self.get_group_rect(self.current_frames)

        screen = pg.display.get_surface()
        self.area = screen.get_rect()

        self.main_engine = pg.mixer.Sound("./resources/main_engine.wav")
        self.rcs_engine = pg.mixer.Sound("./resources/RCS.wav")
        self.rcs_engine.set_volume(0.5)

        ## Motion constants ##
        self.ROTATION_SPEED = 180 # degrees/second
        self.MAX_SPEED = 250      # pixels/second
        self.DRAG = 0.01           # pixels/seconds
        self.THRUST_POWER = 0.25
        self.MASS = 500
        self.GROUND_LEVEL = (self.area.height - vector.y)

        self.acceleration = 0
        self.originpos = pg.Vector2(vector.x - self.rect.width / 2, vector.y) # Initialize initial original position
        self.position = pg.Vector2(vector.x - self.rect.width / 2, vector.y) # Initialize position (on screen)
        self.velocity = pg.Vector2() # Initialize Velocity
        self.altitude =  self.GROUND_LEVEL # Initialize altitude at Rect Bottom
        self.angle = 0
        self.angular_velocity = 0
        self.thrust = 0
        self.touchdown = True
        self.engine_fire = False
        self.rcs_fire_r = self.rcs_fire_l = False
        self.crashed = False
        self.game_crash = False
        # print(f"ground level: {self.GROUND_LEVEL}, {self.altitude}\nBottom: {self.area.height - self.rect.bottom}")

        for sprite in self.current_frames:
            sprite.update((vector.x - self.rect.width / 2, vector.y))

    def update(self):
        for sprite in self.current_frames:
            sprite.update(self.position)

        self.rect = self.get_group_rect(self.current_frames)

        if self.velocity.y <= -1 and (self.position.y - self.velocity.y) >= self.originpos.y:
            self.crashed = True

    def draw(self, screen):
        if not self.crashed:
            self.current_frames.draw(screen)

    def debug(self,screen, font):
        pg.draw.rect(screen, (0,0,0), self.rect, 2)
        text_surface = font.render(f"Position: {self.position}", True, (255,255,255))
        screen.blit(text_surface, (self.position.x + self.rect.width, self.position.y + self.rect.height))
        pg.draw.line(screen, (255,255,255), (0,self.area.height - self.GROUND_LEVEL), (self.area.width, self.area.height - self.GROUND_LEVEL))
        pg.draw.line(screen, (255,0,0), (self.area.width//2, 0), (self.area.width//2, self.area.height))
        pg.draw.line(screen, (255,0,0), (0, self.area.height//2), (self.area.width, self.area.height//2))
        pg.draw.line(screen, (255,255,255), (0,self.area.height - self.altitude), (self.area.width, self.area.height - self.altitude))
        pg.draw.line(screen, (255,0,255), (0,self.position.y), (self.area.width, self.position.y))
        # end_y = (self.area.height // 2) - (self.rect.height//2 + self.position.y)


    def calc(self, gravity):
        self.rotate()

        ## Thrust Engine Fire
        Vx = Vy = 0

        if self.engine_fire:
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

        if self.velocity.y > 0:
            self.touchdown = False


    def rotate(self):
        # Tips the rocket left or right
        if self.rcs_fire_l or self.rcs_fire_r:
            # first method
            self.angular_velocity -= 0.02 if self.rcs_fire_l else 0 # Increase turn right
            self.angular_velocity += 0.02 if self.rcs_fire_r else 0 # Increase turn left
            self.angle -= self.angular_velocity # Apply rcs power to angle

            # Ensure angle is at Reasonable Range (0 to 360)
            self.angle %= 360
            for sprite in self.default_frames:
                sprite.rotate(self.angle)
            for sprite in self.thrust_frames:
                sprite.rotate(self.angle)
        else:
            self.angular_velocity = 0

    def reset(self):
        self.position = pg.Vector2(self.originpos).copy()
        self.velocity = pg.Vector2()
        for sprite in self.current_frames:
            sprite.reset()
        for sprite in self.thrust_frames:
            sprite.reset()
        for sprite in self.default_frames:
            sprite.reset()
        self.rect = self.get_group_rect(self.current_frames)
        self.angular_velocity = self.thrust = self.angle = 0
        self.altitude = self.GROUND_LEVEL
        self.touchdown = True
        self.crashed = False
        self.game_crash = False

    def input(self, key, type):
        if type == KEYDOWN:
            if key == K_UP:
                self.engine_fire = True
                self.main_engine.play(loops=-1)
                self.current_frames = self.thrust_frames.copy()
            if key == K_RIGHT:
                self.rcs_fire_r = True
                self.rcs_engine.play(loops=-1)
            if key == K_LEFT:
                self.rcs_fire_l = True
                self.rcs_engine.play(loops=-1)
            if key == K_1:
                self.crashed = True
            if key == K_2:
                self.crashed = True
                self.game_crash = True
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