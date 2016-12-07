from enum import Enum
import random as rnd


class Sea_cell(Enum):
    water = 0
    predator = 1
    victim = 2
    obstacle = 3


class Sea():
    def __init__(self, x_size, y_size, predators_count, victims_count, obstacles_count):
        if x_size <= 0 or y_size <= 0 or predators_count <= 0 or victims_count <= 0 or obstacles_count <= 0:
            raise ValueError("Sea arguments must be positive.")

        if x_size * y_size <= predators_count + victims_count + obstacles_count:
            raise ValueError("Too much components of sea.")

        self.predators_count = predators_count
        self.victims_count = victims_count
        self.obstacles_count = obstacles_count
        self.size = (x_size, y_size)
        self.field = []
        self.generate_field()

    def __str__(self):
        return str(self.field)

    def generate_field(self):
        # use here rnd.shuffle()
        self.field = []


lst = [Sea_cell.water, Sea_cell.predator, Sea_cell.obstacle]
print(type(rnd.choice(lst)))
print(Sea(2, 3, 1, 1, 1))
