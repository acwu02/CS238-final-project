from map import Map
import numpy as np
import csv

MAP_WIDTH = 20
MAP_HEIGHT = 20

def write_csv(map, file_name):
    header = ['s', 'a', 'r', 'sp']
    pts = [np.ravel_multi_index(i, dims=(MAP_WIDTH, MAP_HEIGHT)) for i in map.tiles]

    with open(file_name, mode='w', newline='') as csv_file:
        csv_writer = csv.writer(csv_file)

map = Map()
map.generate()
write_csv(map, "test.csv")