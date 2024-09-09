from .Grid import Grid
import numpy as np
from .Plant import Plant
from .Cluster import Cluster
from .Equations import Equations
from typing import List
import sys
import math
from logging_config import logger

class Simulation:
    def __init__(self, plant_types, grid_size, steps_num, output_file, output_folder, replication_logic, simulation_message):
        self.plant_types = plant_types
        self.grid_size = grid_size
        self.steps_num = steps_num
        self.replication_logic=replication_logic
        self.grid = Grid(shape=self.grid_size, output_file=output_file, output_folder=output_folder)
        self.clusters = []
        self.simulation_message=simulation_message
        logger.info(f"Init simulation with {steps_num} steps")


    def estabilish_cluster_collisions(self):
        '''
        Should return tuples of clusters meeting
        example stav:
        - cluster1 susedi s cl2 a cl3
        - cluster2 susedi s cl3 a cl1
        - cluster3 susedi s cl2 a cl1
        - cluster4 je sam, nesusedi
        vysledok:
        (1,2), (1,3), (2,3),
        (4,)
        :return:
        '''
        clusters_coliding = set()  # Clusters plants are in each others neighborhood
        clusters_nbrs = {cluster: self.grid.get_neighboring_plants_of_cluster(cluster)
                         for cluster in self.clusters}  # Neigboring plants of each cluster
        # Cluster pairs meeting on a grid are indentified
        for cluster1 in self.clusters:
            for cluster2 in self.clusters:
                if cluster2.id <= cluster1.id:
                    # Remove duplicit computation of neighbors
                    # - neighboring clusters 1,2 are the same as 2,1
                    continue
                else:
                    # Check if plants from one cluster are in neighborhood of the second cluster
                    if cluster1.plants.intersection(clusters_nbrs[cluster2]):
                        if cluster1.cluster_type != cluster2.cluster_type:
                            clusters_coliding.add((cluster1, cluster2))
                        else:
                            logger.warn("ERR: clusters of the same type should not occur next to each other")
                    else:
                        # Plants in cluster1 are not in the neighborhood of cluster2
                        continue

        clusters_alone = set(self.clusters) - set([cluster for cluster_tpl in clusters_coliding for cluster in cluster_tpl])
        return clusters_coliding, clusters_alone

    def replicate(self, cluster, num_new_plants):
        """Handles plant replication within a given cluster."""
        example_plant = cluster.get_random_plant()
        for _ in range(num_new_plants):
            available = iter(self.grid.list_free_neighbouring_positions_in_cluster(cluster))
            try:
                position = next(available)
                if position:
                    new_x, new_y = position
                    new_plant = Plant(plant_props=example_plant.get_type_properties())
                    cluster.add_plant(new_plant)
                    self.grid.add_plant(x=new_x, y=new_y, plant=new_plant)
                    # self._find_or_create_cluster(new_x, new_y, new_plant)
            except StopIteration:
                logger.info(f"No next free position. New {_+1}/{num_new_plants} plants for cluster: {cluster.id}")
                break


    def _find_or_create_cluster(self, x, y, plant: Plant):
        'identify cluster - plant rovnakeho typu vedla alebo ak ziadna plant nie je nearby, tak nova cluster instance'

        neighbors = self.grid.list_neighbouring_plants(x, y)
        neighbor_clusters = {plant.in_cluster for plant in neighbors if plant.in_cluster}
        plant_belongs_cluster_type = plant.plant_type

        if neighbor_clusters:
            for n_cluster in neighbor_clusters:
                if n_cluster.cluster_type == plant_belongs_cluster_type:
                    n_cluster.add_plant(plant)
                    logger.info(f"Cluster {n_cluster.id}: assigned new plant (cluster size:{n_cluster.size()})")
                    # main_cluster = n_cluster
                    # neighbor_clusters.remove(n_cluster)
                    break
        if plant.in_cluster is None:
            new_cluster = Cluster(plant)
            self.clusters.append(new_cluster)
            plant.in_cluster = new_cluster
            logger.info(f"Cluster {new_cluster.id}: (new created)")
        # if main_cluster:
        #     for other_cluster in neighbor_clusters:
        #         if other_cluster.cluster_type == plant_belongs_cluster_type:
        #             self.clusters.remove(other_cluster)
        #             main_cluster.merge(other_cluster)
        #     main_cluster.add_plant(plant)
        #     plant.in_cluster = main_cluster
        # else:
        #     new_cluster = Cluster(plant)
        #     self.clusters.append(new_cluster)
        #     plant.in_cluster = new_cluster

    def resolve_competition(self):
        """Handles competition logic between clusters."""
        for cluster in self.clusters:
            for other_cluster in self.clusters:
                if cluster is not other_cluster:
                    if self.are_clusters_adjacent(cluster, other_cluster):
                        # Apply competition logic here, e.g., removing weaker plants
                        self.compete(cluster, other_cluster)

    def are_clusters_adjacent(self, cluster1, cluster2):
        """Check if two clusters are next to each other on the grid.
        Checks all the neighbors of each plant in the cluster"""
        for plant in cluster1.plants:
            x, y = self.grid.get_plant(plant)
            neighbors = self.grid.list_neighbouring_plants(x, y)
            for neighbor in neighbors:
                if neighbor in cluster2.plants:
                    return True
        return False

    def compete(self, cluster1, cluster2):
        """Resolve competition between two adjacent clusters of different species."""
        # Example logic: remove a random plant from the weaker cluster
        if cluster1.get_strength() > cluster2.get_strength():
            self.remove_random_plant(cluster2)
        else:
            self.remove_random_plant(cluster1)

    def remove_random_plant(self, cluster):
        """Removes a random plant from a cluster."""
        if cluster.plants:
            plant_to_remove = cluster.plants.pop()  #TODO implement logic to remove outermost plant
            pos = self.grid.get_plant(plant_to_remove)
            if pos:
                self.grid.remove_plant(*pos)

    def split_cluster(self, cluster: Cluster, relocate_plants: List[Plant], new_cluster: Cluster):
        self.clusters = Cluster(relocate_plants[0])
        Cluster.split_clusters(split_cluster=cluster, relocate_plants=relocate_plants, new_cluster=new_cluster)

    def asses_clusters_reproduction_dying_rate(self, clusters_coliding, clusters_alone):
        cluster_rates_set={}

        for cl1, cl2 in clusters_coliding:
            dcl1, dcl2 = self.replication_logic(cl1, cl2)
            cluster_rates_set.setdefault(cl1, []).append(dcl1)
            cluster_rates_set.setdefault(cl2, []).append(dcl2)

        for cl1 in clusters_alone:
            dcl1, _ = self.replication_logic(cl1, None)
            cluster_rates_set.setdefault(cl1, []).append(dcl1)

        cluster_rate = {}
        for cluster in cluster_rates_set.keys():
            rate_sum = np.mean(cluster_rates_set[cluster])
            cluster_rate[cluster] = rate_sum

        return cluster_rate

    def run(self, seed_plants=None, plants_num=5):
        # Place plants for simulation
        if seed_plants:
            # Init from dictionary of placement and type
            for x,y, plant_type_i in seed_plants:
                plant = Plant(plant_props=self.plant_types[plant_type_i])
                self.grid.add_plant(x, y, plant)
                self._find_or_create_cluster(x, y, plant)
                self.grid.logger_plot()
        else:
            logger.info(f"pre-init: Init {plants_num} plants")
            for _ in range(plants_num):
                while True:
                    x,y = np.random.randint(low=0, high=self.grid_size, size=2, dtype=int)
                    if self.grid.is_empty(x,y):
                        break
                    else:
                        logger.warn(f"pre-init: Position {(x,y)} generated twice")
                z = np.random.randint(low=0, high=len(self.plant_types), dtype=int)
                plant = Plant(plant_props=self.plant_types[z])
                self.grid.add_plant(x, y, plant)
                self._find_or_create_cluster(x, y, plant)
                self.grid.logger_plot()
        logger.info(f"pre-init: resolving clusters after seeding plants")
        self.resolve_merges_and_splits()
        logger.info(f"pre-init:Plants planted!\n\n")

        # Let the simulation run
        for _ in range(self.steps_num):
            logger.info(f"STEP: {_}")
            # self.grid.save_grid(message=f"Step {_}",new_step=True)
            self.grid.plot_grid(step=_, message=f"{self.simulation_message}\n"
                                                f"Start of step {_}.")

            # 1. Starting with grid from previous step - merges and splits of clusters are resolved
            self.grid.logger_plot()

            # 2. Find neighboring clusters and define colisions
            logger.info(f"       *** 2. Find neighboring clusters and define colisions")
            clusters_colisions, clusters_alone = self.estabilish_cluster_collisions()

            # 3. Computing cluster colliding tolls -> reproduction/dying number for each cluster competition
            logger.info(f"       *** 3. Computing cluster colliding tolls -> reproduction/dying numbers")

            clusters_rates = self.asses_clusters_reproduction_dying_rate(clusters_colisions,
                                                                         clusters_alone)


            # 4. apply the rates of growth
            logger.info(f"       *** 4. Apply the rates of growth")
            self.update_clusters(clusters_rates)
            self.grid.save_grid(message="Reproduce or die")


            # 5. resolve merges and splits
            logger.info(f"       *** 5. Resolve merges and splits")
            self.resolve_merges_and_splits()

            # 6. delete empty clusters
            logger.info(f"       *** 6. Delete empty clusters")
            for cluster in self.clusters.copy():
                if cluster.size()==0:
                    logger.info(f"Cluster {cluster.id}: (deleted)")
                    self.clusters.remove(cluster)

            # END OF STEP
            logger.info(f"      Stats at the end of step {_}")
            self.grid.logger_plot()
            logger.info(f"Number of clusters {len(self.clusters)}.")
            for cl in self.clusters:
                logger.info(f" {cl.id} - size {cl.size()} - {cl.get_plant_positions(self.grid)}")


    def update_clusters(self, clusters_rates):
        dying_to_replicating = sorted(clusters_rates.items(), key=lambda item: item[1])

        # First I remove plants that are supposed to die and then I add new ones
        for cls, rate in dying_to_replicating:
            if rate<0:
                rate = math.floor(rate)
                logger.info(f"Cluster {cls.id}: dying by {rate}")
                self.kill_plants(cls, rate)
                ...
            elif rate > 0:
                rate = math.ceil(rate)
                logger.info(f"Cluster {cls.id}: growing by {rate}")
                self.replicate(cls, rate)
            else:
                logger.info(f"Cluster {cls.id}: not reproducing this step")

    def kill_plants(self, cluster, kill_num):
        """
        Plant is killed when no reference points to it. Removing from grid
        and from cluster plant list it belongs currently
        :param cluster: cluster where plant belongs
        :param kill_num: number of plants to remove
        :return:
        """
        for _ in range(abs(kill_num)):
            if cluster.size() != 0:
                plant = cluster.get_random_plant()
                self.grid.remove_plant(**self.grid.get_plant_position(plant))
                cluster.remove_plant(plant)
            else:
                break
        logger.info(f"Cluster {cluster.id}: Killing done! {_+1}/{kill_num}")

    def resolve_merges_and_splits(self):
        # Splitting of clusters
        for cluster in self.clusters:
            connected, out_of_cluster = cluster.check_cluster_connectivity(self.grid)
            if connected:
                continue
            else:
                logger.info(f"Cluster {cluster.id}: fell apart!")
                cluster.remove_plants(out_of_cluster)
                for plant in out_of_cluster:
                    pos = self.grid.get_plant_position(plant)
                    self._find_or_create_cluster(**pos, plant=plant)

        # Merging of clusters
        clusters_to_merge = {}
        clusters_nbrs = {cluster: self.grid.get_neighboring_plants_of_cluster(cluster)
                         for cluster in self.clusters}  # Neigboring plants of each cluster
        for cluster_main in self.clusters:
            for cluster_other in self.clusters:
                if cluster_other.id <= cluster_main.id:
                    continue
                else:
                    if cluster_main.cluster_type == cluster_other.cluster_type:
                        neighbors_main = clusters_nbrs[cluster_main]
                        if neighbors_main.intersection(cluster_other.plants):
                            logger.info(f"Clusters {cluster_main.id}-{cluster_other.id}: neighboring")
                            clusters_to_merge.setdefault(cluster_main, []).append(cluster_other)
                        else:
                            logger.info(f"Clusters {cluster_main.id}-{cluster_other.id}: not neighboring")
                    else:
                        # logger.info(f"Clusters {cluster_main.id}-{cluster_other.id}: different types")
                        ...

        order_of_merging = sorted(clusters_to_merge.items(), key=lambda item: item[0].id, reverse=True)
        for main_cls, other_clss in order_of_merging.copy():
            for o in other_clss:
                main_cls.merge(o)
                logger.info(f"Clusters (main) {main_cls.id} and {o.id}: merged (main has {main_cls.size()} plants)")


    def print_cluster_sizes(self):
        for c in self.clusters:
            print(f"{c.id}: {c.size()}")

    def print_cluster_neighbors(self):
        clusters_nbrs = {cluster: self.grid.get_neighboring_plants_of_cluster(cluster)
                         for cluster in self.clusters}
        for k, v in clusters_nbrs.items():
            print(f"{k.id}: {len(v)} nbrs.  {[p.id for p in v]}")