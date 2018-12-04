import sys
from simtools.SetupParser import SetupParser
from simtools.ExperimentManager.ExperimentManagerFactory import ExperimentManagerFactory

from build_cb import build_project_cb
from interventions import add_all_interventions
from reports import add_all_reports

# Run parameters:
run_priority = "AboveNormal"
run_coreset = "emod_32cores"
experiment_name = "CoreMagude_Test"

if __name__ == '__main__':

    sys.path.insert(".")

    cb = build_project_cb()
    add_all_interventions(cb)
    add_all_reports(cb)


    # Start the simulation
    SetupParser.init()
    SetupParser.set("HPC", "priority", run_priority)
    SetupParser.set("HPC", "node_group", run_coreset)

    exp_manager = ExperimentManagerFactory.init()
    exp_manager.run_simulations(config_builder=cb, exp_name=experiment_name)