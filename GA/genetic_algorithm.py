import numpy as np
import random
import sys
import math

class genetic_algorithm:
    """
        This constructor method will 
    """
    def __init__(self, p, n, points,
                       selection = None,
                       selection_adjustments = None,
                       crossover = None,
                       mutation = None,
                       crossover_rate = 1,
                       mutation_rate = 0.05,
                       size = 100):
        self.p = p
        self.n = n
        self.points = points

        self.selection = selection
        self.selection_adjustments = selection_adjustments

        self.crossover = crossover
        self.crossover_rate = crossover_rate
        
        self.mutation = mutation
        self.mutation_rate = mutation_rate

        self.population = self.__init_population(size)
        self.population_size = size

    """
        This function will initialize the population pool.
        @param size(int): The size to specify the population pool

        @returns (np.shape(size, n)): 
                 The initial population pool, 
                 with 'size' number of chromosomes that are of length 'n'
    """
    def __init_population(self, size):

        #Get a np array of (size, n) for the pool
        initial_population = np.empty((size, self.n), dtype=np.int32)

        #For every location for a chromosome
        for chromosome in range(0, size):

            #Get 'p' city locations that specify the 'median' cities of a chromosome
            selected_cities = {}
            #While there are less than 'p' cities selected
            while (len(selected_cities) < self.p):
                #Get a random city
                random_city = random.randint(0, self.n-1)
                #Ensure that a city hasn't been selected yet
                while ((random_city in selected_cities)):
                    random_city = random.randint(0, self.n-1)

                #Keep track of the selected city
                selected_cities[random_city] = random_city

            #Finally initialize a chromosome
            for city in range(0, self.n):

                #If the city has been selected, put 1 in the chromosome to indicate that
                #it's been 'selected'. Else, put 0 in the chromosome.
                if (city in selected_cities):
                    initial_population[chromosome, city] = 1
                else:
                    initial_population[chromosome, city] = 0

        return initial_population
    
    """
        The actual fitness function for this genetic algorithm.
        For every vertex that is not selected(0s in the chromosome),
        the distance inbetween all selected vertices(1s in the chromosome) will be calculated, 
        which will the minimum distance to be returned.

        The fitness function will sum up the minimum distances inbetween all non-selected vertices and
        and the closest select vertices.

        @param chromosome(np.array((n))):
               The bitstring that represents selected(1) and non-selected(0) cities.
               NOTE: Each chromosome will be exactly 'p' 1s.

        @returns int:
                The sum of the minimum distances between all non-selected cities and the closest selected cities.
    """
    def fitness_function(self, chromosome):

        #Get the city indices that have been selected(where they are 1)
        selected_cities = np.where(chromosome == 1)[0]

        #Keep track of the total minimum distances
        total_distance = 0

        #For every city in a particular chromosome
        for city in range(0, len(chromosome)):

            #Skip over cities that have been selected
            if (city in selected_cities):
                continue

            #Keep track of the minimum distance
            min_distance = sys.maxsize

            #Scanning through the selected cities, and get the minimum distance
            #between a current city and the all of the selected cities in the chromosome
            for selected_city in selected_cities:
                curr_distance = self.__euclidean_distance(city, selected_city)
                if (curr_distance < min_distance):
                    min_distance = curr_distance

            total_distance += min_distance

        return total_distance

    def __euclidean_distance(self, curr_city, selected_city):
        x_term = (self.points[curr_city][0] - self.points[selected_city][0]) ** 2
        y_term = (self.points[curr_city][1] - self.points[selected_city][1]) ** 2
        return math.sqrt(x_term + y_term)
    
    """
        This is a helper function that will calculate the fitness for all of the 
        chromosomes in the population pool.

        @returns (dict)
                 This dictionary contains fitness-chromosome pairings, 
                 where the key is the raw fitness
                 and the value is the chromosome associated with the raw fitness.
    """
    def calculate_raw_fitness(self):
        fitness_to_chromosome = {}

        #For every possible chromosome in the population pool, get its fitness
        #based on the specifications of the p-median problem
        for chromosome_index in range(0, self.population_size):

            #Getting the raw fitness of the current chromosome
            raw_fitness = self.fitness_function(self.population[chromosome_index])
            
            #Store a fitness_chromosome pairing
            if (not (raw_fitness in fitness_to_chromosome)):
                fitness_to_chromosome[raw_fitness] = [self.population[chromosome_index]]
            else:
                fitness_to_chromosome[raw_fitness].append(self.population[chromosome_index])
        
        #Return 'fitness_to_chromosome' pairings, which will be sorted from greatest fitness to least fitness
        return dict(sorted(fitness_to_chromosome.items(), reverse=True))

    
    
    def __get_elite_chromosomes(self, adjusted_fitness):

        #Getting the two best fittest values from the adjusted fitness pool
        #(Should be the last two entries since the pool is sorted)
        best_fitness = list(adjusted_fitness.keys())[len(adjusted_fitness)-1]
        next_best_fitness = list(adjusted_fitness.keys())[len(adjusted_fitness)-2]

        #Return the best chromosomes from the adjusted fitness pool
        return (
            adjusted_fitness[best_fitness],
            adjusted_fitness[next_best_fitness]
        )

    def __fixup_chromosome(self, child):
        while (np.sum(child) > self.p):
            selected_cities = np.where(child == 1)[0]
            max_fitness = -sys.maxsize - 1 
            for selected_city_index in selected_cities:
                shorter_child = child.copy()
                shorter_child[selected_city_index] = 0
                shorter_fitness = self.fitness_function(shorter_child)

                print(selected_city_index)
            print()

        while (np.sum(child) < self.p):
            print()
        print(np.sum(child) > self.p)
        print(np.sum(child) < self.p)

        print()

    def run_algorithm(self, iterations = 1):

        for iteration in range(0, iterations):

            adjusted_fitness = self.selection_adjustments(
                self.calculate_raw_fitness(),
                self.population_size
            )
            new_population_pool = np.array((self.population_size, self.n), dtype=np.int32)

            for pop_index in range(0, int(self.population_size/2)):

                child1 = np.empty((self.n), dtype=np.int32)
                child2 = np.empty((self.n), dtype=np.int32)

                #At the beginning of a new generation, copy over the best 
                #chromosomes from the last generation.
                if (pop_index == 0):
                    (child1, child2) = self.__get_elite_chromosomes(adjusted_fitness)
                else:

                    #Select two chromosomes from the pool
                    (parent1, parent2) = self.selection(adjusted_fitness)

                    #Crossover the selected chromosomes
                    if (random.uniform(0, 1) < self.crossover_rate):
                        (child1, child2) = self.crossover(parent1, parent2)
                    else:
                        (child1, child2) = (parent1, parent2)
                    
                    #Fixup the chromosomes(i.e they do not have exactly 'p' 1 bits)
                    self.__fixup_chromosome(child1)
                    self.__fixup_chromosome(child2)
                print()