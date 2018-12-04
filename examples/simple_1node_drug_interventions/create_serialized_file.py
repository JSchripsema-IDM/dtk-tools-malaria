from dtk.utils.builders.sweep import GenericSweepBuilder
from simtools.ExperimentManager.ExperimentManagerFactory import ExperimentManagerFactory
from simtools.ModBuilder import ModBuilder, ModFn
from simtools.SetupParser import SetupParser
from examples.simple_1node_drug_interventions.configure_sahel_intervention_system import configure_sahel_intervention_system
from dtk.generic.serialization import add_SerializationTimesteps

sim_duration = 1    # in years
num_seeds = 1

serialization_path = './input'

expname = 'single_node_example_with_interventions_serialized_file'


# Initialize and setup config builder
cb = configure_sahel_intervention_system(sim_duration)

builder = GenericSweepBuilder.from_dict({'Run_Number': range(1)})
add_SerializationTimesteps(cb, [60*365], end_at_final=True)

run_sim_args = {'config_builder': cb,
                'exp_name': expname,
                'exp_builder': builder}


if __name__ == "__main__":

    SetupParser.default_block = 'HPC'

    SetupParser.init()
    exp_manager = ExperimentManagerFactory.init()
    exp_manager.run_simulations(**run_sim_args)
    # Wait for the simulations to be done
    exp_manager.wait_for_finished(verbose=True)
    assert (exp_manager.succeeded())
