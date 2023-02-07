import pygame as pg
from pygame import Vector2
from settings import *
from numpy.random import randint, uniform

from utility_functions import *
from biomass.entity import Entity

def generateFoodColor():
    color_inline = (
        randint(0, 50),  # red
        randint(140, 255),# green
        randint(0, 50),  # blue
    )

    color_outline = (
        randint(0, 50),  # red
        color_inline[1] - 90, # green
        randint(0, 50),  # blue
    )

    return color_inline, color_outline


class Food(Entity):
    def __init__(self, screenAssist, position : Vector2, velocity : Vector2):
        super().__init__(screenAssist, position, velocity, FOOD_INITIAL_MASS, FOOD_MAX_SPEED)

        self.dead = False
        self.color_inline, self.color_outline = generateFoodColor()
        self.nearby_food = []

        self.mass = FOOD_INITIAL_MASS
        self.visual_range = FOOD_VISUAL_RANGE
    

    @classmethod
    def generate_random(cls, screenAssist):
        return Food(
            screenAssist,
            screenAssist.randPosition(),
            screenAssist.randVelocity(-1, 1)
        )
    

    def death_check(self):
        if self.dead == True or self.mass <= 0:
            return True
        return False


    def kill(self):
        self.dead = True

    def draw(self, screen):
        pg.draw.circle(screen, self.color_inline, self.position, self.mass)
        pg.draw.circle(screen, self.color_outline, self.position, self.mass, round(self.mass/4))
    

    def reproduction_check(self, all_food):
        if self.mass >= FOOD_REPRODUCTION_THRESHHOLD:
            split = randint(1, 4)
            
            for _ in range(split):
                position = Vector2(self.position.x + randint(-5, 5), self.position.y + randint(-5, 5))
                force = 166
                velocity = Vector2(uniform(-force, force), uniform(-force, force))
                all_food.append(Food(self.screenAssist, position, velocity))
            
            self.mass /= split


    def cluster(self):
        closest_food = self.get_closest(self, self.nearby_food)
        if closest_food == self or closest_food == None:
            return

        self.velocity += self.screenAssist.toroidal_direction(self.position, closest_food.position) * FOOD_CLUSTER_STRENGTH
        
    def vibrate(self):
        vibration_strength = 0.5
        self.position += Vector2(
            uniform(-vibration_strength, vibration_strength), uniform(-vibration_strength, vibration_strength)
        )


    def update(self, all_food):
        self.sort_nearby(self.nearby_food)
        self.death_check()
        self.cluster()
        self.apply_friction(FRICTION)
        self.update_position()
        self.vibrate()
        self.handle_collisions(self.nearby_food)

        self.boundery_screen()

        self.reproduction_check(all_food)

        self.mass += uniform(-0.03, FOOD_MASS_GAIN)
        