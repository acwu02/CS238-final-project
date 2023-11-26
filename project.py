from map import Map
import numpy as np
import csv

MAP_WIDTH = 20
MAP_HEIGHT = 20

def next_state(s, a, states):
    sp = tuple(x + y for x, y in zip(s, a))
    return sp if sp in states else None

def find_actions_and_states(s, states):
    possible_actions = {
        (1, 0): 1,
        (-1, 0): 2,
        (0, 1): 3,
        (0, -1): 4
    }
    return [(possible_actions[a], next_state(s, a, states))
        for a in possible_actions.keys() if next_state(s, a, states)]

def write_csv(map, file_name):
    header = ['s', 'a', 'r', 'sp']
    dataset = [header]
    states = map.tiles
    for s, r in states.items():
        possible_moves = find_actions_and_states(s, states)
        for a, sp in possible_moves:
            # TODO implement rewards
            dataset.append(
                [
                    np.ravel_multi_index(s, dims=(MAP_WIDTH, MAP_HEIGHT)),
                    a,
                    r,
                    np.ravel_multi_index(sp, dims=(MAP_WIDTH, MAP_HEIGHT)),
                ]
            )

    with open(file_name, mode='w', newline='') as csv_file:
        csv_writer = csv.writer(csv_file)
        for row in dataset:
            csv_writer.writerow(row)

def main():
    map = Map()
    map.generate()
    print(map.tiles)
    write_csv(map, "test.csv")

if __name__ == "__main__":
    main()