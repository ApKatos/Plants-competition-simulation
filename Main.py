from src import Simulation

def main():
    plant_types=[
        {
            "plant_type": "qwerty",
            "replication_strength": 1,
            "image_representation": "o"
        },
        # {
        #     "plant_type": "kolko",
        #     "replication_strength": 1,
        #     "image_representation": "x"
        # }
    ]
    sim = Simulation.Simulation(plant_types=plant_types, grid_size=4, steps_num=1)
    sim.run(plants_num=9)


if __name__=="__main__":
    main()