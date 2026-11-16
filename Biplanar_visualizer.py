import networkx as nx
import matplotlib.pyplot as plt
import numpy as np

from matplotlib.widgets import TextBox

#Constants
WIDTH = 3
HEIGHT = 2

A = [(0,0),(1,0),(2,0)]
B = [(0,0),(1,1),(2,0)]

#Initial layout taken from paper
plane_graph_1 = nx.Graph()
plane_graph_2 = nx.Graph()
pos_dict = {}
back_up_pos = None;

for i in range(WIDTH):
    for j in range(HEIGHT):
        plane_graph_1.add_nodes_from([f"L({i},{j})", f"R({i},{j})", f"X({i},{j})", f"Z({i},{j})"])
        plane_graph_2.add_nodes_from([f"L({i},{j})", f"R({i},{j})", f"X({i},{j})", f"Z({i},{j})"])
        pos_dict[f"X({i},{j})"] = (0+2*i,0+2*j)
        pos_dict[f"Z({i},{j})"] = (1+2*i,1+2*j)
        pos_dict[f"L({i},{j})"] = (0+2*i,1+2*j)
        pos_dict[f"R({i},{j})"] = (1+2*i,0+2*j)

back_up_pos = pos_dict.copy();

#Wheel A
for i in range(WIDTH):
    for j in range(HEIGHT):
        #A3
        plane_graph_1.add_edge(f"X({i},{j})",f"L({(i+A[2][0])%WIDTH},{(j+A[2][1])%HEIGHT})")
        plane_graph_1.add_edge(f"Z({i},{j})",f"R({(i-A[2][0])%WIDTH},{(j-A[2][1])%HEIGHT})")

        #A2
        plane_graph_1.add_edge(f"X({i},{j})",f"L({(i+A[1][0])%WIDTH},{(j+A[1][1])%HEIGHT})")
        plane_graph_1.add_edge(f"Z({i},{j})",f"R({(i-A[1][0])%WIDTH},{(j-A[1][1])%HEIGHT})")

        #B3
        plane_graph_1.add_edge(f"X({i},{j})",f"R({(i+B[2][0])%WIDTH},{(j+B[2][1])%HEIGHT})")
        plane_graph_1.add_edge(f"Z({i},{j})",f"L({(i-B[2][0])%WIDTH},{(j-B[2][1])%HEIGHT})")


#Wheel B
for i in range(WIDTH):
    for j in range(HEIGHT):
        #A1
        plane_graph_2.add_edge(f"X({i},{j})",f"L({(i+A[0][0])%WIDTH},{(j+A[0][1])%HEIGHT})")
        plane_graph_2.add_edge(f"Z({i},{j})",f"R({(i-A[0][0])%WIDTH},{(j-A[0][1])%HEIGHT})")

        #B2
        plane_graph_2.add_edge(f"X({i},{j})",f"R({(i+B[1][0])%WIDTH},{(j+B[1][1])%HEIGHT})")
        plane_graph_2.add_edge(f"Z({i},{j})",f"L({(i-B[1][0])%WIDTH},{(j-B[1][1])%HEIGHT})")

        #B1
        plane_graph_2.add_edge(f"X({i},{j})",f"R({(i+B[0][0])%WIDTH},{(j+B[0][1])%HEIGHT})")
        plane_graph_2.add_edge(f"Z({i},{j})",f"L({(i-B[0][0])%WIDTH},{(j-B[0][1])%HEIGHT})")

def submit(command: str):
    command = command.split(" ")
    
    if len(command) < 1:
        return
    match command[0]:
        case "move":
            if len(command) < 4:
                return
            
            pos_dict[command[1]] = (float(command[2]), float(command[3]))
        case "switch":
            if len(command) <3:
                return
            if command[1][0:5] == "inter" or command[2][0:5] == "inter":
                return

            
            if plane_graph_1.has_edge(command[1], command[2]):
                plane_graph_2.add_edge(command[1], command[2])
                plane_graph_1.remove_edge(command[1], command[2])
            elif plane_graph_2.has_edge(command[1], command[2]):
                plane_graph_1.add_edge(command[1], command[2])
                plane_graph_2.remove_edge(command[1], command[2])

        case "split":
            if len(command) < 3:
                return

            inter_x = (pos_dict[command[1]][0] + pos_dict[command[2]][0])/2
            inter_y = (pos_dict[command[1]][1] + pos_dict[command[2]][1])/2
            inter_name = "inter("+command[1]+","+command[2]+")"
            
            if plane_graph_1.has_edge(command[1], command[2]):
                pos_dict[inter_name] = (inter_x,inter_y)
                plane_graph_1.add_node(inter_name)
                plane_graph_1.add_edge(command[1], inter_name)
                plane_graph_1.add_edge(inter_name, command[2])
                plane_graph_1.remove_edge(command[1], command[2])
            elif plane_graph_2.has_edge(command[1], command[2]):
                pos_dict[inter_name] = (inter_x,inter_y)
                plane_graph_2.add_node(inter_name)
                plane_graph_2.add_edge(command[1], inter_name)
                plane_graph_2.add_edge(inter_name, command[2])
                plane_graph_2.remove_edge(command[1], command[2])
        
        case "merge":
            if len(command) < 2:
                return
            if command[1][0:5] != "inter":
                return

            if plane_graph_1.has_node(command[1]):
                neighbours = plane_graph_1.neighbors(command[1])
                plane_graph_1.add_edge(neighbours[0], neighbours[1])
                plane_graph_1.remove_node(command[1])

            elif plane_graph_2.has_node(command[1]):
                neighbours = list(plane_graph_2.neighbors(command[1]))
                plane_graph_2.add_edge(neighbours[0], neighbours[1])
                plane_graph_2.remove_node(command[1])
                
            

            

    axes[0].clear()
    axes[1].clear()
    nx.draw(plane_graph_1,pos_dict, axes[0], with_labels=True, arrows=True, connectionstyle="arc3, rad=0.2")
    nx.draw(plane_graph_2,pos_dict, axes[1], with_labels=True, arrows=True, connectionstyle="arc3, rad=0.2")
    plt.draw()
        

fig, axes = plt.subplots(1, 2)
nx.draw(plane_graph_1,pos_dict, axes[0], with_labels=True, arrows=True, connectionstyle="arc3, rad=0.2")
nx.draw(plane_graph_2,pos_dict, axes[1], with_labels=True, arrows=True, connectionstyle="arc3, rad=0.2")
axbox = fig.add_axes([0.1, 0.05, 0.8, 0.075])
text_box = TextBox(axbox, "", textalignment="center")
text_box.on_submit(submit)
text_box.set_val("move X(0,0) 0 0")  # Trigger `submit` with the initial string.

plt.show()

