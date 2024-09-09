import itertools
from . import Cluster
from logging_config import logger

class Plant:
    id_iter = itertools.count()

    def __init__(self,plant_props, in_cluster=None):
        # self.x = x
        # self.y = y
        self.id = next(Plant.id_iter)
        self._set_properties(**plant_props)
        self.in_cluster = in_cluster
        # properties of plant, should be specific for the type of plant

    def get_type_properties(self):
        return {
            "plant_type": self.plant_type,
            "replication_frequency": self.replication_frequency,
            "aggressivity": self.aggressivity,
            "image_representation": self.image_representation,
            "color": self.color,
            "max_population": self.max_population
        }

    def _set_properties(self, plant_type, replication_frequency, aggressivity, image_representation, color, max_population):
        self.plant_type = plant_type # How is plant species called
        self.replication_frequency = replication_frequency # How often plant replicates
        self.aggressivity = aggressivity
        self.image_representation = image_representation # How is plant visualized on a grid
        self.color = color
        self.max_population = max_population

    @staticmethod
    def breed_plant(cls, breeding_plant, simulation_step):
        if breeding_plant.replication_frequency %simulation_step ==0:
            return Plant(breeding_plant.get_type_properties(), in_cluster=breeding_plant.in_cluster)
