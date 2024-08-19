import itertools
from . import Cluster


class Plant:
    id_iter = itertools.count()

    def __init__(self, plant_props, in_cluster=None):
        self.id = next(Plant.id_iter)
        self._set_properties(**plant_props)
        self.in_cluster = in_cluster
        # properties of plant, should be specific for the type of plant

    def _set_properties(self, plant_type, replication_strength, image_representation):
        self.plant_type = plant_type
        self.replication_strength = replication_strength
        self.image_representation = image_representation