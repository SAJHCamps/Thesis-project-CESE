import networkx as nx
import matplotlib.pyplot as plt
import random as rd
from math import atan2, cos, sin
from copy import copy, deepcopy
import itertools as it

class Layout_Instance:
    crossing_penalty:float = 10
    too_long_penalty:float = 10
    too_long_size:float = 5
    too_closeby_penalty:float = 25
    too_closeby_size:float = 1
    intermediate_discouraging:float = 1
    mutation_rate_node_position:float = 1/250
    deviation_node_position:float = 1/2
    mutation_rate_split_edge:float = 1/250
    mutation_rate_merge_edge:float = 1/250
    mutation_rate_switch_plane:float = 1/250

    def __init__(self, vertices: dict[str,tuple[float,float]], edges_top: list[tuple[str,str]], edges_bottom: list[tuple[str,str]], intermediates_top: dict[tuple[str,str],dict[str,list[float]]], intermediates_bottom: dict[tuple[str,str],dict[str,list[float]]], intermediate_counter:int=0):
        self.vertices = vertices
        self.edges_top = edges_top
        self.edges_bottom = edges_bottom
        self.intermediates_top = intermediates_top
        self.intermediates_bottom = intermediates_bottom
        self.intermediate_counter = intermediate_counter
        self.current_score = self.score()
        return
    
    def plot(self, axe_graph_1=None, axe_graph_2=None):
        if axe_graph_1 == None or axe_graph_2 == None:
            fig, axes = plt.subplots(1, 2)
        else:
            axes = [axe_graph_1, axe_graph_2]
        
        plane_graph_top = nx.Graph()
        plane_graph_bottom = nx.Graph()

        plane_graph_top.add_nodes_from(list(self.vertices.keys()))
        plane_graph_bottom.add_nodes_from(list(self.vertices.keys()))

        nodes_positions_top = self.vertices.copy()
        nodes_positions_bottom = self.vertices.copy()

        for edge in self.edges_top:
            if edge in self.intermediates_top:
                intermediates = list(self.intermediates_top[edge].keys())
                intermediates.sort(key = lambda x: self.intermediates_top[edge][x][2])
                plane_graph_top.add_nodes_from(intermediates)

                for i in self.intermediates_top[edge].keys():
                    nodes_positions_top[i] = self.intermediates_top[edge][i][0:2]

                plane_graph_top.add_edge(edge[0], intermediates[0])
                plane_graph_top.add_edge(intermediates[-1], edge[1])
                for i in range(len(intermediates)-1):
                    plane_graph_top.add_edge(intermediates[i], intermediates[i+1])
            else:
                plane_graph_top.add_edge(*edge)

        for edge in self.edges_bottom:
            if edge in self.intermediates_bottom:
                intermediates = list(self.intermediates_bottom[edge].keys())
                intermediates.sort(key = lambda x: self.intermediates_bottom[edge][x][2])
                plane_graph_bottom.add_nodes_from(intermediates)

                for i in self.intermediates_bottom[edge].keys():
                    nodes_positions_bottom[i] = self.intermediates_bottom[edge][i][0:2]

                plane_graph_bottom.add_edge(edge[0], intermediates[0])
                plane_graph_bottom.add_edge(intermediates[-1], edge[1])
                for i in range(len(intermediates)-1):
                    plane_graph_bottom.add_edge(intermediates[i], intermediates[i+1])
            else:
                plane_graph_bottom.add_edge(*edge)

        nx.draw(plane_graph_top, nodes_positions_top, axes[0], with_labels=True, arrows=True)
        nx.draw(plane_graph_bottom, nodes_positions_bottom, axes[1], with_labels=True, arrows=True)
        axes[0].set_title(f"Top connections")
        axes[1].set_title(f"Bottom connections")
        for ax in axes:
            ax.set_axis_on()
            ax.tick_params(left=True, bottom=True, labelleft=True, labelbottom=True)
            ax.grid(True)
            ax.set_aspect("equal")

        if axe_graph_1 == None or axe_graph_2 == None:
            plt.suptitle(f"Layout with score: {self.score()}")
            plt.show()
        return
    
    def score_edge(self, edge_1: tuple[str,str], edge_2: tuple[str,str], intermediates_dict: dict[tuple[str,str],list[tuple[float,float]]]) -> float:
        sections_1 = []
        sections_2 = []

        if edge_1 in intermediates_dict.keys():
            intermediates_list = list(intermediates_dict[edge_1].values())
            intermediates_list.sort(key=lambda x: x[2])
            sections_1.append((self.vertices[edge_1[0]],intermediates_list[0][0:2]))
            for i in range(0,len(intermediates_list)-1):
                sections_1.append((intermediates_list[i][0:2], intermediates_list[i+1][0:2]))
            sections_1.append((intermediates_list[-1][0:2], self.vertices[edge_1[1]]))
        else:
            sections_1.append((self.vertices[edge_1[0]],self.vertices[edge_1[1]]))
        
        if edge_2 in intermediates_dict.keys():
            intermediates_list = list(intermediates_dict[edge_2].values())
            intermediates_list.sort(key=lambda x: x[2])
            sections_2.append((self.vertices[edge_2[0]],intermediates_list[0][0:2]))
            for i in range(0,len(intermediates_list)-1):
                sections_2.append((intermediates_list[i][0:2], intermediates_list[i+1][0:2]))
            sections_2.append((intermediates_list[-1][0:2], self.vertices[edge_2[1]]))
        else:
            sections_2.append((self.vertices[edge_2[0]],self.vertices[edge_2[1]]))

        crossings = []

        for i,section_1 in enumerate(sections_1):
            for j,section_2 in enumerate(sections_2):
                denominator = (section_1[0][0] - section_1[1][0])*(section_2[0][1] - section_2[1][1]) - (section_2[0][0] - section_2[1][0])*(section_1[0][1] - section_1[1][1])
                if denominator != 0:
                    t = ((section_1[0][0] - section_2[0][0])*(section_2[0][1] - section_2[1][1]) - (section_1[0][1] - section_2[0][1])*(section_2[0][0] - section_2[1][0]))/denominator
                    u = -((section_1[0][0] - section_1[1][0])*(section_1[0][1] - section_2[0][1]) - (section_1[0][1] - section_1[1][1])*(section_1[0][0] - section_2[0][0]))/denominator
                    if 0 <= t <= 1 and 0 <= u <= 1:
                        crossings.append([i,j,t,u])

        score = 0
        for i_crossing,j_crossing,t,u in crossings:
            before_half_1 = 0
            after_half_1 = 0

            for i in range(0,i_crossing):
                before_half_1 += ((sections_1[i][0][0] - sections_1[i][1][0])**2 + (sections_1[i][0][1] - sections_1[i][1][1])**2)**0.5
            
            length_corssing_section_1 = ((sections_1[i_crossing][0][0] - sections_1[i_crossing][1][0])**2 + (sections_1[i_crossing][0][1] - sections_1[i_crossing][1][1])**2)**0.5
            before_half_1 += t*length_corssing_section_1
            after_half_1 += (1-t)*length_corssing_section_1

            for i in range(i_crossing+1,len(sections_1)):
                after_half_1 += ((sections_1[i][0][0] - sections_1[i][1][0])**2 + (sections_1[i][0][1] - sections_1[i][1][1])**2)**0.5

            before_half_2 = 0
            after_half_2 = 0

            for i in range(0,j_crossing):
                before_half_2 += ((sections_2[i][0][0] - sections_2[i][1][0])**2 + (sections_2[i][0][1] - sections_2[i][1][1])**2)**0.5
            
            length_corssing_section_2 = ((sections_2[j_crossing][0][0] - sections_2[j_crossing][1][0])**2 + (sections_2[j_crossing][0][1] - sections_2[j_crossing][1][1])**2)**0.5
            before_half_2 += t*length_corssing_section_2
            after_half_2 += (1-t)*length_corssing_section_2

            for i in range(j_crossing+1,len(sections_2)):
                after_half_2 += ((sections_2[i][0][0] - sections_2[i][1][0])**2 + (sections_2[i][0][1] - sections_2[i][1][1])**2)**0.5

            penalty = self.crossing_penalty*(1-abs(0.5 - before_half_1/(before_half_1+after_half_1)) - abs(0.5 - before_half_2/(before_half_2+after_half_2)))
            if penalty > score:
                score = penalty
            

        return score

    def score(self) -> float:
        score = 0

        for edge in self.intermediates_top.keys():
            score += self.intermediate_discouraging*len(self.intermediates_top[edge])
        
        for edge in self.intermediates_bottom.keys():
            score += self.intermediate_discouraging*len(self.intermediates_bottom[edge])

        for i in self.vertices.keys():
            for j in self.vertices.keys():
                if i != j:
                    score += max(self.too_closeby_penalty*(self.too_closeby_size - ((self.vertices[i][0] - self.vertices[j][0])**2 + (self.vertices[i][1] - self.vertices[j][1])**2)**0.5) , 0)

        for edge in self.edges_top:
            length = 0
            if edge in self.intermediates_top:
                intermediates = list(self.intermediates_top[edge].values())
                intermediates.sort(key=lambda x: x[2])
                
                length += ((self.vertices[edge[0]][0] - intermediates[0][0])**2 + (self.vertices[edge[0]][1] - intermediates[0][1])**2)**0.5
                length += ((self.vertices[edge[0]][0] - intermediates[-1][0])**2 + (self.vertices[edge[0]][1] - intermediates[-1][1])**2)**0.5

                for i in range(len(intermediates)-1):
                    length += ((intermediates[i][0] - intermediates[i+1][0])**2 + (intermediates[i][1] - intermediates[i+1][1])**2)**0.5
                
            else:
                length = ((self.vertices[edge[0]][0] - self.vertices[edge[1]][0])**2 + (self.vertices[edge[0]][1] - self.vertices[edge[1]][1])**2)**0.5
            
            score += max(self.too_long_penalty*(length - self.too_long_size), 0)

        for edge in self.edges_bottom:
            length = 0
            if edge in self.intermediates_bottom:
                intermediates = list(self.intermediates_bottom[edge].values())
                intermediates.sort(key=lambda x: x[2])
                
                length += ((self.vertices[edge[0]][0] - intermediates[0][0])**2 + (self.vertices[edge[0]][1] - intermediates[0][1])**2)**0.5
                length += ((self.vertices[edge[0]][0] - intermediates[-1][0])**2 + (self.vertices[edge[0]][1] - intermediates[-1][1])**2)**0.5

                for i in range(len(intermediates)-1):
                    length += ((intermediates[i][0] - intermediates[i+1][0])**2 + (intermediates[i][1] - intermediates[i+1][1])**2)**0.5
            
            else:
                length =  ((self.vertices[edge[0]][0] - self.vertices[edge[1]][0])**2 + (self.vertices[edge[0]][1] - self.vertices[edge[1]][1])**2)**0.5
            
            score += max(self.too_long_penalty*(length - self.too_long_size), 0)
        
        
        
        for (edge_1,edge_2) in it.combinations(self.edges_top, 2):
            score += self.score_edge(edge_1, edge_2, self.intermediates_top)


        for (edge_1,edge_2) in it.combinations(self.edges_bottom, 2):
            score += self.score_edge(edge_1, edge_2, self.intermediates_bottom)


        return score
    
    def mutate(self):
        #position mutation
        for node in self.vertices.keys():
            if rd.random() < self.mutation_rate_node_position:
                self.vertices[node] = [self.vertices[node][i] + rd.gauss(0, self.deviation_node_position) for i in range(2)]
        
        for intermediate_edge in self.intermediates_top.keys():
            for intermediate_node in self.intermediates_top[intermediate_edge].keys():
                if rd.random() < self.mutation_rate_node_position:
                    self.intermediates_top[intermediate_edge][intermediate_node] = [self.intermediates_top[intermediate_edge][intermediate_node][0] + rd.gauss(0, self.deviation_node_position), \
                                                                                        self.intermediates_top[intermediate_edge][intermediate_node][1] + rd.gauss(0, self.deviation_node_position), \
                                                                                        self.intermediates_top[intermediate_edge][intermediate_node][2]]
        for intermediate_edge in self.intermediates_bottom.keys():
            for intermediate_node in self.intermediates_bottom[intermediate_edge].keys():
                if rd.random() < self.mutation_rate_node_position:
                    self.intermediates_bottom[intermediate_edge][intermediate_node] = [self.intermediates_bottom[intermediate_edge][intermediate_node][0] + rd.gauss(0, self.deviation_node_position), \
                                                                                        self.intermediates_bottom[intermediate_edge][intermediate_node][1] + rd.gauss(0, self.deviation_node_position), \
                                                                                        self.intermediates_bottom[intermediate_edge][intermediate_node][2]]

        #plane switch mutation
        # self.switch_mutation()
        
        #intermediates merging
        self.merge_mutation()
        
        #edge splitting
        self.split_mutation()
        
        self.current_score = self.score()
        return
    
    def merge_mutation(self):
        to_merge = []
        for edge in self.intermediates_top.keys():
            for node in self.intermediates_top[edge].keys():
                if rd.random() < self.mutation_rate_merge_edge:
                    to_merge.append([edge, node, True])

        for edge in self.intermediates_bottom.keys():
            for node in self.intermediates_bottom[edge].keys():
                if rd.random() < self.mutation_rate_merge_edge:
                    to_merge.append([edge, node, False])

        for entry in to_merge:
            edge = entry[0]
            node = entry[1]
            top_bool = entry[2]
            if top_bool:
                index = self.intermediates_top[edge][node][2]
                del self.intermediates_top[edge][node]
                for intermediate_node in self.intermediates_top[edge].keys():
                    if self.intermediates_top[edge][intermediate_node][2] > index:
                        self.intermediates_top[edge][intermediate_node][2] -= 1
                if len(self.intermediates_top[edge]) == 0:
                    del self.intermediates_top[edge]
            else:
                index = self.intermediates_bottom[edge][node][2]
                del self.intermediates_bottom[edge][node]
                for intermediate_node in self.intermediates_bottom[edge].keys():
                    if self.intermediates_bottom[edge][intermediate_node][2] > index:
                        self.intermediates_bottom[edge][intermediate_node][2] -= 1
                if len(self.intermediates_bottom[edge]) == 0:
                    del self.intermediates_bottom[edge]
        return

    def split_mutation(self):
        to_split = []
        for edge in self.edges_top:
            if rd.random() < self.mutation_rate_split_edge:
                to_split.append([edge, True])

        for edge in self.edges_bottom:
            if rd.random() < self.mutation_rate_split_edge:
                to_split.append([edge, False])

        for entry in to_split:
            edge = entry[0]
            top_bool = entry[1]
            split = rd.random()
            node_name = f"I{self.intermediate_counter}"
            self.intermediate_counter += 1
            if top_bool:
                if edge in self.intermediates_top:
                    start_vertex = None
                    end_vertex = None
                    index = rd.randint(0, len(self.intermediates_top[edge]))
                    if index == 0:
                        start_vertex = [self.vertices[edge[0]][0], self.vertices[edge[0]][1]]
                    else:
                        for vertex in self.intermediates_top[edge].keys():
                            if self.intermediates_top[edge][vertex][2] == index-1:
                                start_vertex = [self.intermediates_top[edge][vertex][0], self.intermediates_top[edge][vertex][1]]
                    
                    if index == len(self.intermediates_top[edge]):
                        end_vertex = [self.vertices[edge[1]][0], self.vertices[edge[1]][1]]
                    else:
                        for vertex in self.intermediates_top[edge].keys():
                            if self.intermediates_top[edge][vertex][2] == index:
                                end_vertex = [self.intermediates_top[edge][vertex][0], self.intermediates_top[edge][vertex][1]]

                    for vertex in self.intermediates_top[edge].keys():
                            if self.intermediates_top[edge][vertex][2] >= index:
                                self.intermediates_top[edge][vertex][2] += 1
                    
                    self.intermediates_top[edge][node_name] = [split*start_vertex[0] + (1-split)*end_vertex[0] + rd.gauss(0, self.deviation_node_position),\
                                                                split*start_vertex[1] + (1-split)*end_vertex[1] + rd.gauss(0, self.deviation_node_position), index]

                else:
                    self.intermediates_top[edge] = {node_name: [split*self.vertices[edge[0]][0] + (1-split)*self.vertices[edge[1]][0] + rd.gauss(0, self.deviation_node_position), \
                                                    split*self.vertices[edge[0]][1] + (1-split)*self.vertices[edge[1]][1] + rd.gauss(0, self.deviation_node_position), 0]}
            else:
                if edge in self.intermediates_bottom:
                    start_vertex = None
                    end_vertex = None
                    index = rd.randint(0, len(self.intermediates_bottom[edge]))
                    if index == 0:
                        start_vertex = [self.vertices[edge[0]][0], self.vertices[edge[0]][1]]
                    else:
                        for vertex in self.intermediates_bottom[edge].keys():
                            if self.intermediates_bottom[edge][vertex][2] == index-1:
                                start_vertex = [self.intermediates_bottom[edge][vertex][0], self.intermediates_bottom[edge][vertex][1]]
                    
                    if index == len(self.intermediates_bottom[edge]):
                        end_vertex = [self.vertices[edge[1]][0], self.vertices[edge[1]][1]]
                    else:
                        for vertex in self.intermediates_bottom[edge].keys():
                            if self.intermediates_bottom[edge][vertex][2] == index:
                                end_vertex = [self.intermediates_bottom[edge][vertex][0], self.intermediates_bottom[edge][vertex][1]]

                    for vertex in self.intermediates_bottom[edge].keys():
                            if self.intermediates_bottom[edge][vertex][2] >= index:
                                self.intermediates_bottom[edge][vertex][2] += 1
                    
                    self.intermediates_bottom[edge][node_name] = [split*start_vertex[0] + (1-split)*end_vertex[0] + rd.gauss(0, self.deviation_node_position),\
                                                                split*start_vertex[1] + (1-split)*end_vertex[1] + rd.gauss(0, self.deviation_node_position), index]

                else:
                    self.intermediates_bottom[edge] = {node_name: [split*self.vertices[edge[0]][0] + (1-split)*self.vertices[edge[1]][0] + rd.gauss(0, self.deviation_node_position), \
                                                    split*self.vertices[edge[0]][1] + (1-split)*self.vertices[edge[1]][1] + rd.gauss(0, self.deviation_node_position), 0]}
        return

    def switch_mutation(self):
        to_switch = []
        for edge in self.edges_top:
            if rd.random() < self.mutation_rate_switch_plane:
                to_switch.append(edge)

        for edge in self.edges_bottom:
            if rd.random() < self.mutation_rate_switch_plane:
                to_switch.append(edge)
        
        for edge in to_switch:
            if edge in self.edges_top:
                if edge in self.intermediates_top:
                    self.intermediates_bottom[edge] = self.intermediates_top[edge]
                    del self.intermediates_top[edge]
                
                self.edges_top.remove(edge)
                self.edges_bottom.append(edge)
            elif edge in self.edges_bottom:
                if edge in self.intermediates_bottom:
                    self.intermediates_top[edge] = self.intermediates_bottom[edge]
                    del self.intermediates_bottom[edge]
                
                self.edges_bottom.remove(edge)
                self.edges_top.append(edge)

    def centre(self):
        average_x = 0
        average_y = 0

        for vertex in self.vertices.keys():
            average_x += self.vertices[vertex][0]
            average_y += self.vertices[vertex][1]

        average_x = average_x/len(self.vertices)
        average_y = average_y/len(self.vertices)

        for vertex in self.vertices.keys():
            self.vertices[vertex] = (self.vertices[vertex][0] - average_x, self.vertices[vertex][1] - average_y)

        for intermediate_list in self.intermediates_bottom.values():
            for intermediate in intermediate_list.values():
                intermediate[0] -= average_x
                intermediate[1] -= average_y

        for intermediate_list in self.intermediates_top.values():
            for intermediate in intermediate_list.values():
                intermediate[0] -= average_x
                intermediate[1] -= average_y

        return

    def crossover(self, other: Layout_Instance):
        max_distance = 0
        max_distance_tuple = ()
        for vertex_tuple in it.combinations(self.vertices.keys(), 2):
            coordinates_vertex_1 = self.vertices[vertex_tuple[0]]
            coordinates_vertex_2 = self.vertices[vertex_tuple[1]]
            if (coordinates_vertex_1[0] - coordinates_vertex_2[0])**2 + (coordinates_vertex_1[1] - coordinates_vertex_2[1])**2 > max_distance:
                max_distance = (coordinates_vertex_1[0] - coordinates_vertex_2[0])**2 + (coordinates_vertex_1[1] - coordinates_vertex_2[1])**2
                max_distance_tuple = vertex_tuple

        rotation_shift_x = other.vertices[vertex_tuple[0]][0]
        rotation_shift_y = other.vertices[vertex_tuple[0]][1]
        for vextrex in other.vertices.keys():
            other.vertices[vextrex] = (other.vertices[vextrex][0] - rotation_shift_x, other.vertices[vextrex][1] - rotation_shift_y)

        angle_self = -atan2(self.vertices[max_distance_tuple[0]][1] - self.vertices[max_distance_tuple[1]][1], self.vertices[max_distance_tuple[0]][0] - self.vertices[max_distance_tuple[1]][0])
        angle_other = -atan2(other.vertices[max_distance_tuple[0]][1] - other.vertices[max_distance_tuple[1]][1], other.vertices[max_distance_tuple[0]][0] - other.vertices[max_distance_tuple[1]][0])
        rotation_angle = angle_self - angle_other

        for vertex in other.vertices.keys():
            new_x = self.vertices[vertex][0]*cos(rotation_angle)  - self.vertices[vertex][1]*sin(rotation_angle)
            new_y = self.vertices[vertex][0]*sin(rotation_angle)  + self.vertices[vertex][1]*cos(rotation_angle)
            self.vertices[vertex] = (new_x + rotation_shift_x, new_y + rotation_shift_y)

        self.centre()
        other.centre()

        selection_self = set([rd.choice(list(self.vertices.keys()))])
        connectivity_basis = rd.choice([self.edges_top, self.edges_bottom])
        neighbours = []
        for edge in connectivity_basis:
            if edge[0] in selection_self and edge[1] not in selection_self:
                neighbours.append(edge[1])
            if edge[1] in selection_self and edge[0] not in selection_self:
                neighbours.append(edge[0])

        while len(selection_self) < len(self.vertices.keys())/2:
            new_vertex = None
            if len(neighbours) > 0:
                new_vertex = rd.choice(neighbours)
                neighbours.remove(new_vertex)       
            else:
                new_vertex = rd.choice([vertex for vertex in self.vertices.keys() if vertex not in selection_self])

            selection_self.add(new_vertex)
            for edge in connectivity_basis:
                if edge[0] == new_vertex and edge[1] not in selection_self:
                    neighbours.append(edge[1])
                if edge[1] == new_vertex and edge[0] not in selection_self:
                    neighbours.append(edge[0])

        selection_other = [vertex for vertex in self.vertices.keys() if vertex not in selection_self]

        child_vertex_dict = {}
        for vertex in selection_self:
            child_vertex_dict[vertex] = deepcopy(self.vertices[vertex])
        
        for vertex in selection_other:
            child_vertex_dict[vertex] = deepcopy(other.vertices[vertex])

        child_top_edges = []
        child_intermediates_top = {}
        child_bottom_edges = []
        child_intermediates_bottom = {}

        all_edges = self.edges_top + self.edges_bottom

        for edge in all_edges:
            if edge[0] in selection_self and edge[1] in selection_self:
                if edge in self.edges_top:
                    if edge in self.intermediates_top:
                        child_intermediates_top[edge] = deepcopy(self.intermediates_top[edge])
                    child_top_edges.append(edge)
                else:
                    if edge in self.intermediates_bottom:
                        child_intermediates_bottom[edge] = deepcopy(self.intermediates_bottom[edge])
                    child_bottom_edges.append(edge)
            
            elif edge[0] in selection_other and edge[1] in selection_other:
                if edge in other.edges_top:
                    if edge in other.intermediates_top:
                        child_intermediates_top[edge] = deepcopy(other.intermediates_top[edge])
                    child_top_edges.append(edge)
                else:
                    if edge in other.intermediates_bottom:
                        child_intermediates_bottom[edge] = deepcopy(other.intermediates_bottom[edge])
                    child_bottom_edges.append(edge)

            else:
                if rd.randint(0, 1) == 0:
                    if edge in self.edges_top:
                        if edge in self.intermediates_top:
                            child_intermediates_top[edge] = deepcopy(self.intermediates_top[edge])
                        child_top_edges.append(edge)
                    else:
                        if edge in self.intermediates_bottom:
                            child_intermediates_bottom[edge] = deepcopy(self.intermediates_bottom[edge])
                        child_bottom_edges.append(edge)
                else:
                    if edge in other.edges_top:
                        if edge in other.intermediates_top:
                            child_intermediates_top[edge] = deepcopy(other.intermediates_top[edge])
                        child_top_edges.append(edge)
                    else:
                        if edge in other.intermediates_bottom:
                            child_intermediates_bottom[edge] = deepcopy(other.intermediates_bottom[edge])
                        child_bottom_edges.append(edge)
        
        return Layout_Instance(child_vertex_dict, child_top_edges, child_bottom_edges, child_intermediates_top, child_intermediates_bottom, max(self.intermediate_counter, other.intermediate_counter))


        
        
def main1():
    test_layout = Layout_Instance({"1":(0,0), "2":(1,0), "3":(0,1), "4":(1,1)}, [("1","2"), ("1","3")], [("2","4"), ("3","4")], {("1","2"): {"IS": [-0.5, 0.5, 0]}}, {})
    test_layout.plot()
    while(input("Continue? ") == ""):
        for _ in range(100):
            test_layout.mutate()
        test_layout.plot()
        
def main2():
    test_layout_1 = Layout_Instance({"1":(0,0), "2":(1,0), "3":(0,1), "4":(1,1)}, [("1","2"), ("1","3")], [("2","4"), ("3","4")], {("1","2"): {"IS": [-0.5, 0.5, 0]}}, {})
    test_layout_1.plot()
    test_layout_2 = Layout_Instance({"1":(0,0), "2":(2,0), "3":(0,2), "4":(2,2)}, [("1","2"), ("1","3")], [("2","4"), ("3","4")], {}, {})
    test_layout_2.plot()
    test_layout_3 = test_layout_1.crossover(test_layout_2)
    test_layout_3.plot()

def main3():
    test_layout = Layout_Instance({"1":(0,0), "2":(1,0), "3":(0,1), "4":(1,1)}, [("1","2"), ("1","3")], [("2","4"), ("3","4")], {("1","2"): {"IS": [-0.5, 0.5, 0]}}, {})
    while(True):
        test_layout.split_mutation()
        test_layout.split_mutation()
        test_layout.merge_mutation()
        test_layout.merge_mutation()

def test1():
    test_layout = Layout_Instance({"1":(0,0), "2":(1,0), "3":(0,1), "4":(1,1)}, [("1","2"), ("1","3")], [("2","4"), ("3","4")], {("1","2"): {"IS": [-0.5, 0.5, 0]}}, {})
    test_layout.crossing_penalty = 10
    test_layout.too_long_penalty = 0
    test_layout.too_long_size = 10
    test_layout.too_closeby_penalty = 0
    test_layout.too_closeby_size = 0
    test_layout.intermediate_discouraging = 0
    test_layout.plot()


if __name__ == "__main__":
    rd.seed(52)
    main2()
