import numpy as np

from array_tomography_lib import colocalisation_result

if __name__ == "__main__":
    n_objects = 10
    colocalisation_result = colocalisation_result.ColocalisationResult("A", 10, ["B", "C"])
    for a in range(n_objects):
        colocalisation_result.colocalisations[a] = {
            "A": 1,
            "B": np.random.randint(2),
            "C": np.random.randint(2),
        }

    colocalisation_result.print_colocalisations()
    colocalisation_result.get_results()
    # colocalisa/tion_save.get_combinations()
