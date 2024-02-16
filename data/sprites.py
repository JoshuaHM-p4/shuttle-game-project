import pygame as pg
from pygame.locals import *

class ParticleSprite(pg.sprite.Sprite):
    def __init__(self, images, position):
        super().__init__()
        self.image_index = 0
        self.images = images
        self.image = self.images[self.image_index]
        self.rect = self.image.get_rect(center=position)
        self.animation_speed = 0.1  # Adjust the animation speed as needed

    def update(self):
        # Update the animation frame
        self.image_index += self.animation_speed
        if self.image_index >= len(self.images):
            # If we've reached the end of the animation, remove the explosion sprite
            self.kill()
        else:
            self.image = self.images[int(self.image_index)]
            self.rect = self.image.get_rect(center=self.rect.center)

class ShuttleSprite(pg.sprite.Sprite):
    def __init__(self, images, position):
        super().__init__()
        self.image_index = 0

        if isinstance(images, list):
            self.images = [image.copy() for image in images]  # Make copies of the images
            self.clean_images = [image.copy() for image in images]  # Store clean copies for rotation
        else:
            self.images = [images.copy()]  # Convert single image to list for consistency
            self.clean_images = [images.copy()]

        self.image = self.images[self.image_index]
        # self.rect = self.image.get_rect(center=position)
        self.rect = self.image.get_rect(center=position)
        self.animation_speed = 0.1  # Adjust the animation speed as needed

    def update(self, position):
        self.image_index += self.animation_speed
        if self.image_index >= len(self.images):
            self.image_index = 0
        self.image = self.images[int(self.image_index)]
        self.rect.topleft = position

    def rotate(self, angle):
        # Rotate the clean images and set the current image to the rotated version
        if isinstance(self.images,list):
            rotated_images = [pg.transform.rotate(image, angle) for image in self.clean_images]
            self.images = rotated_images
            self.image = self.images[int(self.image_index)]  # Update the current image
        else:
            rotated_image = pg.transform.rotate(self.clean_images, angle)
            self.image = rotated_image

        self.rect = self.image.get_rect(center=self.rect.center)

    def reset(self):
        # Reset images to clean copy
        self.images = self.clean_images.copy()
        self.rect = self.image.get_rect(center=self.rect.center)
