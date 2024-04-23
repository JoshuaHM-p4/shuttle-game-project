import pygame as pg

def debug_shuttle(font, shuttle:object) -> object:
    name_field = [
        "Position: {}",
        "Rect: {}",
        "Vx: {:.2f}",
        "Vy: {:.2f}",
        "Altitude: {}",
        "Angle: {:.2f}",
        "Thrust Power: {:,.2f}",
        "Angular Velocity: {:.2f}",
        "Thrust ON: {}",
        "RCS ON: {}",
        "Touchdown: {}",
        "Crashed: {}",
        "Boosters: {}",
        "Tank: {}"
]
    debug_object = Debug_Overlay(font, name_field)
    return debug_object

def get_shuttle_values(shuttle:object) -> list:
    values = [
        shuttle.position,
        shuttle.rect,
        shuttle.velocity.x,
        shuttle.velocity.y,
        shuttle.altitude,
        shuttle.angle,
        shuttle.thrust,
        shuttle.angular_velocity,
        shuttle.engine_fire,
        (shuttle.rcs_fire_l, shuttle.rcs_fire_r),
        shuttle.touchdown,
        shuttle.crashed,
        shuttle.booster_attached,
        shuttle.tank_attached
    ]
    return values

class Debug_Overlay:
    def __init__(self, font, names):
        """ Debug Overlay for shuttle """

        screen = pg.display.get_surface()
        self.area = screen.get_rect()
        self.rect = self.area.copy()

        self.font = font
        self.height = self.font.size("Tg")[1]

        field = []
        for name in names:
            field.append(name)
        self.texts = field

    def display(self, screen, values):
        for i,text in enumerate(self.texts):
            text = text.format(values[i])
            text_surface = self.font.render(text, True, (255,255,255))
            screen.blit(text_surface, (self.rect.x, self.rect.y + self.height * i))