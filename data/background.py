import pygame as pg
from pygame.locals import *

class Background:
    def __init__(self, screen, surface, point = (0,0), surface_only = False, double_stack = False):
        screen = screen.get_rect()
        self.screen_rect = screen
        self.surface = surface
        self.screen_width = screen.width
        self.screen_height = screen.height
        self.i_point = point
        self.x_scroll  = point[0]
        self.y_scroll = point[1]
        self.surface_only = surface_only
        self.double_stack = double_stack

    def update(self, shuttle):
        move = shuttle.velocity

        self.x_scroll += move[0]
        self.y_scroll += move[1]

        # Adjust scroll position to stay within screen boundaries
        self.x_scroll %= self.screen_width
        if self.double_stack:
            self.y_scroll %= self.screen_height

    def display_surface(self, screen):
        if self.double_stack:
            screen.blit(self.surface, (self.x_scroll, self.y_scroll))
            screen.blit(self.surface, (self.x_scroll, self.y_scroll -self.screen_height))
            screen.blit(self.surface, (self.x_scroll+self.screen_width, self.y_scroll))
            screen.blit(self.surface, (self.x_scroll+self.screen_width, self.y_scroll -self.screen_height))
            screen.blit(self.surface, (self.x_scroll-self.screen_width, self.y_scroll))
            screen.blit(self.surface, (self.x_scroll-self.screen_width, self.y_scroll -self.screen_height))
        elif self.surface_only:
            screen.blit(self.surface, (self.x_scroll,max(0,self.y_scroll))) # main screen
            screen.blit(self.surface, (self.x_scroll+self.screen_width,max(0,self.y_scroll))) # right display
            screen.blit(self.surface, (self.x_scroll-self.screen_width,max(0,self.y_scroll))) # left display
        else:
            screen.blit(self.surface, (self.x_scroll,self.y_scroll)) # main screen
            screen.blit(self.surface, (self.x_scroll+self.screen_width,self.y_scroll)) # right display
            screen.blit(self.surface, (self.x_scroll-self.screen_width,self.y_scroll)) # left display


    def debug(self, screen, font, color = (0,0,0)):
        # For Debugging
        coords = f"({self.x_scroll:.0f}, {self.y_scroll:.0f})"

        pg.draw.rect(screen, color, Rect((self.x_scroll, self.y_scroll), self.screen_rect.size), 2)
        text_surface = font.render(coords, True, color)
        screen.blit(text_surface, (self.x_scroll, self.y_scroll))

    def reset(self):
        self.x_scroll = self.i_point[0]
        self.y_scroll = self.i_point[1]