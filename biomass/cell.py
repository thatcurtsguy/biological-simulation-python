import pygame as pg

from numpy.random import uniform, choice

from settings import *
from Genes.gene_manager import Genes
from biomass.food import Food
from biomass.entity import Entity
from pygame import Vector2



class Cell(Entity):
    def __init__(self, screenAssist, position : Vector2, velocity : Vector2, genes : Genes, energy=50) -> None:
        self.genes = genes

        self.lifespan = CELL_LIFETIME
        self.visual_range = CELL_VISUAL_RANGE
        self.time_alive = 0
        self.color = self.genes.color_genes

        super().__init__(
            screenAssist,
            position=position,
            velocity=velocity,
            mass = self.genes.query("trait", "mass") * 9.5,
            max_speed=self.genes.query("trait", "speed") * 2,
        )

        self.energy = energy

        self.nearby_life = []
        self.nearby_food = []

        self.closest_food : Food = None 
        self.closest_life : Cell = None 

        self.dead = False  

    @classmethod
    def generate_random(cls, screenAssist):
        entity = super().generate_random(screenAssist)  
        return Cell(screenAssist, entity.position, entity.velocity, Genes())


    def get_closest_entities(self):
        self.closest_food = self.get_closest(self, self.nearby_food)
        self.closest_life = self.get_closest(self, self.nearby_life)

    

    def food_eat_check(self):
        if self.closest_food == None:
            return
        
        distance = self.screenAssist.toroidal_distance(self.position, self.closest_food.position)

        if distance <= self.mass + self.closest_food.mass+1 and self.mass >= self.closest_food.mass:
            self.energy += 1
            self.closest_food.mass -= 1


    def draw(self, screen):
        pg.draw.circle(screen, self.color, self.position, self.mass)
    

    def reproduce(self):
        size = self.mass
        new_position = self.position + Vector2(choice([-size*3, size*3]), choice([-size*3, size*3]))
        new_velocity = Vector2(uniform(-1, 1), uniform(-1, 1))

        self.energy /= 2

        return Cell(self.screenAssist, new_position, new_velocity, self.genes.mutate(), self.energy)
   
    def death_check(self):
        return self.dead
    

    def reproduce_check(self):
        if self.energy >= REPRODUCTION_CAP:
            return True
        return False
            

    def old_age_death_check(self):
        if self.time_alive > self.lifespan:
            self.dead = True
    

    def mean_average_position(self, forces):
        """Return the mean average position of a list of pg.Vector2 objects."""
        return sum(forces) / len(forces)
    
    def interact(self):
        # Check if closest entity is life or food
        closest_life = self.closest_life
        closest_food = self.closest_food

        # Get the number of nearby entities of each type
        nearby_life_count = len(self.nearby_life)
        nearby_food_count = len(self.nearby_food)

        # Check if there is a high density of entities of each type
        cell_high_density = self.is_high_density(nearby_life_count)
        food_high_density = self.is_high_density(nearby_food_count)

        # Interact with closest life entity, if it exists
        if closest_life:
            # Check if the closest life entity is larger or smaller than self
            cell_larger = self.is_larger(self.mass, closest_life.mass)

            # Check if the closest life entity is close or far from self
            cell_close = self.is_close(self.position, closest_life.position)

            # Check if the closest life entity is a friend or a foe
            cell_friend = self.is_freind(closest_life.genes)

            force = self.genes.calc_force(cell_close, cell_larger, cell_friend, cell_high_density)

            # Update the velocity based on the mean average of all of the above values
            self.velocity += self.screenAssist.toroidal_direction(self.position, closest_life.position) * force


        if closest_food:
             # Check if the closest life entity is larger or smaller than self
            #food_larger = self.is_larger(self.mass, closest_food.mass)

            # Check if the closest life entity is close or far from self
            #food_close = self.is_close(self.position, closest_food.position)

            #velocities = []

            self.velocity += self.screenAssist.toroidal_direction(self.position, closest_food.position) * self.genes.query("active", "food_near").value

    def is_freind(self, other_gene):
        color1 = self.genes.color_genes
        color2 = other_gene.color_genes

        delta = (color1[0] - color2[0]) + (color1[1] - color2[1]) + (color1[1] - color2[1])

        return delta > 20
    

    def is_high_density(self, nearby : int):
        return nearby > 4
   
    def is_close(self, position1 : Vector2,  position2 : Vector2):
        return 3 < self.screenAssist.toroidal_distance(position1, position2) < CELL_VISUAL_RANGE/2

    def is_larger(self, size1, size2):
        return size1 > size2


    def update(self):
        self.nearby_life = self.sort_nearby(self.nearby_life)
        self.nearby_food = self.sort_nearby(self.nearby_food)

        self.get_closest_entities()
        self.interact()
        self.food_eat_check()

        self.handle_collisions(self.nearby_food) # TODO: try out only handeling collision with the closest cell
        self.handle_collisions(self.nearby_life)

        self.speed_limit()
        self.update_position()
        self.boundery_screen()

        self.old_age_death_check()

        if self.velocity.length() < 0.05:
            self.time_alive += 40
            
        self.time_alive += (self.mass * (self.velocity.length()) )
    