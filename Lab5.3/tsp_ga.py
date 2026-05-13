import random
import math

from numpy import power
"""接收文件路径；返回坐标(x, y)列表"""
def read_tsp(filepath):
    """Parse TSPLIB format file, return list of (x, y) coordinates."""
    coords = []
    reading = False
    with open(filepath, 'r') as f:
        for line in f:
            line = line.strip()
            if line.startswith('NODE_COORD_SECTION'):
                reading = True
                continue
            if line == 'EOF':
                break
            if reading:
                parts = line.split()
                if len(parts) >= 3:
                    coords.append((float(parts[1]), float(parts[2])))
    return coords
"""接收两个二维坐标；返回欧氏距离"""
def calc_distance(a, b):
    return math.sqrt((a[0] - b[0])**2 + (a[1] - b[1])**2)
"""接收一条路径（坐标序列）；返回总长度"""
def tour_length(tour, coords):
    total = 0.0
    n = len(tour)
    for i in range(n):
        total += calc_distance(coords[tour[i]], coords[tour[(i + 1) % n]])
    return total
"""种群初始化，规模为n_cities，返回一个二维列表（pop_size个长度为n_cities的随机路径"""
def init_population(n_cities, pop_size):
    base = list(range(n_cities))
    population = []
    for _ in range(pop_size):
        perm = base[:]
        random.shuffle(perm)
        population.append(perm)
    return population
"""锦标赛选择，从种群里随机抽取tournament_size个个体并以fitness选择适应度最高者"""
def tournament_select(population, fitness, tournament_size=3):
    indices = random.sample(range(len(population)), tournament_size)
    best_idx = max(indices, key=lambda x: fitness[x])
    return population[best_idx][:]
"""OX交叉"""
def order_crossover(parent1, parent2):
    """Order Crossover (OX) — always produces a valid permutation."""
    n = len(parent1)
    s, t = sorted(random.sample(range(n), 2))

    child = [-1] * n
    child[s:t + 1] = parent1[s:t + 1]

    pos = (t + 1) % n
    for city in parent2[t + 1:] + parent2[:t + 1]:
        if city not in child:
            child[pos] = city
            pos = (pos + 1) % n
    return child
"""PMX交叉"""
def pmx_crossover(parent1, parent2):
    n = len(parent1)
    s, t = sorted(random.sample(range(n), 2))

    child = parent1[:]

    for i in range(s, t + 1):
        if child[i] == parent2[i]:
            continue
        j = child.index(parent2[i])
        child[i], child[j] = child[j], child[i]

    return child
"""交换变异"""
def swap_mutation(tour, mutation_possibility=0.1):
    """Swap two randomly chosen cities."""
    tour = tour[:]
    if random.random() < mutation_possibility:
        i, j = random.sample(range(len(tour)), 2)
        tour[i], tour[j] = tour[j], tour[i]
    return tour
"""反转变异"""
def inversion_mutation(tour, mutation_possibility=0.1):
    """Inversion mutation — reverse a random segment of the tour."""
    tour = tour[:]
    if random.random() < mutation_possibility:
        i, j = sorted(random.sample(range(len(tour)), 2))
        tour[i:j + 1] = reversed(tour[i:j + 1])
    return tour

def GA(coords, pop_size=100, generations=500, elite_size=3,
       crossover_possibility=0.8, mutation_possibility=0.998, tournament_size=3,
       crossover='ox', mutation='swap', seed=None, snapshot_interval=200,
       verbose=True):
    """Solve one TSP instance with a genetic algorithm.

    Parameters
    ----------
    coords : list of (float, float)
    pop_size : int
    generations : int
    elite_size : int
    crossover_possibility : float
    mutation_possibility : float
    tournament_size : int
    crossover : 'ox' or 'pmx'
    mutation : 'swap' or 'inversion'
    seed : int or None
    snapshot_interval : int
        Record (gen, best_tour, best_length) every N generations.
    verbose : bool

    Returns
    -------
    best_tour : list
    best_length : float
    history : list
    snapshots : list of (gen, tour, length)
    """
    if seed is not None:
        random.seed(seed)

    crossover_fn = order_crossover if crossover == 'ox' else pmx_crossover
    mutation_fn = swap_mutation if mutation == 'swap' else inversion_mutation

    n = len(coords)
    population = init_population(n, pop_size)
    best_tour = None
    best_length = float('inf')
    history = []
    snapshots = []

    for gen in range(generations):
        lengths = [tour_length(t, coords) for t in population]
        fitness = [1.0 / l for l in lengths]

        min_idx = min(range(len(lengths)), key=lambda i: lengths[i])
        if lengths[min_idx] < best_length:
            best_length = lengths[min_idx]
            best_tour = population[min_idx][:]

        history.append(best_length)

        # Record snapshot every snapshot_interval (include gen 0)
        if gen % snapshot_interval == 0:
            # Show current best tour (may differ from all-time best for current gen)
            current_tour = population[min_idx][:]
            snapshots.append((gen, current_tour, lengths[min_idx]))

        if verbose and gen % 50 == 0:
            print(f"  Gen {gen:4d} | Best: {best_length:12.2f}")

        sorted_idx = sorted(range(len(lengths)), key=lambda i: lengths[i])
        new_pop = [population[sorted_idx[i]][:] for i in range(elite_size)]

        while len(new_pop) < pop_size:
            p1 = tournament_select(population, fitness, tournament_size)
            p2 = tournament_select(population, fitness, tournament_size)

            if random.random() < crossover_possibility:
                child = crossover_fn(p1, p2)
            else:
                child = p1[:]

            child = mutation_fn(child, power(mutation_possibility, gen))
            new_pop.append(child)

        population = new_pop

    if verbose:
        print(f"  DONE  | Best: {best_length:12.2f}")

    return best_tour, best_length, history, snapshots
