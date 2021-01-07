import json
from os import walk, path
from nss import Simulation, Entity, add_food, create_cells

def run_test(name, test):
    simulation_settings = test['simulation_settings']
    entities_cycles = test['entities_cycles']

    print(f'Running test {name} with {len(entities_cycles)} cycles.')

    simulation = Simulation(**simulation_settings)
    add_food(100)
    create_cells(5)

    for i in range(len(entities_cycles)):
        simulation.do_cycles(1, False)

        assert verify_cycle(Entity.entities, entities_cycles[i]), f'\033[91mFailed cycle {i} in test {name}!\033[0m'
    
    print(f'Code passed test {name}!')

def get_entity_info(entity):
    return {
        'x': entity.x,
        'y': entity.y,
        'type': str(type(entity))
    }

def verify_cycle(entities, test_cycle):
    active_entities = filter(lambda e: e.is_active, entities)
    return all((e in test_cycle) for e in list(map(get_entity_info, active_entities)))

def read_test(file_path):
    data = None

    with open(file_path) as file:
        data = json.load(file)

    return data

def run_tests():
    print('Running tests...')

    for root, dirs, files in walk('tests/'):
        test_files = list(filter(lambda name: name.endswith('.json'), files))
        total = len(test_files)

        print(f'Found {total} test(s)')

        for file_name in test_files:
            file_path = path.join(root, file_name)

            run_test(file_name, read_test(file_path))

    print()
    print(25 * '=')
    print('\033[92mAll tests passed successfully\033[0m')
        
if __name__ == '__main__':
    run_tests()