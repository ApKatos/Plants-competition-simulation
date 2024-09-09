from src import Simulation, Equations
from logging_config import logger
import os
import random

def main():
    # Run 4 simulation cases - all are based on maximal population sizes
    K, L = 50, 100
    grid_size = 10
    num_steps = 25
    init_plants=6
    for i in range(1,5):
        os.makedirs(f".\SimulationPlots_case{i}", exist_ok=True)

    seed_plants=[]
    for _ in range(init_plants):
        x,y = random.randint(0,grid_size-1), random.randint(0,grid_size-1)
        i = 0 if _<init_plants//2 else 1
        seed_plants.append((x,y,i))

    ### 1. Population 'a' survives
    plant_types1 = [
        {
            "plant_type": " 'x' - Plantie magnifica",
            "replication_frequency":0.5,
            "aggressivity": 0.4,
            "image_representation": ".",
            "color": "blue",
            "max_population": K
        },
        {
            "plant_type": " 'y' - Planta simplifica",
            "replication_frequency":0.5,
            "aggressivity": 2.1,
            "image_representation": "o",
            "color": "red",
            "max_population": L
        }
    ]
    output1 = "./result1.txt"
    logger.info("\n\nInit main ______________________________________________________")

    sim1 = Simulation.Simulation(plant_types=plant_types1, grid_size=grid_size, steps_num=num_steps+10,
                                output_file=output1, output_folder=".\SimulationPlots_case1",
                                replication_logic=Equations.Equations.competition_2population_max_size,
                                 simulation_message="1. Population 'x' - Plantie magnifica should survive")
    sim1.run(seed_plants=seed_plants)
    # sim1.run(plants_num=init_plants)

    ### 2. Population b. survives
    plant_types2 = [
        {
            "plant_type": " 'x' - Plantie magnifica",
            "replication_frequency":0.5,
            "aggressivity": 0.9,
            "image_representation": ".",
            "color": "blue",
            "max_population": K
        },
        {
            "plant_type": " 'y' - Planta simplifica",
            "replication_frequency":0.5,
            "aggressivity": 1.5,
            "image_representation": "o",
            "color": "red",
            "max_population": L
        }
    ]
    output2 = "./result2.txt"
    logger.info("\n\nInit main ______________________________________________________")

    sim2 = Simulation.Simulation(plant_types=plant_types2, grid_size=grid_size, steps_num=num_steps,
                                output_file=output2, output_folder=".\SimulationPlots_case2",
                                replication_logic=Equations.Equations.competition_2population_max_size,
                                 simulation_message="2. Population 'y' - Planta simplifica")
    sim2.run(seed_plants=seed_plants)
    # sim2.run(plants_num=init_plants)




    ### 3. Both survive
    plant_types3 = [
        {
            "plant_type": " 'x' - Plantie magnifica",
            "replication_frequency":0.5,
            "aggressivity": 0.3,
            "image_representation": ".",
            "color": "blue",
            "max_population": K
        },
        {
            "plant_type": " 'y' - Planta simplifica",
            "replication_frequency":0.5,
            "aggressivity": 1.3,
            "image_representation": "o",
            "color": "red",
            "max_population": L
        }
    ]
    output3 = "./result3.txt"
    logger.info("\n\nInit main ______________________________________________________")

    sim3 = Simulation.Simulation(plant_types=plant_types3, grid_size=grid_size, steps_num=num_steps,
                                output_file=output3, output_folder=".\SimulationPlots_case3",
                                replication_logic=Equations.Equations.competition_2population_max_size,
                                 simulation_message="3. Both should survive")
    sim3.run(seed_plants=seed_plants)
    # sim3.run(plants_num=init_plants)



    # 4. Survives one or the second
    plant_types4 = [
        {
            "plant_type": " 'x' - Plantie magnifica",
            "replication_frequency":0.5,
            "aggressivity": 0.9,
            "image_representation": ".",
            "color": "blue",
            "max_population": K
        },
        {
            "plant_type": " 'y' - Planta simplifica",
            "replication_frequency":0.5,
            "aggressivity": 2.2,
            "image_representation": "o",
            "color": "red",
            "max_population": L
        }
    ]
    output4 = "./result4.txt"
    logger.info("\n\nInit main ______________________________________________________")

    sim4 = Simulation.Simulation(plant_types=plant_types4, grid_size=grid_size, steps_num=num_steps,
                                output_file=output4, output_folder=".\SimulationPlots_case4",
                                replication_logic=Equations.Equations.competition_2population_max_size,
                                 simulation_message="4. Should survive one or the other")
    sim4.run(seed_plants=seed_plants)
    # sim4.run(plants_num=init_plants)




if __name__=="__main__":
    main()