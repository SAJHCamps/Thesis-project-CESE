from EA_biplanar_graph_layout import Layout_Instance
import random as rd
from copy import deepcopy
import matplotlib.pyplot as plt
import pickle as pck
from datetime import datetime
import pathlib
import math
import itertools



class EA_Layout_Experiment:
    population_size = 1000
    offpsring_size = 100
    tournament_size = 4

    def __init__(self, rounds, constructor, saving, save_interval, save_path):
        self.population = [constructor() for _ in range(self.population_size)]
        self.max_rounds =  rounds
        self.saving = saving
        self.save_interval = save_interval
        self.save_path = save_path
        self.round = 0
        self.best = self.population[0]
        self.best_score = self.population[0].current_score
        self.average_scores = []
        self.best_scores = []
        self.evaluate_pop()
        self.selector_reproduction = self.tournament_selection
        self.elimnator = self.tournament_eliminator
        self.reproducor = self.crossover_reproducor
        
        return

    def evaluate_pop(self):
        best = min(self.population, key=lambda x: x.current_score)
        if best.current_score < self.best_score:
            self.best = deepcopy(best)
            self.best_score = self.best.current_score
        
        return
    
    def save_best(self):
        with open(self.save_path.joinpath(f"best_layout_round_{self.round}.pkl"), "bw") as file:
            pck.dump(self, file)
        return
    
    def small_BB_code():
        WIDTH = 3
        HEIGHT = 2

        A = [(0,0),(1,0),(2,0)]
        B = [(0,0),(1,1),(2,0)]

        pos_dict = {}

        for i in range(WIDTH):
            for j in range(HEIGHT):
                pos_dict[f"X({i},{j})"] = [rd.uniform(0,5),rd.uniform(0,5)]
                pos_dict[f"Z({i},{j})"] = [rd.uniform(0,5),rd.uniform(0,5)]
                pos_dict[f"L({i},{j})"] = [rd.uniform(0,5),rd.uniform(0,5)]
                pos_dict[f"R({i},{j})"] = [rd.uniform(0,5),rd.uniform(0,5)]
        
        edges_total = []

        for i in range(WIDTH):
            for j in range(HEIGHT):
                #A1
                edges_total.append((f"X({i},{j})",f"L({(i+A[0][0])%WIDTH},{(j+A[0][1])%HEIGHT})"))
                edges_total.append((f"Z({i},{j})",f"R({(i-A[0][0])%WIDTH},{(j-A[0][1])%HEIGHT})"))

                #A2
                edges_total.append((f"X({i},{j})",f"L({(i+A[1][0])%WIDTH},{(j+A[1][1])%HEIGHT})"))
                edges_total.append((f"Z({i},{j})",f"R({(i-A[1][0])%WIDTH},{(j-A[1][1])%HEIGHT})"))

                #A3
                edges_total.append((f"X({i},{j})",f"L({(i+A[2][0])%WIDTH},{(j+A[2][1])%HEIGHT})"))
                edges_total.append((f"Z({i},{j})",f"R({(i-A[2][0])%WIDTH},{(j-A[2][1])%HEIGHT})"))

                #B1
                edges_total.append((f"X({i},{j})",f"R({(i+B[0][0])%WIDTH},{(j+B[0][1])%HEIGHT})"))
                edges_total.append((f"Z({i},{j})",f"L({(i-B[0][0])%WIDTH},{(j-B[0][1])%HEIGHT})"))

                #B2
                edges_total.append((f"X({i},{j})",f"R({(i+B[1][0])%WIDTH},{(j+B[1][1])%HEIGHT})"))
                edges_total.append((f"Z({i},{j})",f"L({(i-B[1][0])%WIDTH},{(j-B[1][1])%HEIGHT})"))

                #B3
                edges_total.append((f"X({i},{j})",f"R({(i+B[2][0])%WIDTH},{(j+B[2][1])%HEIGHT})"))
                edges_total.append((f"Z({i},{j})",f"L({(i-B[2][0])%WIDTH},{(j-B[2][1])%HEIGHT})"))
        
        edges_top = []
        edges_bottom = []
        for edge in edges_total:
            if rd.randint(0,1) == 0:
                edges_top.append(edge)
            else:
                edges_bottom.append(edge)
        
        return Layout_Instance(pos_dict, edges_top, edges_bottom, {}, {})
    
    def small_BB_code_planar_fixed():
        WIDTH = 3
        HEIGHT = 2

        A = [(0,0),(1,0),(2,0)]
        B = [(0,0),(1,1),(2,0)]

        pos_dict = {}

        for i in range(WIDTH):
            for j in range(HEIGHT):
                pos_dict[f"X({i},{j})"] = [rd.uniform(0,5),rd.uniform(0,5)]
                pos_dict[f"Z({i},{j})"] = [rd.uniform(0,5),rd.uniform(0,5)]
                pos_dict[f"L({i},{j})"] = [rd.uniform(0,5),rd.uniform(0,5)]
                pos_dict[f"R({i},{j})"] = [rd.uniform(0,5),rd.uniform(0,5)]
        
        edges_top = []
        edges_bottom = []

        for i in range(WIDTH):
            for j in range(HEIGHT):
                #A1
                edges_top.append((f"X({i},{j})",f"L({(i+A[0][0])%WIDTH},{(j+A[0][1])%HEIGHT})"))
                edges_top.append((f"Z({i},{j})",f"R({(i-A[0][0])%WIDTH},{(j-A[0][1])%HEIGHT})"))

                #A2
                edges_bottom.append((f"X({i},{j})",f"L({(i+A[1][0])%WIDTH},{(j+A[1][1])%HEIGHT})"))
                edges_bottom.append((f"Z({i},{j})",f"R({(i-A[1][0])%WIDTH},{(j-A[1][1])%HEIGHT})"))

                #A3
                edges_bottom.append((f"X({i},{j})",f"L({(i+A[2][0])%WIDTH},{(j+A[2][1])%HEIGHT})"))
                edges_bottom.append((f"Z({i},{j})",f"R({(i-A[2][0])%WIDTH},{(j-A[2][1])%HEIGHT})"))

                #B1
                edges_top.append((f"X({i},{j})",f"R({(i+B[0][0])%WIDTH},{(j+B[0][1])%HEIGHT})"))
                edges_top.append((f"Z({i},{j})",f"L({(i-B[0][0])%WIDTH},{(j-B[0][1])%HEIGHT})"))

                #B2
                edges_top.append((f"X({i},{j})",f"R({(i+B[1][0])%WIDTH},{(j+B[1][1])%HEIGHT})"))
                edges_top.append((f"Z({i},{j})",f"L({(i-B[1][0])%WIDTH},{(j-B[1][1])%HEIGHT})"))

                #B3
                edges_bottom.append((f"X({i},{j})",f"R({(i+B[2][0])%WIDTH},{(j+B[2][1])%HEIGHT})"))
                edges_bottom.append((f"Z({i},{j})",f"L({(i-B[2][0])%WIDTH},{(j-B[2][1])%HEIGHT})"))
        
        return Layout_Instance(pos_dict, edges_top, edges_bottom, {}, {})
    
    def circle_code():
        POINTS = 7
        nodes = list(range(POINTS))
        pos_dict = {}
        rd.shuffle(nodes)

        for i, node in enumerate(nodes):
            pos_dict[node] = [math.cos(2*math.pi*i/len(nodes)), math.sin(2*math.pi*i/len(nodes))]
        
        top_edges = [(i,(i+1)%POINTS) for i in range(POINTS)]
        bottom_edges = [(i,(i+3)%POINTS) for i in range(POINTS)]

        return Layout_Instance(pos_dict, top_edges, bottom_edges, {}, {})

    def circle_code_random_pos():
        POINTS = 7
        nodes = list(range(POINTS))
        pos_dict = {}

        for i, node in enumerate(nodes):
            pos_dict[node] = [rd.uniform(0,5),rd.uniform(0,5)]
        
        top_edges = [(i,(i+1)%POINTS) for i in range(POINTS)]
        bottom_edges = [(i,(i+3)%POINTS) for i in range(POINTS)]

        return Layout_Instance(pos_dict, top_edges, bottom_edges, {}, {})

    def circle_code_random_pos_split():
        POINTS = 12
        nodes = list(range(POINTS))
        pos_dict = {}

        for node in nodes:
            pos_dict[node] = [rd.uniform(0,5),rd.uniform(0,5)]
        
        top_edges = []
        bottom_edges = []

        for i in range(POINTS):
            if rd.choice([True,False]):
                top_edges.append((i,(i+1)%POINTS))
            else:
                bottom_edges.append((i,(i+1)%POINTS))

            if rd.choice([True,False]):
                top_edges.append((i,(i+3)%POINTS))
            else:
                bottom_edges.append((i,(i+3)%POINTS))

        return Layout_Instance(pos_dict, top_edges, bottom_edges, {}, {})            

    def complete_graph_random_pos_split():
        POINTS = 8
        nodes = list(range(POINTS))
        pos_dict = {}

        for i, node in enumerate(nodes):
            pos_dict[node] = [rd.uniform(0,5),rd.uniform(0,5)]
        
        top_edges = []
        bottom_edges = []

        for edge in itertools.combinations(range(POINTS),2):
            if rd.choice([True,False]):
                top_edges.append(edge)
            else:
                bottom_edges.append(edge)

        return Layout_Instance(pos_dict, top_edges, bottom_edges, {}, {})
    
    def complete_graph_random_pos():
        POINTS = 9
        nodes = list(range(POINTS))
        pos_dict = {}

        for i, node in enumerate(nodes):
            pos_dict[node] = [rd.uniform(0,5),rd.uniform(0,5)]
        
        top_edges = [(0,1), (2,3), (1,2), (1,4), (1,5), (1,6), (1,7), (2,4), (2,5), (2,6), (2,7), (4,5), (5,6), (6,7)]
        bottom_edges = [(0,2), (1,3), (0,3), (0,4), (0,5), (0,6), (0,7), (3,4), (3,5), (3,6), (3,7), (5,7), (7,4), (4,6)]

        return Layout_Instance(pos_dict, top_edges, bottom_edges, {}, {})  

    def rank_selection(self, amount):
        self.population.sort(key= lambda x: x.current_score)
        return self.population[:amount]
    
    def random_selection(self, amount):
        return rd.sample(self.population, amount)
    
    def tournament_selection(self, amount):
        parents = []
        for _ in range(amount):
            tournament = rd.sample(self.population, self.tournament_size)
            tournament.sort(key= lambda x: x.current_score)
            parents.append(tournament[0])
        return parents

    def mutation_reproducor(self):
        parents = self.selector_reproduction(self.offpsring_size)

        for parent in parents:
            child = deepcopy(parent)
            child.mutate()
            self.population.append(child)
    
    def crossover_reproducor(self):
        parents = self.selector_reproduction(2*self.offpsring_size)

        for i in range(0, len(parents), 2):
            child = parents[i].crossover(parents[i+1])
            child.mutate()
            self.population.append(child)

    def tournament_eliminator(self):
        while len(self.population) > self.population_size:
            tournament = rd.sample(self.population, self.tournament_size)
            tournament.sort(key= lambda x: x.current_score)
            self.population.remove(tournament[-1])
        
    def rank_elimination(self):
        self.population.sort(key= lambda x: x.current_score)
        del self.population[self.population_size:]

    def run_round(self):
        if self.round >= self.max_rounds and self.max_rounds != -1:
            return
        
        self.reproducor()
        
        self.evaluate_pop()

        self.elimnator()


        self.best_scores.append(self.best_score)
        self.average_scores.append(sum([pop.current_score for pop in self.population])/len(self.population))

        self.round += 1
        return
    
    def run(self):
        fig, axes = plt.subplots(2, 2)
        self.plot_progress(axes)

        while(self.round < self.max_rounds or self.max_rounds == -1):
            print(f"Running round {self.round}")
            self.run_round()
            self.plot_progress(axes)

            if self.saving and self.round % self.save_interval == 0:
                self.save_best()
            
        self.best.plot()


    def plot_progress(self, axes=None):
        if type(axes) == type(None):
            fig, axes = plt.subplots(2, 2)
        
        axes[0,0].clear()
        axes[0,0].plot(self.best_scores, label= "Best scores")
        axes[0,0].plot(self.average_scores, label= "Average scores")
        axes[0,0].set_title("All generations")
        axes[0,0].legend()

        axes[0,1].clear()
        axes[0,1].set_title("Last 100 generations")
        axes[0,1].plot(self.best_scores[-100:], label= "Best scores")
        axes[0,1].plot(self.average_scores[-100:], label= "Average scores")
        axes[0,1].legend()

        axes[1,0].clear()
        axes[1,1].clear()
        self.best.plot(axes[1,0], axes[1,1])

        plt.show(block=False)
        plt.draw()
        plt.pause(1)


def main_experiment():
    path = input("Which experiment do you want to continue (empty for new)? ")
    if len(path) == 0:
        path = pathlib.Path(__file__).resolve().parent / (r"EA_layoutstest_run_" + datetime.now().strftime("%y-%m-%dT%H-%M-%S"))
        path.mkdir()
        experiment = EA_Layout_Experiment(1000, EA_Layout_Experiment.small_BB_code_planar_fixed, True, 100, path)
    else:
        file = open(path, "br")
        experiment  = pck.load(file)

    
    if len(input("Do you want to run it? ")) >0: 
        experiment.run()
    else:
        experiment.plot_progress()
        input("exit? ")

def main_plotting():
    plt.rcParams['text.usetex'] = True
    path = input("Which experiment do you want to continue (empty for new)? ")
    file = open(path, "br")
    experiment  = pck.load(file)

    fig, ax = plt.subplots()

    ax.plot(experiment.best_scores, label= "Best scores")
    ax.plot(experiment.average_scores, label= "Average scores")
    ax.set_yscale("symlog")
    ax.set_title("Scores for the smallest BB code")
    ax.legend()
    ax.grid()

    plt.show()

    experiment.best.plot()
    
        
if __name__ == "__main__":
    main_plotting()


