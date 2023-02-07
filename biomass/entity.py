from pygame import Vector2
from math import sqrt
from numpy.random import randint, uniform

class Entity:
    def __init__(self, screenAssist, position : Vector2, velocity : Vector2, mass, max_speed) -> None:
        self.position = position
        self.velocity = velocity
        self.mass = mass
        self.max_speed = max_speed
        self.screenAssist = screenAssist

    @classmethod
    def generate_random(cls, screenAssist):
        position = screenAssist.randPosition()
        velocity = screenAssist.randVelocity(-1, 1)
        return Entity(screenAssist, position, velocity, randint(5, 20), uniform(1, 4))
    

    # physics related functions
    def handle_collisions(self, entities):
        # Iterate over nearby objects
        for other_obj in entities:
            # Skip self
            if other_obj is self:
                continue
            
            # Calculate collision axis and distance between objects
            collision_vector = self.position - other_obj.position
            distance = collision_vector.length()

            if distance >= self.mass + other_obj.mass or distance == 0:
                continue

            normal_vector = collision_vector / distance
            overlap = (self.mass + other_obj.mass) - distance

            # Calculate the mass ratio between the two objects
            mass_ratio = self.mass / other_obj.mass
            self_movement = normal_vector * overlap * mass_ratio / (mass_ratio + 1)
            other_movement = normal_vector * overlap * 1 / (mass_ratio + 1)
            
            # Move both objects away from each other based on their mass
            self.position += self_movement
            other_obj.position -= other_movement
    

    def boundery_screen(self):
        border = self.screenAssist.border
        if self.position.x < border.x:
            self.position.x = border.x + border.w
        
        elif self.position.x > border.x + border.w:
            self.position.x = border.x
        
        if self.position.y < border.y:
            self.position.y = border.y + border.h
        
        elif self.position.y > border.y + border.h:
            self.position.y = border.y


    # other
    def update_position(self):
        self.position += self.velocity
    
    def apply_friction(self, friction):
        self.velocity /= friction


    def speed_limit(self):
        speed = sqrt(self.velocity.x * self.velocity.x + self.velocity.y * self.velocity.y)

        if speed > self.max_speed:
            self.velocity.x = (self.velocity.x / speed) * self.max_speed
            self.velocity.y = (self.velocity.y / speed) * self.max_speed
    

    def sort_nearby(self, array):
        return [
            cell for cell in array 
            if cell != self and self.screenAssist.toroidal_distance(self.position, cell.position) < self.visual_range
        ]

    def get_closest(self, current_entity, array_of_entities):
        entities = [entity for entity in array_of_entities if entity is not current_entity]
        return min(entities, key=lambda other_entity: self.screenAssist.toroidal_distance(self.position, other_entity.position), default=None)

    