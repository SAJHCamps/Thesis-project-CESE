from EA_biplanar_graph_experiment import EA_Layout_Experiment
import pickle as pck
import matplotlib.pyplot as plt
from pathlib import Path

if __name__ == "__main__":
    path = input("Which experiments do you want to summarised? ")
    folder = Path(path)
    if not folder.is_dir():
        exit()
    
    for item in folder.iterdir():
        if "EA_layoutstest_run_" not in item.name:
            continue
        
        if not item.is_dir():
            continue
        
        for experiment_path in item.iterdir():
            experiment_file = open(experiment_path, "br")
            experiment:EA_Layout_Experiment  = pck.load(experiment_file)

            print(experiment.best_score)
            
            experiment_file.close()


