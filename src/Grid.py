import numpy as np
from .Plant import Plant
from typing import Optional
from logging_config import logger
import copy
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import os

class Grid:
    def __init__(self, shape, output_file, output_folder):
        self.shape = shape
        self.grid = np.full((shape,shape), None)
        self.hashing_plants = dict()
        self.output_file=output_file
        self.output_folder=output_folder

    def add_plant(self, x, y, plant: Plant):
        self.grid[x,y] = plant
        self.hashing_plants[plant] = (x,y)

    def get_grid_copy(self):
        return copy.deepcopy(self)

    def get_plant(self, x, y):
        return self.grid[x,y]

    def remove_plant(self, x, y):
        self.hashing_plants.pop(self.grid[x,y])
        self.grid[x,y] = None

    def get_plant_position(self, plant: Plant):
        # TODO: might be good idea to implement the plant search better
        if plant in self.hashing_plants.keys():
            p = self.hashing_plants[plant]
            return {"x": p[0], "y": p[1]}
        else:
            for i in range(self.shape):
                for j in range(self.shape):
                    if self.grid[i,j] == plant:
                        self.hashing_plants[plant] = (i,j)
                        return {"x" : i, "y" : j}
        raise Exception("Plant not on a grid!")

    def is_empty(self, x, y):
        return True if not self.grid[x,y] else False

    def list_neighbouring_plants(self,x: int,y: int):
        """
        Return neighboring plants of given position. Neigbors are only vertically
        or horizontally placed
        :param x:
        :param y:
        :return:
        """
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

    def list_free_neighbouring_positions(self,x,y):
        # Neighbors are only vertically and horizontally (not diagonal directions)
        nbrs = set()
        for m1,m2 in [(-1,0),(0,+1),(0,-1),(+1,0)]:
            nx,ny = x+m1,y+m2
            if nx < 0 or ny <0 or nx >= self.shape or ny >= self.shape:
                continue
            else:
                if not self.grid[nx, ny]:
                    nbrs.add((nx, ny))
        return nbrs

    def plot(self):
        for i in range(self.shape):
            print("+---" * self.shape + "+")
            for j in range(self.shape):
                pos = self.grid[i,j]
                print(f"| {pos.image_representation if isinstance(pos, Plant) else ' '} ", end="")
            print("|")
        print("+---" * self.shape + "+")

    def logger_plot(self):
        # Initialize a list to collect log messages
        log_messages = []

        # Generate the grid top border
        border = "+---" * self.shape + "+"
        log_messages.append(border)

        # Generate the grid rows
        for i in range(self.shape):
            row = ""
            for j in range(self.shape):
                pos = self.grid[i, j]
                # Append the cell representation to the row
                cell_representation = pos.image_representation if isinstance(pos, Plant) else ' '
                row += f"| {cell_representation} "
            # Append the right border of the row
            row += "|"
            log_messages.append(row)

        # Append the bottom border
        log_messages.append(border)

        # Log all messages at once
        for message in log_messages:
            logger.info(message)

    def get_neighboring_plants_of_cluster(self, cluster):
        """
        Should return all neighboring plants of a given cluster.
        :param cluster:
        :return:
        """
        cluster_neighbors_total = set().union(*(self.list_neighbouring_plants(**self.get_plant_position(plant))
                for plant in cluster.plants if self.list_neighbouring_plants(**self.get_plant_position(plant))) or set())
        # TODO - cluster_neighbors contains also plants of its own. Every neighbor of a plant
        # I want only neighboring plants outside the cluster
        cluster_outside_neighbors = cluster_neighbors_total - cluster.plants

        return cluster_outside_neighbors

    def list_free_neighbouring_positions_in_cluster(self, cluster):

        free_nbrs= set().union(*(self.list_free_neighbouring_positions(**self.get_plant_position(plant))
                               for plant in cluster.plants) or set())

        return free_nbrs

    def save_grid(self, message, new_step=False):
        with open(self.output_file,"a") as output:
            if new_step:
                output.write(f"\n\n")
            output.write(f"> {message}\n")
            for i in range(self.shape):
                output.write("+---" * self.shape + "+\n")
                for j in range(self.shape):
                    pos = self.grid[i, j]
                    output.write(f"| {pos.image_representation if isinstance(pos, Plant) else ' '} ")
                output.write("|\n")
            output.write("+---" * self.shape + "+\n")



    def plot_grid(self, step, message):
        plt.ion()
        # Create the colored grid
        fig, ax = plt.subplots()

        ax.set_aspect('equal')
        plants_leg = set()
        plants_props = []

        # Annotate the grid with characters
        for i in range(self.shape):
            for j in range(self.shape):
                plant = self.grid[i, j]

                if plant:
                    if plant.plant_type in plants_leg:
                        pass
                    else:
                        plants_leg.add(plant.plant_type)
                        plants_props.append(plant.get_type_properties())

                # Set the background color based on the character
                color = plant.color if plant else "black"

                # Create a rectangle for the background color
                ax.add_patch(Rectangle((j, i), 1, 1, color=color))

                # Add the character text in the center of the cell
                ax.text(j + 0.5, i + 0.5, plant.image_representation if plant else " ", ha='center', va='center', color='black', fontsize=12)



        ax.set_xlim(0, self.shape)
        ax.set_ylim(0, self.shape)
        plt.xticks([])
        plt.yticks([])
        plt.suptitle(message)
        plt.gca().invert_yaxis()  # Invert y-axis to match matrix orientation

        x_offset = self.shape + 0.5
        y_spacing = 8

        for i, plant in enumerate(plants_props):
            y_offset = self.shape - i * y_spacing  # Adjust spacing between plant entries

            # Add a colored rectangle corresponding to the plant's color
            ax.add_patch(Rectangle((x_offset, y_offset - 0.5), 1, 1, color=plant['color']))

            # Add text with the plant's name, aggressivity, and reproduction rate
            ax.text(x_offset + 1.2, y_offset, f"{plant['plant_type']}", fontweight='bold', va='center', fontsize=10, color=plant['color'])
            ax.text(x_offset + 1.2 + 2, y_offset + 3, f"Aggressivity: {plant['aggressivity']}, \n"
                                                        f"Replication: {plant['replication_frequency']}, \n"
                                                        f"Max population: {plant['max_population']}",
                    va='center', fontsize=9)

        plt.tight_layout()
        plt.savefig(os.path.join(self.output_folder,f'step_{step}.png'))
        plt.show()
        plt.close()