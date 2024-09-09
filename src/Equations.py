from .Cluster import Cluster
from typing import Optional
from logging_config import logger


class Equations:
    @staticmethod
    def competition_2population(cls1: Cluster, cls2: Optional[Cluster]):
        """
        x, y - population sizes
        r, s - reproduction rate: Plant.replication_frequency
        a, b - extent of competition: Plant.aggressivity
        :param cls1: diff for population in cluster 1
        :param cls2: diff for population in cluster 2
        :return:
        """
        x, r, a, _ = cls1.cluster_properties().values()
        y, s, b, _ = cls2.cluster_properties().values() if cls2 else (0, None, None, None)

        d_cls1 = ((r * x - r * a * y) * x)
        d_cls2 = ((s * y - r * b * x) * y) if cls2 else 0

        # The d values are differentials, number of individuals that should grow or die
        logger.info(f"Competition ({cls1.id},{cls2.id if cls2 else ''}) with population size (x={x},y={y}) results in (dx={d_cls1},dy={d_cls2}). (new_x={d_cls1 + x},new_y={ d_cls2 + y if d_cls2 is not None else y})")
        return d_cls1, d_cls2

    @staticmethod
    def competition_2population_max_size(cls1: Cluster, cls2: Optional[Cluster]):
        """
        x, y - population sizes
        r, s - reproduction rate: Plant.replication_frequency
        a, b - extent of competition: Plant.aggressivity
        :param cls1: diff for population in cluster 1
        :param cls2: diff for population in cluster 2
        :return:
        """
        x, r, a, K = cls1.cluster_properties().values()
        y, s, b, L = cls2.cluster_properties().values() if cls2 else (0, None, None, None)

        d_cls1 = r * (1 - ((x+a*y)/K)) * x
        d_cls2 = s * (1 - ((y+b*x)/L)) * y if cls2 else 0

        # The d values are differentials, number of individuals that should grow or die
        logger.info(
            f"Competition ({cls1.id},{cls2.id if cls2 else ''}) with population size (x={x},y={y}) results in (dx={d_cls1},dy={d_cls2}). (new_x={d_cls1 + x},new_y={d_cls2 + y if d_cls2 is not None else y})")
        return d_cls1, d_cls2
