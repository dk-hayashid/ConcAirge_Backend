import numpy as np


def return_measured_data():
    temperature_list = [21.7, 21.9, 22.1, 22.1, 23.0, 21.8, 22.3, 22.3, 22.7, 23.3, 22.3, 22.8, 22.7, 22.8, 22.8, 22.6, 22.7, 22.7, 22.7, 22.6, 23.7, 23.1, 23.0, 22.9, 22.8, 23.0,
                        23.1, 23.0, 23.0, 22.8, 23.0, 23.1, 23.1, 23.1, 22.9, 23.3, 23.2, 23.2, 23.2, 22.9, 23.1, 23.6, 24.1, 23.1, 23.1, 23.3, 23.2, 23.1, 23.0, 22.9, 22.9, 23.0, 22.8, 22.9, 23.0]
    data = np.array(temperature_list)
    return data
