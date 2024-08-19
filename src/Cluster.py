import itertools
from typing import List
from . import Plant

class Cluster:
    id_generator = itertools.count()
    def __init__(self, plant: Plant):
        self.plants = set({plant})   #I need to represent the plants by graph to check connectivity
        self.id = next(Cluster.id_generator)
        self.cluster_type = plant.plant_type

    def has_plant(self, plant: Plant):
        if plant in self.plants:
            return True
        else:
            return False

    def add_plant(self,plant: Plant):
        self.plants.add(plant)

    def merge(self, other_cluster):
        'All the plants in the cluster need to have their cluster ids overwritten'
        # TODO: put plants from other to main
        # TODO: change references in all of the plants from other cluster to main cluster
        for plant in other_cluster.plants:
            plant.in_cluster = self
            self.plants.add(plant)

    @staticmethod
    def split_clusters(cls, cluster_to_split, splitting_plant):
        'From one neighboring cluster create 2 clusters upon the plant that splits them'


    def check_cluster_connectivity(self, grid):
        'Each plant has to have at least one other plant in the neighborhood\
        If it does not: then the plant that does not have the other in neighborhood splits \
        the cluster into 2+ subclusters'
        """Check if the cluster is still connected using BFS/DFS."""
        if not self.plants:
            return False

        start_plant = next(iter(self.plants))
        visited = set()
        stack = [start_plant]

        while stack:
            plant = stack.pop()
            if plant in visited:
                continue
            visited.add(plant)
            for neighbor in grid.list_neighbouring_plants(**grid.get_plant_position(plant)):
                if neighbor in self.plants:
                    stack.append(neighbor)

        return visited == self.plants  # True if all plants were visited
