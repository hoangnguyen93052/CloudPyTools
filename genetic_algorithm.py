import random
import numpy as np
import matplotlib.pyplot as plt

class Individual:
    def __init__(self, chromosome_length):
        self.chromosome = self.generate_chromosome(chromosome_length)
        self.fitness = self.evaluate_fitness()

    def generate_chromosome(self, length):
        return [random.randint(0, 1) for _ in range(length)]

    def evaluate_fitness(self):
        return sum(self.chromosome)

class GeneticAlgorithm:
    def __init__(self, population_size, chromosome_length, mutation_rate, generations):
        self.population_size = population_size
        self.chromosome_length = chromosome_length
        self.mutation_rate = mutation_rate
        self.generations = generations
        self.population = self.initialize_population()

    def initialize_population(self):
        return [Individual(self.chromosome_length) for _ in range(self.population_size)]

    def select_parents(self):
        total_fitness = sum(individual.fitness for individual in self.population)
        selection_probs = [individual.fitness / total_fitness for individual in self.population]
        return np.random.choice(self.population, size=2, p=selection_probs)

    def crossover(self, parent1, parent2):
        crossover_point = random.randint(1, self.chromosome_length - 1)
        child1_chromosome = parent1.chromosome[:crossover_point] + parent2.chromosome[crossover_point:]
        child2_chromosome = parent2.chromosome[:crossover_point] + parent1.chromosome[crossover_point:]
        return Individual(self.chromosome_length), Individual(self.chromosome_length)

    def mutate(self, individual):
        for index in range(self.chromosome_length):
            if random.random() < self.mutation_rate:
                individual.chromosome[index] = 1 - individual.chromosome[index]
        individual.fitness = individual.evaluate_fitness()

    def evolve(self):
        for generation in range(self.generations):
            new_population = []
            for _ in range(self.population_size // 2):
                parent1, parent2 = self.select_parents()
                child1, child2 = self.crossover(parent1, parent2)
                self.mutate(child1)
                self.mutate(child2)
                new_population.extend([child1, child2])
            self.population = new_population
            self.log_generation(generation)

    def log_generation(self, generation):
        best_fitness = max(individual.fitness for individual in self.population)
        print(f'Generation {generation}: Best Fitness = {best_fitness}')

    def get_best_individual(self):
        return max(self.population, key=lambda ind: ind.fitness)

def main():
    population_size = 100
    chromosome_length = 20
    mutation_rate = 0.01
    generations = 50

    ga = GeneticAlgorithm(population_size, chromosome_length, mutation_rate, generations)
    ga.evolve()
    
    best_individual = ga.get_best_individual()
    print(f'Best Individual: {best_individual.chromosome}, Best Fitness: {best_individual.fitness}')

    plot_results(ga)

def plot_results(ga):
    best_fitness_over_time = []

    for generation in range(ga.generations):
        best_fitness = max(individual.fitness for individual in ga.population)
        best_fitness_over_time.append(best_fitness)

    plt.plot(best_fitness_over_time)
    plt.xlabel('Generation')
    plt.ylabel('Best Fitness')
    plt.title('GA Optimization Progress')
    plt.show()

if __name__ == "__main__":
    main()