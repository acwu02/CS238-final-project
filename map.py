import random
import matplotlib.pyplot as plt

MAP_WIDTH = 20
MAP_HEIGHT = 20

OPEN_SPACE = "."

def get_random_number(min_val, max_val):
    return random.randint(min_val, max_val)

class Vertex:
    def __init__(self, id):
        self.id = id
        self.tiles = {}

class Room(Vertex):
    def __init__(self, id):
        super().__init__(id)
        self._height = get_random_number(5, 15)
        self._width = get_random_number(5, 15)

        self.corners = {
            'topLeft': None,
            'topRight': None,
            'bottomLeft': None,
            'bottomRight': None
        }

        self.coords = []
        self.generate()

    def generate(self):
        self.tiles = {}
        self._generate_corners()
        self._generate_walls()
        self._generate_interior()

    def _generate_corners(self):
        self.corners['topLeft'] = {
            'x': get_random_number(0, MAP_WIDTH - 10),
            'y': get_random_number(0, MAP_HEIGHT - 10)
        }
        height = get_random_number(3, 5)
        width = get_random_number(5, 8)
        self.corners['topRight'] = {
            'x': self.corners['topLeft']['x'] + width,
            'y': self.corners['topLeft']['y']
        }
        self.corners['bottomLeft'] = {
            'x': self.corners['topLeft']['x'],
            'y': self.corners['topLeft']['y'] + height
        }
        self.corners['bottomRight'] = {
            'x': self.corners['topLeft']['x'] + width,
            'y': self.corners['topLeft']['y'] + height
        }
        self.x_min = self.corners['topLeft']['x']
        self.y_min = self.corners['topLeft']['y']
        self.x_max = self.corners['topRight']['x']
        self.y_max = self.corners['bottomLeft']['y']
        for key in self.corners:
            corner = self.corners[key]
            self.tiles[(corner['x'], corner['y'])] = OPEN_SPACE

    def _generate_walls(self):
        for i in range(self.x_min, self.x_max):
            self.tiles[(i, self.y_min)] = OPEN_SPACE
            self.tiles[(i, self.y_max)] = OPEN_SPACE
        for i in range(self.y_min, self.y_max):
            self.tiles[(self.x_min, i)] = OPEN_SPACE
            self.tiles[(self.x_max, i)] = OPEN_SPACE

    def _generate_interior(self):
        for i in range(self.x_min + 1, self.x_max):
            for j in range(self.y_min + 1, self.y_max):
                self.tiles[(i, j)] = OPEN_SPACE

class Graph:
    def __init__(self):
        self.vertices = {}
        self.adjacency_list = {}

    def add_vertex(self, vertex):
        self.vertices[vertex.id] = vertex
        self.adjacency_list[vertex.id] = []

    def add_edge(self, vertex1, vertex2):
        self.adjacency_list[vertex1.id].append(vertex2.id)
        self.adjacency_list[vertex2.id].append(vertex1.id)

    def remove_all_vertices(self):
        self.vertices = {}
        self.adjacency_list = {}

    def randomly_add_edges(self):
        num_edges = random.randint(0, len(self.vertices) - 1)
        for _ in range(num_edges):
            v1 = self.get_random_vertex()
            v2 = self.get_random_vertex()
            if v1.id != v2.id and v2.id not in self.adjacency_list[v1.id]:
                self.add_edge(v1, v2)

        connected_components = self.get_connected_components()
        if len(connected_components) > 1:
            self.connect_unconnected_vertices(connected_components)

    def connect_unconnected_vertices(self, connected_components):
        curr_component = connected_components[0]
        for i in range(len(connected_components) - 1):
            random_vertex1 = self.vertices[random.choice(curr_component)]
            next_component = connected_components[i + 1]
            random_vertex2 = self.vertices[random.choice(next_component)]
            curr_component = next_component
            self.add_edge(random_vertex1, random_vertex2)

    def get_random_vertex(self):
        random_key = random.choice(list(self.vertices.keys()))
        return self.vertices[random_key]

    def get_connected_components(self):
        visited = {}
        connected_components = []
        for vertex in self.vertices:
            if vertex not in visited:
                component = []
                self.dfs(vertex, visited, component)
                connected_components.append(component)
        return connected_components

    def dfs(self, vertex, visited, component):
        visited[vertex] = True
        component.append(vertex)
        for neighbor in self.adjacency_list[vertex]:
            if neighbor not in visited:
                self.dfs(neighbor, visited, component)


class Map(Graph):
    def __init__(self):
        super().__init__()
        self._height = MAP_HEIGHT
        self._width = MAP_WIDTH
        self.tiles = {}
        self.enemies = {}

    def generate(self):
        self._generate_rooms()
        self.randomly_add_edges()
        for key, room in self.vertices.items():
            self.tiles.update(room.tiles)
            for coords, tile in room.tiles.items():
                x, y = coords[0], coords[1]
        self._generate_paths()

    def _is_in_vertices(self, x, y):
        for vertex in self.vertices.values():
            for corner in vertex.corners.values():
                if corner.x == x and corner.y == y:
                    return True
        return False

    def _generate_rooms(self):
        num_of_rooms = random.randint(0, 4) + 5
        for i in range(num_of_rooms):
            room = Room(i)
            counter = 0
            while not self._is_allowed_location(room):
                room.generate()
                if counter >= 50:
                    return
                counter += 1
            self.add_vertex(room)

    def _is_allowed_location(self, room1):
        for room2 in self.vertices.values():
            if self._overlaps(room1, room2) or self._overlaps(room2, room1):
                return False
        return True

    def _overlaps(self, room1, room2):
        for corner in room1.corners.values():
            if (room2.corners['bottomLeft']['x'] - 1 <= corner['x'] <= room2.corners['bottomRight']['x'] + 1 and
                    room2.corners['topLeft']['y'] - 1 <= corner['y'] <= room2.corners['bottomLeft']['y'] + 1):
                return True
        return False

    def _generate_paths(self):
        drawn_edges = {}
        for key, room in self.vertices.items():
            for adjacent in self.adjacency_list[room.id]:
                sorted_edge = tuple(sorted([room.id, adjacent]))
                if not drawn_edges.get(sorted_edge):
                    self._generate_path(room, self.vertices[adjacent])
                    drawn_edges[sorted_edge] = True

    def _generate_path(self, room1, room2):
        start_with_y = random.choice([True, False])
        p1 = {'x': random.randint(room1.x_min + 1, room1.x_max - 1),
              'y': random.randint(room1.y_min + 1, room1.y_max - 1)}
        p2 = {'x': random.randint(room2.x_min + 1, room2.x_max - 1),
              'y': random.randint(room2.y_min + 1, room2.y_max - 1)}
        path = []
        while p1['x'] != p2['x']:
            p1['x'] += 1 if p1['x'] < p2['x'] else -1
            path.append([p1['x'], p1['y']])
        while p1['y'] != p2['y']:
            p1['y'] += 1 if p1['y'] < p2['y'] else -1
            path.append([p1['x'], p1['y']])

        self._draw_path(path)

    def _draw_path(self, path):
        for px in path:
            x, y = px
            tile = OPEN_SPACE
            self.tiles[(x, y)] = tile

    # TODO fix
    def add_item(self, item):
        random_room = self.get_random_vertex()
        item.x = random.randint(random_room.x_min + 1, random_room.x_max - 1)
        item.y = random.randint(random_room.y_min + 1, random_room.y_max - 1)
        while not self._is_valid_item_location(item):
            item.x = random.randint(random_room.x_min + 1, random_room.x_max - 1)
            item.y = random.randint(random_room.y_min + 1, random_room.y_max - 1)
        self.update_tile(item)
        return True

    def get_tile(self, x, y):
        tile = self.tiles.get(f'{x},{y}')
        return tile if tile else None

    def is_open_tile(self, x, y):
        return self.get_tile(x, y) == '.'

def plot(tiles):
    x_coords, y_coords = zip(*tiles.keys())
    plt.scatter(x_coords, y_coords)
    plt.xlabel('X Coordinate')
    plt.ylabel('Y Coordinate')
    plt.show()

def main():
    map = Map()
    map.generate()
    plot(map.tiles)

if __name__ == "__main__":
    main()