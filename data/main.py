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
    bg_surface = pg.image.load('./resources/BG.png').convert()
    bg2_surface = pg.image.load("./resources/BG_2.png").convert()
    space_surface = pg.image.load('./resources/space.png').convert_alpha()

    ## Initialize Game Elements
    # Shuttle
    starting_position = pg.Vector2(SCREEN_WIDTH//2, SCREEN_HEIGHT-240)
    shuttle = Shuttle(starting_position)
    tank = Tank(shuttle)
    right_booster = Booster(shuttle, "R") # right booster frames
    left_booster = Booster(shuttle, "L") # left booster frames

    # Background
    pad_bg = Background(screen, bg_surface, (0,0), surface_only=True)
    atmosphere_bg = Background(screen, bg2_surface, (0,-SCREEN_HEIGHT))
    space_bg = Background(screen, space_surface, (0, -SCREEN_HEIGHT*2), double_stack=True)

    # Sprites
    # Explosion images
    explosion_images = [pg.image.load(f"./resources/explosion/water{i}.png").convert_alpha() for i in range(1,9)]
    explosion_group = pg.sprite.Group()

    smoke_images =[pg.image.load(f"./resources/smoke/smoke{i}.png").convert_alpha() for i in range(1,6)]
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
                            atmosphere_bg.reset()
                            space_bg.reset()
                        case pg.K_F1:
                            debug_mode = not debug_mode
                    shuttle.input(event.key, KEYDOWN)
                    right_booster.input(event.key, KEYDOWN)
                    left_booster.input(event.key, KEYDOWN)
                    tank.input(event.key, KEYDOWN)
                case pg.KEYUP:
                    shuttle.input(event.key, KEYUP)
                    right_booster.input(event.key, KEYUP)
                    left_booster.input(event.key, KEYUP)

        ## Update Space Shuttle
        shuttle.calc(gravity)
        shuttle.update()

        if shuttle.booster_attached:
            right_booster.attach(shuttle.r_booster_pos, shuttle.angle, shuttle.velocity, shuttle.altitude)
            left_booster.attach(shuttle.l_booster_pos, shuttle.angle, shuttle.velocity, shuttle.altitude)
        else:
            right_booster.jettison(shuttle, gravity, "R")
            left_booster.jettison(shuttle, gravity, "L")

        if not right_booster.crashed:
            right_booster.update()
        if not left_booster.crashed:
            left_booster.update()

        if shuttle.tank_attached:
            tank.attach(shuttle)
        else:
            tank.jettison(shuttle, gravity, "B")

        tank.update()

        ## Update Background based on Space Shuttle Velocity
        pad_bg.update(shuttle)
        atmosphere_bg.update(shuttle)
        space_bg.update(shuttle)

        ## Background
        screen.fill((20, 24, 46))  # Clear screen
        space_bg.display_surface(screen)
        atmosphere_bg.display_surface(screen)
        pad_bg.display_surface(screen) # Display Pad Background

        ## Display Shuttle
        right_booster.draw(screen)
        left_booster.draw(screen)
        tank.draw(screen)
        shuttle.draw(screen)

        # Check if the engine is firing and inside atmosphere
        if shuttle.engine_fire and shuttle.altitude < 960:
            # Create smoke sprites when the engine is firing
            opposite_velocity = (-shuttle.velocity[0], -shuttle.velocity[1])
            for _ in range(1):  # Adjust the number of smoke sprites as needed
                smoke_sprite = SmokeSprite(smoke_images, shuttle.exhaust_line_2, opposite_velocity)
                smoke_group.add(smoke_sprite)

        if right_booster.engine_fire and right_booster.altitude < 960:
            opposite_velocity = (-right_booster.velocity[0], -right_booster.velocity[1])
            for _ in range(1):  # Adjust the number of smoke sprites as needed
                smoke_sprite = SmokeSprite(smoke_images, right_booster.exhaust_line_2, opposite_velocity)
                smoke_group.add(smoke_sprite)

        if left_booster.engine_fire and left_booster.altitude < 960:
            opposite_velocity = (-left_booster.velocity[0], -left_booster.velocity[1])
            for _ in range(1):  # Adjust the number of smoke sprites as needed
                smoke_sprite = SmokeSprite(smoke_images, left_booster.exhaust_line_2, opposite_velocity)
                smoke_group.add(smoke_sprite)

        smoke_group.update()

        # Remove smoke sprites that have finished their animation
        for smoke_sprite in smoke_group.sprites():
            if not pg.sprite.spritecollideany(smoke_sprite, smoke_group):
                smoke_sprite.kill()

        smoke_group.draw(screen)

        ## Handle if Shuttle State is Crashed
        if shuttle.crashed or right_booster.crashed or left_booster.crashed or tank.crashed:
            # Display the explosion sprite
            if not crash_time and shuttle.crashed:
                # Calculate the time since the crash
                crash_time = pg.time.get_ticks()

                # Initiate Explosion Sprite
                crash_position = shuttle.rect.midbottom
                explosion_sprite = ExplosionSprite(explosion_images, crash_position)
                explosion_group.add(explosion_sprite)

                # Initiate Erorr message
                error_message = game_font.render("Rocket Exploded! Game Over!", True, (255,0,0))
                if shuttle.game_crash:
                    error_message = game_font.render("Error!", True, (255,0,0))
                error_rect = error_message.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))

                # Stop music and play explosion
                pg.mixer.stop()
                explosion_sfx[randint(0,6)].play()

            if left_booster.crashed and not left_booster.gone:
                crash_position = left_booster.rect.midbottom
                explosion_sprite = ExplosionSprite(explosion_images, crash_position)
                explosion_group.add(explosion_sprite)
                explosion_sfx[randint(0,6)].play()
                left_booster.gone = True

            if right_booster.crashed and not right_booster.gone:
                crash_position = left_booster.rect.midbottom
                explosion_sprite = ExplosionSprite(explosion_images, crash_position)
                explosion_group.add(explosion_sprite)
                explosion_sfx[randint(0,6)].play()
                right_booster.gone = True

            if tank.crashed and not tank.gone:
                crash_position = tank.rect.midbottom
                explosion_sprite = ExplosionSprite(explosion_images, crash_position)
                explosion_group.add(explosion_sprite)
                explosion_sfx[randint(0,6)].play()
                tank.gone = True

            explosion_group.update()
            explosion_group.draw(screen)

            for explosion_sprite in explosion_group.sprites():
                if not pg.sprite.spritecollideany(explosion_sprite, explosion_group):
                    explosion_sprite.kill()

            if shuttle.crashed:
                # Display error message
                screen.blit(error_message, error_rect)

            if shuttle.crashed and pg.time.get_ticks() - crash_time >= 2000:
                # Reset the game
                shuttle.reset()
                tank.reset()
                right_booster.reset()
                left_booster.reset()
                pad_bg.reset()
                space_bg.reset()
                crashed = False
                crash_time = 0
                menu_bgm.play(loops=-1)
                update_music = False

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
            atmosphere_bg.debug(screen,game_font, color = (0,255,255))
            right_booster.debug(screen, game_font)
            left_booster.debug(screen, game_font)
            tank.debug(screen, game_font)
            values = get_shuttle_values(shuttle)
            debug.display(screen, values)
        pg.display.flip()
        clock.tick(60)