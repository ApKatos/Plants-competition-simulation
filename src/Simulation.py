from . import Grid
import numpy as np
from . import Plant
from . import Cluster


class Simulation:
    def __init__(self, plant_types, grid_size, steps_num):
        self.plant_types = plant_types
        self.grid_size = grid_size
        self.steps_num = steps_num
        self.grid = Grid.Grid(shape=self.grid_size)
        self.clusters = []

    def _find_or_create_cluster(self, x, y, plant: Plant):
        'identify cluster - plant rovnakeho typu vedla alebo ak ziadna plant nie je nearby, tak nova cluster instance'

        neighbors = self.grid.list_neighbouring_plants(x, y)
        neighbor_clusters = {plant.in_cluster for plant in neighbors if plant.in_cluster}
        plant_belongs_cluster_type = plant.plant_type
        main_cluster=None

        if neighbor_clusters:
            # TODO: here I have to resolve merging of clusters if the newly added plant joins 2 clusters of the same type
            for n_cluster in neighbor_clusters:
                if n_cluster.cluster_type == plant_belongs_cluster_type:
                    main_cluster = n_cluster
                    neighbor_clusters.remove(n_cluster)
                    break
        if main_cluster:
            for other_cluster in neighbor_clusters:
                if other_cluster.cluster_type == plant_belongs_cluster_type:
                    self.clusters.remove(other_cluster)
                    main_cluster.merge(other_cluster)
            main_cluster.add_plant(plant)
            plant.in_cluster = main_cluster
        else:
            new_cluster = Cluster.Cluster(plant)
            self.clusters.append(new_cluster)
            plant.in_cluster = new_cluster

    def run(self, seed_plants=None, plants_num=5):


        # Place plants for simulation
        if seed_plants:
            # Init from dictionary of placement and type
            ...
        else:
            for _ in range(plants_num):
                while True:
                    x,y = np.random.randint(low=0, high=self.grid_size, size=2, dtype=int)
                    if self.grid.position_free(x,y):
                        break
                    else:
                        print(f"Position {(x,y)} generated twice")
                z = np.random.randint(low=0, high=len(self.plant_types), dtype=int)
                plant = Plant.Plant(plant_props=self.plant_types[z])
                self.grid.add_plant(x, y, plant)
                self._find_or_create_cluster(x, y, plant)

        # Let the simulation run
        for _ in range(self.steps_num):
            self.grid.plot()

        self.clusters[0].check_cluster_connectivity(self.grid)
