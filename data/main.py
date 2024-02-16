import pygame as pg
import os
from random import randint
from pygame.locals import *
from data.shuttle import *
from data.debug import *
from data.background import *
from data.sprites import *

def main():
    pg.init()

    ## Initialize Pygame
    SCREEN_WIDTH = 960
    SCREEN_HEIGHT = 720
    SCREEN_SIZE = (SCREEN_WIDTH, SCREEN_HEIGHT)
    screen = pg.display.set_mode(SCREEN_SIZE)
    clock = pg.time.Clock()
    game_font = pg.font.Font('./resources/04B_19.TTF', 30)

    # Music and Sound
    menu_bgm = pg.mixer.Sound('./resources/Dixiklo - KSP Mission Control.wav')
    launch_bgm = pg.mixer.Sound('./resources/Dixiklo - Jupiter, the Bringer of Jollity.wav')
    menu_bgm.set_volume(0.5)
    launch_bgm.set_volume(0.5)
    update_music = False

    explosion_sfx = [pg.mixer.Sound(f"./resources/explosion_sound/boom{i}.wav") for i in range(1,7)] + [pg.mixer.Sound("./resources/explosion_sound/Fireworks.wav")]
    for sfx in explosion_sfx:
        sfx.set_volume(0.3)

    # Declare Background Surface
    bg_surface = pg.image.load('./resources/moon2.png').convert()
    space_surface = pg.image.load('./resources/space.png').convert_alpha()

    ## Initialize Game Elements
    # Shuttle
    starting_position = pg.Vector2(SCREEN_WIDTH//2, SCREEN_HEIGHT-120)
    shuttle = Shuttle(starting_position)

    # Background
    pad_bg = Background(screen, bg_surface, (0,0), surface_only=True)
    space_bg = Background(screen, space_surface, (0, -SCREEN_SIZE[1]), double_stack=True)

    # Sprites
    # Explosion images
    explosion_images = [pg.image.load(f"./resources/explosion/water{i}.png").convert_alpha() for i in range(1,9)]
    explosion_group = pg.sprite.Group()

    smoke_images =[pg.image.load(f"./resources/explosion/smoke{i}.png").convert_alpha() for i in range(1,6)]
    smoke_group = pg.sprite.Group()

    ## Declare Game States and Constants
    running = True
    game_active = False
    debug_mode = False
    gravity = 0.025
    crashed = False
    crash_time = 0

    debug = debug_shuttle(game_font, shuttle)

    ### < GAME LOOP > ###
    while running:
        pos = pg.mouse.get_pos()
        for event in pg.event.get():
            match event.type:
                case pg.QUIT:
                    running = not running
                case pg.KEYDOWN:
                    match event.key:
                        case pg.K_ESCAPE:
                            pad_bg.reset()
                            space_bg.reset()
                        case pg.K_F1:
                            debug_mode = not debug_mode
                    shuttle.input(event.key, KEYDOWN)
                case pg.KEYUP:
                    shuttle.input(event.key, KEYUP)

        ## Update Space Shuttle
        shuttle.calc(gravity)
        shuttle.update()

        ## Update Background based on Space Shuttle Velocity
        pad_bg.update(shuttle)
        space_bg.update(shuttle)

        ## Background
        screen.fill((20, 24, 46))  # Clear screen
        space_bg.display_surface(screen)
        pad_bg.display_surface(screen) # Display Pad Background

        ## Display Shuttle
        shuttle.draw(screen)

        ## Handle Game Events
        

        ## Handle if Shuttle State is Crashed
        if shuttle.crashed:
            # Display the explosion sprite
            if not crash_time:
                # Calculate the time since the crash
                crash_time = pg.time.get_ticks()

                # Initiate Explosion Sprite
                crash_position = shuttle.rect.midbottom
                explosion_sprite = ParticleSprite(explosion_images, crash_position)
                explosion_group.add(explosion_sprite)

                # Initiate Erorr message
                error_message = game_font.render("Rocket Exploded! Game Over!", True, (255,0,0))
                if shuttle.game_crash:
                    error_message = game_font.render("Error!", True, (255,0,0))
                error_rect = error_message.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))

                # Stop music and play explosion
                pg.mixer.stop()
                explosion_sfx[randint(0,6)].play()

            # Display error message
            screen.blit(error_message, error_rect)

            if pg.time.get_ticks() - crash_time >= 2000:
                # Reset the game
                shuttle.reset()
                pad_bg.reset()
                space_bg.reset()
                crashed = False
                crash_time = 0
                menu_bgm.play(loops=-1)

        explosion_group.update()
        explosion_group.draw(screen)

        # Change music between touchdown and after launch
        if shuttle.touchdown and not shuttle.crashed:
            if not update_music:
                launch_bgm.stop()
                menu_bgm.play(loops=-1)
                update_music = True
        else:
            if update_music:
                menu_bgm.stop()
                launch_bgm.play(loops=-1)
                update_music = False

        ## Display Debug
        if debug_mode:
            shuttle.debug(screen, game_font)
            pad_bg.debug(screen, game_font, color = (0,255,0))
            space_bg.debug(screen, game_font, color = (255,0,255))
            values = get_shuttle_values(shuttle)
            debug.display(screen, values)


        pg.display.flip()
        clock.tick(60)

        # if not shuttle.touchdown:
        #     bg_scroll_1 += shuttle.velocity.y
        #     sp_scroll_y += shuttle.velocity.y

        # bg_scroll_x += shuttle.velocity.x

        # # Ensure that the background doesn't scroll past the screen boundaries
        # if bg_scroll_x < -SCREEN_SIZE[0]: # If background scroll passes one screen left
        #     bg_scroll_x += SCREEN_SIZE[0]
        # elif bg_scroll_x >= SCREEN_SIZE[0]: # If backgorund scroll passes one screen right
        #     bg_scroll_x -= SCREEN_SIZE[0]

        # # Reset space scrolling if it moves off the screen
        # if sp_scroll_y >= SCREEN_SIZE[1]: #
        #     sp_scroll_y = 0

        # Display the surface
        # screen.blit(bg_surface, (bg_scroll_x,max(0,bg_scroll_1))) # main screen
        # screen.blit(bg_surface, (bg_scroll_x+SCREEN_SIZE[0],max(0,bg_scroll_1))) # left
        # screen.blit(bg_surface, (bg_scroll_x-SCREEN_SIZE[0],max(0,bg_scroll_1))) # right
        # screen.blit(space_surface, (bg_scroll_x, sp_scroll_y))
        # screen.blit(space_surface, (bg_scroll_x, sp_scroll_y -SCREEN_SIZE[1]))
        # screen.blit(space_surface, (bg_scroll_x+SCREEN_SIZE[0], sp_scroll_y))
        # screen.blit(space_surface, (bg_scroll_x+SCREEN_SIZE[0], sp_scroll_y -SCREEN_SIZE[1]))
        # screen.blit(space_surface, (bg_scroll_x-SCREEN_SIZE[0], sp_scroll_y))
        # screen.blit(space_surface, (bg_scroll_x-SCREEN_SIZE[0], sp_scroll_y -SCREEN_SIZE[1]))

        # FOR DEBUGGING
        # pg.draw.rect(screen, (255,0,0), Rect((0,sp_scroll_1), SCREEN_SIZE), 2) # for debugging
        # sp_1_surface = game_font.render(str(sp_scroll_1), True, (255,255,255))
        # screen.blit(sp_1_surface, (0, sp_scroll_1))
        # pg.draw.rect(screen, (0,255,0), Rect((0,sp_scroll_2), SCREEN_SIZE), 2)
        # sp_2_surface = game_font.render(str(sp_scroll_2), True, (255,255,255))
        # screen.blit(sp_2_surface, (0, sp_scroll_2))
        # print(f"{sp_scroll_1:.0f} {sp_scroll_2:.0f}")



