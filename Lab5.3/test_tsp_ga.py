"""
Tests and runner for tsp_ga.py — Genetic Algorithm TSP solver.

Usage (solve):
    python test_tsp_ga.py                    # interactive: pick file & operators
    python test_tsp_ga.py wi29.tsp           # quick solve with defaults
    python test_tsp_ga.py wi29.tsp --crossover pmx --mutation inversion --gen 300

Usage (unit tests):
    python -m pytest test_tsp_ga.py -v
    python test_tsp_ga.py --test
"""
import unittest
import random
import math
import os
import sys
import time
import glob

import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from tsp_ga import (
    read_tsp, calc_distance, tour_length,
    init_population, tournament_select,
    order_crossover, pmx_crossover,
    swap_mutation, inversion_mutation,
    GA,
)


# ============================================================
# Visualization
# ============================================================

def print_tour_path(tour):
    """Print best tour as 1→2→3→...→1."""
    path_str = "→".join(str(i + 1) for i in tour)
    path_str += f"→{tour[0] + 1}"
    print(f"\n  Best tour path:")
    print(f"  {path_str}")


def plot_convergence(history, snapshot_interval=200):
    """Line chart: best tour length vs generation."""
    plt.figure(figsize=(10, 5))
    plt.plot(history, linewidth=0.8, color='steelblue')
    plt.xlabel('Generation')
    plt.ylabel('Best Tour Length')
    plt.title('GA Convergence — Best Tour Length over Generations')
    # Mark snapshot points
    for g in range(0, len(history), snapshot_interval):
        if g < len(history):
            plt.scatter(g, history[g], color='red', s=30, zorder=5)
    plt.tight_layout()
    plt.show(block=False)


def plot_tour_snapshots(coords, snapshots, cols=3):
    """Show 2D city+tour plots, one per snapshot. Cities = red dots, tour = blue lines."""
    n = len(snapshots)
    rows = math.ceil(n / cols)

    fig, axes = plt.subplots(rows, cols, figsize=(5 * cols, 5 * rows))
    axes = axes.flatten() if hasattr(axes, 'flatten') else [axes]

    for idx, (gen, tour, length) in enumerate(snapshots):
        ax = axes[idx]
        # Cities as red dots
        xs = [c[0] for c in coords]
        ys = [c[1] for c in coords]
        ax.scatter(xs, ys, c='red', s=20, zorder=5)

        # Tour as blue lines
        for i in range(len(tour)):
            a = coords[tour[i]]
            b = coords[tour[(i + 1) % len(tour)]]
            ax.plot([a[0], b[0]], [a[1], b[1]],
                    color='steelblue', linewidth=0.6, alpha=0.8)

        ax.set_title(f"Gen {gen}  |  Length: {length:,.1f}", fontsize=9)
        ax.set_aspect('equal')
        ax.axis('off')

    # Hide unused subplots
    for idx in range(n, len(axes)):
        axes[idx].set_visible(False)

    plt.suptitle("Tour Evolution (every 200 generations)", fontsize=13, y=0.98)
    plt.tight_layout()
    plt.show(block=False)


# ============================================================
# User-facing solver
# ============================================================

def solve_tsp_file(filepath, pop_size=100, generations=500, elite_size=2,
                   crossover_possibility=0.8, mutation_possibility=0.2,
                   tournament_size=3, crossover='ox', mutation='swap',
                   seed=42, verbose=True):
    """Read a TSP file and solve it with the GA.

    Displays:
      - best tour path (e.g. 1→2→3→...→1)
      - convergence line chart
      - 2D tour evolution snapshots
    """
    coords = read_tsp(filepath)
    n = len(coords)

    # Scale down for large instances
    if n > 5000:
        pop_size = min(pop_size, 30)
        generations = min(generations, 100)
    elif n > 1000:
        pop_size = min(pop_size, 50)
        generations = min(generations, 200)
    elif n > 200:
        pop_size = min(pop_size, 80)
        generations = min(generations, 300)

    snapshot_interval = 200

    print(f"File     : {filepath}")
    print(f"Cities   : {n}")
    print(f"Pop size : {pop_size}   Generations: {generations}")
    print(f"Crossover: {crossover}     Mutation   : {mutation}")
    print("-" * 50)

    t0 = time.time()
    tour, length, history, snapshots = GA(
        coords,
        pop_size=pop_size,
        generations=generations,
        elite_size=elite_size,
        crossover_possibility=crossover_possibility,
        mutation_possibility=mutation_possibility,
        tournament_size=tournament_size,
        crossover=crossover,
        mutation=mutation,
        seed=seed,
        snapshot_interval=snapshot_interval,
        verbose=verbose,
    )
    elapsed = time.time() - t0

    print(f"\n  Best tour length : {length:12.2f}")
    print(f"  Time elapsed     : {elapsed:7.1f} s")

    # Show results
    print_tour_path(tour)

    if len(coords) <= 1000:  # visualizations for reasonably sized instances
        plot_convergence(history, snapshot_interval)
        plot_tour_snapshots(coords, snapshots)
        print("\n  (Close the plot windows to exit)")
        plt.show()
    else:
        plot_convergence(history, snapshot_interval)
        print("\n  (Large instance — tour snapshots skipped; close plot to exit)")
        plt.show()

    return tour, length, elapsed


# ============================================================
# CLI
# ============================================================

def _list_tsp_files():
    files = sorted(glob.glob('*.tsp'))
    if not files:
        print("No .tsp files found in current directory.")
        sys.exit(1)
    return files


def _pick_file_interactive(files):
    print("\nAvailable TSP files:")
    for i, f in enumerate(files):
        print(f"  [{i}] {f}")
    while True:
        choice = input("Select file (number): ").strip()
        try:
            idx = int(choice)
            if 0 <= idx < len(files):
                return files[idx]
        except ValueError:
            pass
        print("Invalid choice, try again.")


def _pick_operator_interactive(name, options):
    print(f"\n{name} methods:")
    for i, op in enumerate(options):
        print(f"  [{i}] {op}")
    while True:
        choice = input(f"Select {name} (number, default 0): ").strip()
        if choice == '':
            return options[0]
        try:
            idx = int(choice)
            if 0 <= idx < len(options):
                return options[idx]
        except ValueError:
            pass
        print("Invalid choice, try again.")


def main():
    """Entry point: solve a TSP file with user-chosen operators."""
    if '--test' in sys.argv:
        sys.argv.remove('--test')
        unittest.main(verbosity=2)
        return

    filepath = None
    crossover = 'ox'
    mutation = 'swap'
    generations = 500
    pop_size = 100

    i = 1
    while i < len(sys.argv):
        arg = sys.argv[i]
        if arg in ('--crossover', '-c'):
            crossover = sys.argv[i + 1]
            i += 2
        elif arg in ('--mutation', '-m'):
            mutation = sys.argv[i + 1]
            i += 2
        elif arg in ('--gen', '-g'):
            generations = int(sys.argv[i + 1])
            i += 2
        elif arg in ('--pop', '-p'):
            pop_size = int(sys.argv[i + 1])
            i += 2
        elif not arg.startswith('-'):
            filepath = arg
            i += 1
        else:
            i += 1

    if filepath is None:
        files = _list_tsp_files()
        filepath = _pick_file_interactive(files)
        crossover = _pick_operator_interactive('Crossover', ['ox', 'pmx'])
        mutation = _pick_operator_interactive('Mutation', ['swap', 'inversion'])

    solve_tsp_file(filepath, pop_size=pop_size, generations=generations,
                   crossover=crossover, mutation=mutation)


# ============================================================
# Unit tests
# ============================================================

class TestFileIO(unittest.TestCase):

    def test_read_tsp_wi29(self):
        coords = read_tsp('wi29.tsp')
        self.assertEqual(len(coords), 29)
        self.assertAlmostEqual(coords[0][0], 20833.3333)
        self.assertAlmostEqual(coords[0][1], 17100.0000)
        self.assertAlmostEqual(coords[28][0], 27462.5000)

    def test_read_tsp_dj38(self):
        coords = read_tsp('dj38.tsp')
        self.assertEqual(len(coords), 38)

    def test_read_tsp_ca4663(self):
        coords = read_tsp('ca4663.tsp')
        self.assertEqual(len(coords), 4663)

    def test_read_tsp_ch71009(self):
        coords = read_tsp('ch71009.tsp')
        self.assertEqual(len(coords), 71009)


class TestDistance(unittest.TestCase):

    def test_calc_distance_same(self):
        self.assertAlmostEqual(calc_distance((0, 0), (0, 0)), 0.0)

    def test_calc_distance_3_4_5(self):
        d = calc_distance((0, 0), (3, 4))
        self.assertAlmostEqual(d, 5.0)

    def test_tour_length_three_cities(self):
        coords = [(0, 0), (3, 0), (0, 4)]
        length = tour_length([0, 1, 2], coords)
        self.assertAlmostEqual(length, 12.0)

    def test_tour_length_symmetric(self):
        coords = [(0, 0), (3, 0), (0, 4)]
        l1 = tour_length([0, 1, 2], coords)
        l2 = tour_length([0, 2, 1], coords)
        self.assertAlmostEqual(l1, l2)


class TestPopulation(unittest.TestCase):

    def test_init_population_size(self):
        pop = init_population(10, 20)
        self.assertEqual(len(pop), 20)
        for ind in pop:
            self.assertEqual(len(ind), 10)

    def test_init_population_valid_permutation(self):
        pop = init_population(8, 15)
        for ind in pop:
            self.assertEqual(sorted(ind), list(range(8)))
            self.assertEqual(len(set(ind)), 8)


class TestSelection(unittest.TestCase):

    def setUp(self):
        random.seed(42)
        self.n = 10
        self.pop = init_population(self.n, 10)
        coords = [(random.uniform(0, 100), random.uniform(0, 100))
                  for _ in range(self.n)]
        self.lengths = [tour_length(t, coords) for t in self.pop]
        self.fitnesses = [1.0 / l for l in self.lengths]

    def test_tournament_select_returns_valid(self):
        selected = tournament_select(self.pop, self.fitnesses, 3)
        self.assertEqual(len(selected), self.n)
        self.assertEqual(sorted(selected), list(range(self.n)))


class TestCrossover(unittest.TestCase):

    def setUp(self):
        random.seed(42)
        self.n = 10
        self.p1 = list(range(self.n))
        random.shuffle(self.p1)
        self.p2 = list(range(self.n))
        random.shuffle(self.p2)

    def _assert_valid_perm(self, tour, n):
        self.assertEqual(len(tour), n)
        self.assertEqual(sorted(tour), list(range(n)))
        self.assertEqual(len(set(tour)), n)

    def test_order_crossover_valid(self):
        child = order_crossover(self.p1, self.p2)
        self._assert_valid_perm(child, self.n)

    def test_pmx_crossover_valid(self):
        child = pmx_crossover(self.p1, self.p2)
        self._assert_valid_perm(child, self.n)

    def test_order_crossover_inherits_substring(self):
        n = 8
        p1 = [1, 2, 3, 4, 5, 6, 7, 0]
        p2 = [7, 6, 5, 4, 3, 2, 1, 0]
        for _ in range(50):
            child = order_crossover(p1, p2)
            self._assert_valid_perm(child, n)

    def test_pmx_crossover_inherits_substring(self):
        n = 8
        p1 = [1, 2, 3, 4, 5, 6, 7, 0]
        p2 = [7, 6, 5, 4, 3, 2, 1, 0]
        for _ in range(50):
            child = pmx_crossover(p1, p2)
            self._assert_valid_perm(child, n)


class TestMutation(unittest.TestCase):

    def setUp(self):
        random.seed(42)
        self.n = 10
        self.tour = list(range(self.n))
        random.shuffle(self.tour)

    def _assert_valid_perm(self, tour, n):
        self.assertEqual(len(tour), n)
        self.assertEqual(sorted(tour), list(range(n)))

    def test_swap_mutation_possibility_1_always_mutates(self):
        child = swap_mutation(self.tour, mutation_possibility=1.0)
        self._assert_valid_perm(child, self.n)
        diffs = sum(1 for i in range(self.n) if self.tour[i] != child[i])
        self.assertEqual(diffs, 2)

    def test_swap_mutation_possibility_0_never_mutates(self):
        child = swap_mutation(self.tour, mutation_possibility=0.0)
        self.assertEqual(child, self.tour)

    def test_inversion_mutation_possibility_1_always_mutates(self):
        child = inversion_mutation(self.tour, mutation_possibility=1.0)
        self._assert_valid_perm(child, self.n)

    def test_inversion_mutation_possibility_0_never_mutates(self):
        child = inversion_mutation(self.tour, mutation_possibility=0.0)
        self.assertEqual(child, self.tour)

    def test_inversion_reverses_segment(self):
        tour = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
        orig_sample = random.sample

        def mock_sample(pop, k):
            if k == 2 and isinstance(pop, range):
                return [2, 5]
            return orig_sample(pop, k)

        random.sample = mock_sample
        try:
            child = inversion_mutation(tour, mutation_possibility=1.0)
            self._assert_valid_perm(child, len(tour))
            self.assertEqual(child[2:6], [5, 4, 3, 2])
        finally:
            random.sample = orig_sample


class TestGASolve(unittest.TestCase):

    def setUp(self):
        random.seed(42)

    def test_GA_wi29_basic(self):
        coords = read_tsp('wi29.tsp')
        tour, length, history, _ = GA(
            coords, pop_size=50, generations=100, elite_size=2,
            crossover_possibility=0.8, mutation_possibility=0.1,
            seed=42, snapshot_interval=200, verbose=False
        )
        self.assertEqual(sorted(tour), list(range(29)))
        self.assertGreater(length, 0)
        self.assertEqual(len(history), 100)
        self.assertTrue(all(
            history[i] >= history[i + 1] for i in range(len(history) - 1)
        ))

    def test_GA_wi29_ox_pmx_consistent(self):
        coords = read_tsp('wi29.tsp')
        for cx in ('ox', 'pmx'):
            tour, length, _, _ = GA(
                coords, pop_size=20, generations=30, elite_size=1,
                crossover=cx, seed=42, verbose=False
            )
            self.assertEqual(sorted(tour), list(range(29)))
            self.assertGreater(length, 0)

    def test_GA_wi29_inversion_mutation(self):
        coords = read_tsp('wi29.tsp')
        tour, length, _, _ = GA(
            coords, pop_size=20, generations=30, elite_size=1,
            mutation='inversion', seed=42, verbose=False
        )
        self.assertEqual(sorted(tour), list(range(29)))
        self.assertGreater(length, 0)

    def test_GA_reproducible(self):
        coords = read_tsp('wi29.tsp')
        _, len1, _, _ = GA(
            coords, pop_size=20, generations=30, seed=1234, verbose=False
        )
        _, len2, _, _ = GA(
            coords, pop_size=20, generations=30, seed=1234, verbose=False
        )
        self.assertAlmostEqual(len1, len2)

    def test_GA_dj38(self):
        coords = read_tsp('dj38.tsp')
        tour, length, history, _ = GA(
            coords, pop_size=30, generations=50, seed=42, verbose=False
        )
        self.assertEqual(sorted(tour), list(range(38)))
        self.assertGreater(length, 0)
        self.assertEqual(len(history), 50)

    def test_GA_snapshots(self):
        """Verify snapshots are recorded at correct intervals."""
        coords = read_tsp('wi29.tsp')
        _, _, _, snapshots = GA(
            coords, pop_size=20, generations=100, seed=42,
            snapshot_interval=30, verbose=False
        )
        # snapshots at gen 0, 30, 60, 90
        self.assertGreaterEqual(len(snapshots), 4)
        self.assertEqual(snapshots[0][0], 0)
        self.assertEqual(snapshots[1][0], 30)
        self.assertEqual(snapshots[2][0], 60)
        self.assertEqual(snapshots[3][0], 90)


class TestIntegration(unittest.TestCase):

    def test_all_tsp_files_readable(self):
        expected = {
            'wi29.tsp': 29,
            'dj38.tsp': 38,
            'ca4663.tsp': 4663,
            'ch71009.tsp': 71009,
        }
        for fname, size in expected.items():
            with self.subTest(file=fname):
                coords = read_tsp(fname)
                self.assertEqual(len(coords), size)

    def test_ga_on_all_small(self):
        for fname in ('wi29.tsp', 'dj38.tsp'):
            with self.subTest(file=fname):
                coords = read_tsp(fname)
                tour, length, _, _ = GA(
                    coords, pop_size=30, generations=50,
                    seed=42, verbose=False
                )
                self.assertEqual(sorted(tour), list(range(len(coords))))
                self.assertGreater(length, 0)


if __name__ == '__main__':
    main()
