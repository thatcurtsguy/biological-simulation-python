import pygame as pg

from pygame import Vector2, Rect
from numpy.random import uniform

class ScreenAssist:
    def __init__(self, screen : pg.Surface, border : Rect) -> None:
        self.border = border
        self.screen = screen
    

    def apply_translation(self):
        self.screen.blit(self.screen, (0, 0), (0, 0, 200, 200))


    def toroidal_direction(self, position1: Vector2, position2: Vector2):
        direction = position2 - position1
        if direction.x > self.border.width / 2:
            direction.x -= self.border.width
        elif direction.x < -self.border.width / 2:
            direction.x += self.border.width
        if direction.y > self.border.height / 2:
            direction.y -= self.border.height
        elif direction.y < -self.border.height / 2:
            direction.y += self.border.height
        return direction


    def toroidal_distance(self, position1, position2):
        # Calculation of toroidal distance between two positions in a wrap around space
        delta_x = min(abs(position1.x - position2.x), self.border.width - abs(position1.x - position2.x))
        delta_y = min(abs(position1.y - position2.y), self.border.height - abs(position1.y - position2.y))
        toroidal_distance = (delta_x ** 2 + delta_y ** 2) ** 0.5
        return toroidal_distance


    def randPosition(self, border : Rect = None) -> Vector2:
        used_border = border if border != None else self.border
        return Vector2(
            uniform(used_border.left, used_border.left + used_border.width), 
            uniform(used_border.top,  used_border.top  + used_border.height)
            )

    def randVelocity(self, min_acc, max_acc) -> Vector2:
        return Vector2(tuple(uniform(min_acc, max_acc, 2)))