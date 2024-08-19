import numpy as np
from .Plant import Plant
from typing import Optional

class Grid:
    def __init__(self, shape):
        self.shape = shape
        self.grid = np.full((shape,shape), None)

    def add_plant(self, x, y, plant: Plant):
        self.grid[x,y] = plant

    def get_plant(self, x, y):
        return self.grid[x,y]

    def get_plant_position(self, plant: Plant):
        # TODO: might be good idea to implement the plant search better
        for i in range(self.shape):
            for j in range(self.shape):
                if self.grid[i,j] == plant:
                    return {"x" : i, "y" : j}
        raise Exception("Plant not on a grid!")

    def position_free(self, x, y):
        return True if not self.grid[x,y] else False

    def list_neighbouring_plants(self,x,y):
        # Neighbors are only vertically and horizontally (not diagonal directions)
        nbrs = set()
        for m1,m2 in [(-1,0),(0,+1),(0,-1),(+1,0)]:
            nx,ny = x+m1,y+m2
            if nx < 0 or ny <0 or nx >= self.shape or ny >= self.shape:
                continue
            else:
                if self.grid[nx, ny]:
                    nbrs.add(self.grid[nx, ny])
        return nbrs

    def plot(self):
        for i in range(self.shape):
            print("+---" * self.shape + "+")
            for j in range(self.shape):
                pos = self.grid[i,j]
                print(f"| {pos.image_representation if isinstance(pos, Plant) else ' '} ", end="")
            print("|")
        print("+---" * self.shape + "+")
