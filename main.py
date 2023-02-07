import pygame as pg
import random
import cProfile

from simulation import Simulation, RenderingSettings, PhysicsSettings

seed = random.randint(0, 100000000000)
random.seed(seed)
print(f"""

~ ~ Running Simulation ~ ~
seed: {seed}

""")

pg.init()


def main():
    render_settings = RenderingSettings(
        SCREEN_X=0,
        SCREEN_Y=0,
        SCREEN_WIDTH=1500,
        SCREEN_HEIGHT=800,
        FRAME_RATE=144,
        SCREEN_COLOR=(20, 24, 45),
    )

    physics_settings = PhysicsSettings(
        INIT_CELL_COUNT=100,
        INIT_FOOD_COUNT=100,
        CELL_VISUAL_RADIUS=30,
        FOOD_VISUAL_RADIUS=90,
        MAX_CELLS=300,
        MAX_FOOD=200,
    )

    simulation = Simulation(render_settings, physics_settings)

    simulation.run(1000)

cProfile.run("main()", sort="tottime")