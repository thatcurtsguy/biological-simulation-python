import pygame as pg
from dataclasses import dataclass
from pygame import Rect

from spatial_hash_grid import create_grid
from utility_functions import ScreenAssist

from numpy.random import randint

# biomass
from biomass.cell import Cell
from biomass.food import Food

@dataclass
class RenderingSettings:
    SCREEN_X     : int
    SCREEN_Y     : int
    SCREEN_WIDTH : int
    SCREEN_HEIGHT: int
    FRAME_RATE   : int
    SCREEN_COLOR : tuple


@dataclass
class PhysicsSettings:
    INIT_CELL_COUNT : int 
    INIT_FOOD_COUNT : int

    CELL_VISUAL_RADIUS : int
    FOOD_VISUAL_RADIUS : int

    MAX_CELLS: int
    MAX_FOOD : int


@dataclass
class RuntimeVariables:
    total_frames    : int = 0
    relative_frames : int = 0  
    extinctions     : int = 0

    mouse_pressed : bool = False
    paused        : bool = False


class Simulation(RenderingSettings, PhysicsSettings, RuntimeVariables):
    # - - - - - - - - - - - - - - - - - - initilisation - - - - - - - - - - - - - - - - - - #
    def __init__(self, rs : RenderingSettings, ps : PhysicsSettings) -> None:
        RenderingSettings.__init__(self, rs.SCREEN_X, rs.SCREEN_Y, rs.SCREEN_WIDTH, rs.SCREEN_HEIGHT, rs.FRAME_RATE, rs.SCREEN_COLOR)
        PhysicsSettings.__init__(self, ps.INIT_CELL_COUNT, ps.INIT_FOOD_COUNT, ps.CELL_VISUAL_RADIUS, ps.FOOD_VISUAL_RADIUS, ps.MAX_CELLS, ps.MAX_FOOD)


        self._init_screen()
        self._init_hash_grids()
        self._init_cells()
        self._init_food()

    def _init_screen(self):
        self.screen = pg.display.set_mode((self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
        self.screenAssist = ScreenAssist(self.screen, Rect(self.SCREEN_X, self.SCREEN_Y, self.SCREEN_WIDTH, self.SCREEN_HEIGHT))
        self.clock  = pg.time.Clock()
        self.running = True
    
    def _init_hash_grids(self):
        dimensions_x, dimensions_y = 8, 6
        self.hash_grid_cells = create_grid(-20, -20, self.SCREEN_WIDTH + 40, self.SCREEN_HEIGHT + 40, dimensions_x, dimensions_y)
        self.hash_grid_food  = create_grid(-20, -20, self.SCREEN_WIDTH + 40, self.SCREEN_HEIGHT + 40, dimensions_x, dimensions_y)
    
    def _init_cells(self):
        self.all_cells = [Cell.generate_random(self.screenAssist) for _ in range(self.INIT_CELL_COUNT)]

    def _init_food(self):
        self.all_food = [Food.generate_random(self.screenAssist) for _ in range(self.INIT_FOOD_COUNT)]
    

    # - - - - - - - - - - - - - - - - - - physics - - - - - - - - - - - - - - - - - - #
    def update_cells(self):
        for cell in self.all_cells:
            cell.nearby_life = self.hash_grid_cells.find_near(cell, cell.visual_range)
            cell.nearby_food = self.hash_grid_food.find_near(cell, cell.visual_range)

            cell.update()

            if cell.death_check() == True:
                self.all_cells.remove(cell)
            
            if cell.reproduce_check() == True:
                self.all_cells.append(cell.reproduce())


    def update_food(self):
        for food in self.all_food:
            food.nearby_food = self.hash_grid_food.find_near(food, self.FOOD_VISUAL_RADIUS)
            food.update(self.all_food)

            if food.death_check() == True:
                self.all_food.remove(food)
    

    # - - - - - - - - - - - - - - - - - - rendering - - - - - - - - - - - - - - - - - - #
    def render_entities(self):
        for food in self.all_food: 
            food.draw(self.screen)
        
        for cell in self.all_cells: 
            cell.draw(self.screen)

    
    # - - - - - - - - - - - - - - - - - - pygame - - - - - - - - - - - - - - - - - - #
    def update_caption(self):
        pg.display.set_caption(f"""
            FPS: {round(self.clock.get_fps())}/{self.FRAME_RATE}
            CELLS: {len(self.all_cells)}
            FOOD: {len(self.all_food)}
            TIME PASSED: {round(self.total_frames/60, 2)} mins
            EXTINCTIONS: {self.extinctions}
        """)

    def poll_events(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                quit()
            
            elif event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    pg.quit()
                    quit()
                
                elif event.key == pg.K_SPACE:
                    self.paused = not self.paused
            
            
            elif event.type == pg.MOUSEBUTTONDOWN:
                self.mouse_pressed = True
            
            elif event.type == pg.MOUSEBUTTONUP:
                self.mouse_pressed = False
        
    
    # - - - - - - - - - - - - - - - - - - other - - - - - - - - - - - - - - - - - - #
    def extinction_check(self):
        if len(self.all_cells) != 0 or self.INIT_CELL_COUNT == 0: return

        self.all_food = []
        self._init_cells()
        self._init_food()
        self.extinctions += 1
        self.relative_frames = 0


    def overflow_prevention(self):
        while len(self.all_food) > self.MAX_FOOD:
            self.all_food.pop(randint(0, len(self.all_food)-1))
        
        while len(self.all_cells) > self.MAX_CELLS:
            self.all_food.pop(randint(0, len(self.all_food)-1))
    

    def process_mouse(self):
        if self.mouse_pressed == False: return

        mouse_position = pg.mouse.get_pos()

        size = 20
        border = Rect(mouse_position[0] - size, mouse_position[1] - size, size, size)

        for _ in range(5):
            position = self.screenAssist.randPosition(border)
            velocity = self.screenAssist.randVelocity(-2, 2)
            self.all_food.append(Food(self.screenAssist, position, velocity))


    # - - - - - - - - - - - - - - - - - - gameloop - - - - - - - - - - - - - - - - - - #
    def prep_frame(self):
        self.poll_events()
        self.clock.tick(self.FRAME_RATE)
        self.screen.fill(self.SCREEN_COLOR)
        self.hash_grid_cells.update_particles(self.all_cells)
        self.hash_grid_food.update_particles(self.all_food)
        self.process_mouse()
    

    def update_frame(self):
        self.update_food()
        self.update_cells()

        self.extinction_check()
        self.overflow_prevention()


    def render_frame(self):
        self.render_entities()
    

    def end_frame(self):
        # ending the frame
        self.update_caption()
        #self.screenAssist.apply_translation()
        pg.display.flip()

        self.total_frames += 1
        self.relative_frames += 1

    def run(self, runtime=100**10):
        while self.total_frames < runtime or self.running == False:
            self.prep_frame()
            self.update_frame()
            self.render_frame()
            self.end_frame()

    
