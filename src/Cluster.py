import itertools
from typing import List
from . import Plant
import sys
import math
import numpy as np
from logging_config import logger

class Cluster:
    id_generator = itertools.count()
    def __init__(self, plant: Plant):
        self.plants = set({plant})   #I need to represent the plants by graph to check connectivity
        self.id = next(Cluster.id_generator)
        self.cluster_type = plant.plant_type

    def get_random_plant(self):
        rnd = np.random.randint(low=0,high=len(self.plants))

        return list(self.plants)[rnd]

    def remove_plant(self, plant):
        plant.in_cluster=None
        self.plants.remove(plant)

    def remove_plants(self, plants_list):
        for plant in plants_list:
            self.remove_plant(plant)

    def cluster_properties(self):
        example_plant = self.get_random_plant()
        props = example_plant.get_type_properties()
        return {
                "population_size": len(self.plants),
                "replication_rate": props["replication_frequency"],
                "aggressivity": props["aggressivity"],
                "max_population": props["max_population"]
        }

    def has_plant(self, plant: Plant):
        if plant in self.plants:
            return True
        else:
            return False

    def size(self):
        return len(self.plants)

    def add_plant(self,plant: Plant):
        """
        Plant added into cluster and plant knows about it.
        :param plant:
        :return:
        """
        plant.in_cluster = self
        self.plants.add(plant)

    def merge(self, other_cluster):
        'All the plants in the cluster need to have their cluster ids overwritten'
        for plant in other_cluster.plants.copy():
            other_cluster.remove_plant(plant)
            self.add_plant(plant)

    @staticmethod
    def split_clusters(split_cluster, relocate_plants, new_cluster):
        'From one neighboring cluster create 2 clusters upon the plant that splits them'
        plants_iter = iter(relocate_plants)

        while True:
            plant = next(plants_iter)
            if plant:
                split_cluster.plants.remove(plant)
                plant.in_cluster = new_cluster
            else:
                break

    def check_cluster_connectivity(self, grid):
        'Each plant has to have at least one other plant in the neighborhood\
        If it does not: then the plant that does not have the other in neighborhood splits \
        the cluster into 2+ subclusters'
        """Check if the cluster is still connected using BFS/DFS."""
        if not self.plants or len(self.plants)==1:
            logger.info(f"Number of all plants in cluster is {len(self.plants)}: connected")
            return True, None

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

        unvisited = set(self.plants) - visited
        logger.info(f"Number of all plants in cluster is {len(self.plants)}: "
              f"visited {len(visited)}, unvisited {len(unvisited)}")
        return visited == self.plants, unvisited  # True if all plants were visited

    def resolve_cluster_competition(self, competing_cluster=None):
        local_plant = list(self.plants)[0]
        local_num_plants = len(self.plants)
        if competing_cluster:
            # 2 populations fighting
            comp_plant = list(competing_cluster.plants)[0]
            comp_num_plants = len(competing_cluster.plants)

        else:
            # 1 population is reproducing
            f = math.ceil(local_num_plants / local_plant.replication_frequency)
            replicate = math.ceil(math.log2(f + 0.1 if f == 1 else f))
            return replicate


    def compute_plants_to_grow(self):
        # TODO: remplace with resolve cluste competition
        example_plant = list(self.plants)[0]
        num_plants = len(self.plants)
        f = math.ceil(num_plants / example_plant.replication_frequency)
        replicate = math.ceil(math.log2(f+0.1 if f==1 else f))
        return replicate

    def get_plant_positions(self, grid):
        return [grid.get_plant_position(p) for p in self.plants]