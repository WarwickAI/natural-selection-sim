import sys
import random
import uuid


class Color:
    RESET = '\033[0m'
    RED = '\033[91m'
    GREEN = '\033[92m'
    BLUE = '\033[94m'
    CYAN = '\033[36m'
    YELLOW = '\033[33m'
    WHITE = '\033[37m'


class Simulation:

    def __init__(self, max_x, max_y, seed):
        self.seed = seed
        self.max_x = max_x
        self.max_y = max_y

        random.seed(seed)

    def do_cycles(self, num_moves, display=True):
        for i in range(0, num_moves):
            for entity in Entity.entities:
                if entity.is_active:
                    entity.tick()

            if display:
                print("\033c")
                print("Current move: " + str(i))
                self.display()

                input()

    def display_cells_info(self):
        total_sense_distance = 0
        num_alive_cells = 0

        for entity in Entity.entities:
            if type(entity) is Cell:
                if entity.is_active:
                    total_sense_distance += entity.sense_distance
                    num_alive_cells += 1

                    print(entity.display_info())

        avg_sense_distance = total_sense_distance / num_alive_cells

        print()
        print(f"{Color.CYAN}Displaying Cell information:{Color.RESET}")
        print()

        print("There are currently " + Color.CYAN +
              str(num_alive_cells) + Color.RESET + " living Cells")
        print("The average sense distance is " + Color.CYAN +
              str(avg_sense_distance) + Color.RESET)

    def build_entity_location_dict(self):
        entities = {}

        for entity in Entity.entities:
            if entity.is_active:
                entities[entity.get_location()] = entity
        
        return entities

    def display(self):
        entity_location = self.build_entity_location_dict()
        map_text = ""

        for y in range(1, self.max_y + 1):
            map_text += "\n"
            for x in range(1, self.max_x + 1):

                location = (x, y)

                if location in entity_location:
                    entity = entity_location.get(location)
                    map_text += entity.get_symbol()
                else:
                    map_text += Color.BLUE + " _"

        print(map_text + Color.RESET + "\n")


class Entity:
    entities = []

    def __init__(self, x, y):
        self.entities.append(self)

        self.id = uuid.uuid4()
        self.is_active = True
        self.x = x
        self.y = y

    def die(self):
        self.is_active = False

    def get_location(self):
        return (self.x, self.y)

    def translate_by(self, dx, dy):
        self.x += dx
        self.y += dy

    def manh_distance_to(self, entity):
        target_x, target_y = entity.get_location()

        return abs(self.x - target_x) + abs(self.y - target_y)

    def get_closest_entity(self, of_type, max_distance=200):
        min_entity = None
        min_distance = 9999999

        for entity in self.entities:
            if type(entity) is of_type and entity.is_active:
                distance = self.manh_distance_to(entity)

                if distance < min_distance and distance <= max_distance:
                    min_distance = distance
                    min_entity = entity
        
        return min_entity, min_distance        

    def move_close_to(self, entity):
        target_x, target_y = entity.get_location()

        if target_x > self.x:
            self.translate_by(1, 0)
        elif target_x < self.x:
            self.translate_by(-1, 0)
        elif target_y > self.y:
            self.translate_by(0, 1)
        else:
            self.translate_by(0, -1)

    def tick(self):
        pass

    def get_symbol(self):
        pass


class Food(Entity):
    def __init__(self, x, y):
        super().__init__(x, y)

        self.energy = 10

    def get_energy(self):
        return self.energy

    def get_symbol(self):
        return Color.GREEN + " o"


class Cell(Entity):
    def __init__(self, generation, x, y, energy, sense_distance):
        super().__init__(x, y)

        self.generation = generation
        self.energy = energy
        self.sense_distance = sense_distance
        self.total_moves = 0

        mutation_chance = random.random()
        if mutation_chance > 0.5:
            self.mutate()

    def get_symbol(self):
        return Color.RED + " @"

    def display_info(self):
        info = ("Cell ID: " + str(self.id))
        info += (" | Energy: " + str(self.energy))
        info += (" | XY: " + "(" + str(self.x) + ", " + str(self.y) + ")")
        info += (" | Sense Distance: " + str(self.sense_distance))
        info += (" | Moves: " + str(self.total_moves))
        info += (" | Status: " + "Alive" if self.is_active else "Dead")

        return info

    def move_random(self):
        dx, dy = random.choice([(0, 1), (0, -1), (1, 0), (-1, 0)])

        while not (0 < self.x + dx <= 20 and 0 < self.y + dy <= 20):
            dx, dy = random.choice([(0, 1), (0, -1), (1, 0), (-1, 0)])

        self.translate_by(dx, dy)

    def tick(self, directed=False):
        nearest_food, distance = self.get_closest_entity(Food, max_distance=self.sense_distance)

        if not nearest_food:
            self.move_random()
        else:
            self.move_close_to(nearest_food)

            if distance == 1:
                self.eat(nearest_food)

        self.total_moves += 1
        self.energy -= 1

        if self.energy <= 0:
            self.die()
        elif self.energy >= 100:
            self.reproduce()

        if self.total_moves > 100:
            self.die()

    def eat(self, food):
        self.energy += food.get_energy()
        food.die()

    def mutate(self):
        change = random.choice([-1, 1])
        if self.sense_distance + change >= 1:
            self.sense_distance += change

    def reproduce(self):
        if self.y < 50:
            spawn_y = self.y + 1
            spawn_x = self.x
        elif self.x < 50:
            spawn_x = self.x + 1
            spawn_y = self.y
        else:
            spawn_x = self.x - 1
            spawn_y = self.y - 1

        new_cell = Cell(self.generation + 1, spawn_x,
                        spawn_y, 50, self.sense_distance)
        self.energy -= 50


def add_food(num_food, verbose=False):
    for i in range(1, num_food + 1):
        x, y = random.randint(1, 20), random.randint(1, 20)
        Food(x, y)

    if verbose:
        print("\nAdding " + str(num_food) + " food")

def create_cells(num_cells, verbose=False):
    for i in range(1, num_cells + 1):
        x, y = random.randint(1, 20), random.randint(1, 20)
        Cell(0, x, y, 30, 3)

    if verbose:
        print("Adding " + str(num_cells) + " cells")


if __name__ == '__main__':
    simulation = Simulation(20, 20, seed="WAI")
    add_food(100)
    create_cells(5)

    # Begin menu display
    exit = False
    while not exit:
        print("\n" + Color.BLUE + "▄" * 50 + "\n" + Color.RESET)

        print(f"{Color.CYAN}Cell Natural Selection Simulation{Color.RESET}\n")

        print("1) Add a Cell")
        print("2) Add Food")
        print("3) See Cell Info")
        print("4) View Map")
        print("x) Begin Evolution Cycle")
        print("\n" + Color.BLUE + "▀" * 50 + "\n" + Color.RESET)

        val = input("Press a key: ")
        if val == "1":
            create_cells(1, verbose=True)
        elif val == "2":
            add_food(10, verbose=True)
        elif val == "3":
            simulation.display_cells_info()
        elif val == "4":
            simulation.display()
        elif val == "x":
            print("Beginning evolution cycle")
            simulation.do_cycles(100)
        elif val == "q":
            print("Exiting")
            exit = True

        input()


# TO DO

# Make cell to path to nearest food when food detected
# Make offspring mutate their sense distance up or down on birth
# Test and hopefully observe population sense distance change over time
#


# DONE
# add a new cell attribute with states 0, 1, 2 (die, survive, reproduce)
# upon beginning a cycle, begin random walk
# create a cycle routine that controls the cycles on key press
# add check to ensure cell doesn't leave boundaries
# Fix food map display
# Change cycle routine to step on key press
# each tick, check current location against the food map
# if there is a match, call a function that deletes food from list and increases energy of cell, and changes survival state of cell
# Create pathing algorithm
