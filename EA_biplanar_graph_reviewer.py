from EA_biplanar_graph_experiment import EA_Layout_Experiment
import pickle as pck
import matplotlib.pyplot as plt

if __name__ == "__main__":
    path = input("Which experiment do you want to check? ")
    file = open(path, "br")
    experiment  = pck.load(file)
    while (input("Continue?: ") != ""):
        eval(input("Command to execute (with experiment as variable name): "))
