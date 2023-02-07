from math import floor


def get_key(i1, i2):
    return f'{i1}.{i2}'


def sat(x):
    return min(max(x, 0), 1)


class SpatialHashGrid:

    def __init__(self, bounds, cell_dimensions):
        self.bounds = bounds
        self.cell_dimensions = cell_dimensions
        self.cells = {}
        self.init_cells()

        width = self.bounds[0][1] - self.bounds[0][0]
        height = self.bounds[1][1] - self.bounds[1][0]
        self.max_x = int(width / self.cell_dimensions[0])-1
        self.max_y = int(height/self.cell_dimensions[1])-1

    def init_cells(self):
        width = self.bounds[0][1] - self.bounds[0][0]
        height = self.bounds[1][1] - self.bounds[1][0]
        for y in range(int(height/self.cell_dimensions[1])):
            for x in range(int(width / self.cell_dimensions[0])):
                self.cells[get_key(x, y)] = set()

    def update_particles(self, particles):
        for index in self.cells:
            self.cells[index].clear()
        for particle in particles:
            self.add_particle(particle)

    def add_particle(self, particle):
        x, y = self.get_cell_index([particle.position.x, particle.position.y])

        k = get_key(x, y)
        if k in self.cells:
            self.cells[k].add(particle)

    def get_cell_index(self, position):
        x = floor((position[0] - self.bounds[0][0]) / self.cell_dimensions[0])
        y = floor((position[1] - self.bounds[1][0]) / self.cell_dimensions[1])

        return x, y

    def find_near(self, particle , VISUAL_RANGE):
        nearby = set()
        min_x = particle.position.x - VISUAL_RANGE
        max_x = particle.position.x + VISUAL_RANGE
        min_y = particle.position.y - VISUAL_RANGE
        max_y = particle.position.y + VISUAL_RANGE
    
        initial_x, initial_y = self.get_cell_index([min_x, min_y])
        final_x, final_y = self.get_cell_index([max_x, max_y])
        for x in range(initial_x, final_x+1):
            for y in range(initial_y, final_y+1):
                if x < 0:
                    x += (self.max_x + 1)
                elif x > self.max_x:
                    x -= (self.max_x + 1)
                if y < 0:
                    y += (self.max_y + 1)
                elif y > self.max_y:
                    y -= (self.max_y + 1)

                k = get_key(x, y)

                try:
                    nearby.update(self.cells[k])
                except KeyError:
                    print("I failed")
        
        return nearby
                
        

    def get_cell_coordinates(self, i, j):
        return [self.bounds[0][0] + (self.cell_dimensions[0] * i),
                self.bounds[1][0] + (self.cell_dimensions[1] * j),
                self.cell_dimensions[0],
                self.cell_dimensions[1]]


def create_grid(x, y, width, height, dimensions_x, dimensions_y):
    CELL_DIMENSIONS = [width / dimensions_x, height / dimensions_y]
    grid = SpatialHashGrid([[x, width], [y, height]], CELL_DIMENSIONS)

    return grid