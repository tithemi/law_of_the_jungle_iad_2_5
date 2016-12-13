from enum import Enum
import random as rnd


class CellState(Enum):
    water = 0
    predator = 1
    victim = 2
    obstacle = 3

    def get_symbol(state):
        return ['~', '#', 'o', '@'][state.value]


class Sea:
    def __init__(self, x_size, y_size, predators_count, victims_count, obstacles_count, pred_life_expectancy,
                 reproduction_tick):
        if x_size <= 0 or y_size <= 0 or predators_count < 0 or victims_count < 0 or obstacles_count < 0:
            raise ValueError("Sea arguments must be positive.")

        if x_size * y_size <= predators_count + victims_count + obstacles_count:
            raise ValueError("Too much components of sea.")

        self.predators_count = predators_count
        self.victims_count = victims_count
        self.obstacles_count = obstacles_count
        self.size = (x_size, y_size)
        self.field = []
        self.predator_life_expectancy = pred_life_expectancy
        self.reproduction_tick = reproduction_tick
        self.used_cells = []
        self.generate_field()

    def __str__(self):
        # return str(self.field)
        out_str = ''
        for i in self.field:
            for j in i:
                out_str += CellState.get_symbol(j[0]) + ' '
            out_str += '\n'
        out_str = '\nVictims: {} predators: {}\n'.format(self.get_type_count(CellState.victim),
                                                       self.get_type_count(CellState.predator)) + out_str
        return out_str

    def generate_field(self):
        self.field = []
        cells = [CellState.water, CellState.predator, CellState.victim, CellState.obstacle]
        gen_lst = []
        gen_lst += [[CellState.predator, self.reproduction_tick, self.predator_life_expectancy] for i in
                    range(self.predators_count)]
        gen_lst += [[CellState.victim, self.reproduction_tick] for i in range(self.victims_count)]
        gen_lst += [[CellState.obstacle] for i in range(self.obstacles_count)]
        gen_lst += [[CellState.water] for i in range(
            self.size[0] * self.size[1] - self.predators_count - self.victims_count - self.obstacles_count)]
        rnd.shuffle(gen_lst)
        # print(len(gen_lst), gen_lst)
        lst = []
        for y in range(self.size[0]):
            l = []
            for x in range(self.size[1]):
                l += [gen_lst[x + y * self.size[1]]]
            lst += [l]
        self.field = lst
        # self.field = [[gen_lst[i + j * self.size[1]] for i in range(self.size[1])] for j in range(self.size[0])]

    def get_type_count(self, type):
        return sum([sum([1 for i in range(self.size[0]) if self.get_type(i, j) == type]) for j in range(self.size[1])])

    def clear_cell(self, x, y):
        self.field[x][y] = [CellState.water]

    # without obstacles
    def get_available_neighbours(self, x_inp, y_inp):
        lst = []
        xmax, ymax = self.size[0] - 1, self.size[1] - 1
        for i in range(x_inp - 1, x_inp + 2):
            for j in range(y_inp - 1, y_inp + 2):
                # print(i, j, xmax, ymax)
                if 0 <= i <= xmax and 0 <= j <= ymax and (i != x_inp or j != y_inp) and \
                                self.field[i][j][0] != CellState.obstacle:
                    lst += [[i, j]]
        return lst

    def get_water_neighbours(self, x, y):
        return [i for i in self.get_available_neighbours(x, y) if self.get_type(i[0], i[1]) == CellState.water]

    def get_cell(self, x, y):
        return self.field[x][y]

    def get_type(self, x, y):
        return self.get_cell(x, y)[0]

    def add_new_creature(self, x, y, type, left_life_length):
        creature = [type, self.reproduction_tick]
        if type == CellState.predator:
            creature += [left_life_length]
        self.field[x][y] = creature

    def try_give_birth(self, x, y):
        self.used_cells = [[x, y]]
        type = self.get_type(x, y)
        if type == CellState.water or type == CellState.obstacle:
            return
        if self.get_cell(x, y)[1] > 0:
            return

        self.field[x][y][1] = self.reproduction_tick

        for (i, j) in self.get_water_neighbours(x, y):
            self.add_new_creature(i, j, self.get_type(x, y),
                                  self.get_cell(x, y)[2] if type == CellState.predator else 0)
            return

    def decrease_days_until_birth(self, x, y):
        self.field[x][y][1] -= 1

    def take_step_to_any_water(self, x, y):
        neibs = self.get_water_neighbours(x, y)
        rnd.shuffle(neibs)
        for (i, j) in neibs:
            self.field[i][j] = self.field[x][y]
            self.decrease_days_until_birth(x, y)
            if self.get_type(x, y) == CellState.predator:
                self.field[i][j][2] -= 1
                if self.field[i][j][2] < 1:
                    self.clear_cell(i, j)

            self.clear_cell(x, y)
            # print(self)

            return [i, j]
        return [x, y]

    def try_to_find_food_and_eat(self, x, y):
        for (i, j) in self.get_available_neighbours(x, y):
            if self.get_type(i, j) == CellState.victim:
                self.field[i][j] = self.field[x][y]
                self.clear_cell(x, y)
                self.field[i][j][2] = self.predator_life_expectancy
                self.field[i][j][1] -= 1
                return 1
        return 0

    def take_step(self, x_inp, y_inp):

        type = self.get_type(x_inp, y_inp)

        if type == CellState.water or type == CellState.obstacle:
            return

        neighbours = self.get_available_neighbours(x_inp, y_inp)

        if len(neighbours) < 1:
            return

        if type == CellState.predator:
            if self.try_to_find_food_and_eat(x_inp, y_inp) == 1:
                self.try_give_birth(x_inp, y_inp)
                return

        x, y = self.take_step_to_any_water(x_inp, y_inp)
        self.try_give_birth(x, y)

    def live_day(self):
        # print(len(self.field))
        self.used_cells = []
        for y in range(self.size[1]):
            for x in range(self.size[0]):
                if [x, y] not in self.used_cells:
                    # print(x, y)
                    self.take_step(x, y)

    def live_life(self, max_repeats):
        print(sea)
        for i in range(max_repeats):
            time.sleep(stop_time)
            sea.live_day()
            print(sea)
            if not (self.get_type_count(CellState.predator) and self.get_type_count(CellState.victim)):
                return


import time

# x, y, predators, victims_count, obstacles_count, life_length, reprod
x = 5
y = 6
predators = 1
victims = 10
obstacles_count = 1
predators_life_expectancy = 5
reproduction_time = 10
stop_time = .2
repeats_count = 25
sea = Sea(x, y, predators, victims, obstacles_count, predators_life_expectancy, reproduction_time)
sea.live_life(repeats_count)
# print(SeaCell.)
