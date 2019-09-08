from ArrayTomographyLib import ColocalisationSave
import numpy as np

if __name__ == "__main__":

    n_objects = 10
    colocalisation_save = ColocalisationSave.ColocalisationSave("A", 10, ["B", "C"])
    for a in range(n_objects):
        colocalisation_save.colocalisations[a] = {
            "A": 1,
            "B": np.random.randint(2),
            "C": np.random.randint(2),
        }

    colocalisation_save.print_colocalisations()
    colocalisation_save.get_results()
    # colocalisa/tion_save.get_combinations()
