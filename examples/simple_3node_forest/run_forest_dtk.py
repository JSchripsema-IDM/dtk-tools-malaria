from simtools.ExperimentManager.ExperimentManagerFactory import ExperimentManagerFactory
from simtools.SetupParser import SetupParser
from dtk.utils.reports.VectorReport import add_human_migration_report
from malaria.reports.MalariaReport import add_event_counter_report, add_filtered_spatial_report
from dtk.interventions.health_seeking import add_health_seeking
from dtk.utils.builders.sweep import GenericSweepBuilder

from configure_forest_system import configure_forest_system, set_up_input_paths

from simtools.Analysis.AnalyzeManager import AnalyzeManager
from analyze_migration import MigrationCountAnalyzer
from analyze_spatial_villages import SpatialAnalyzer


# General
exp_name = 'example_forest'
years = 1  # length of simulation, in years
num_seeds = 10

# Setup ----------------------------------------------------------------------------------------------------------
cb = configure_forest_system(years)

cb.update_params( {
    'Config_Name' : exp_name,
    # 'Serialization_Time_Steps' : [365*years]
})

burnin_id = "f7609a58-29f4-e811-a2bd-c4346bcb1555"
exe_collection_id = "520eaf08-cbf1-e811-a2bd-c4346bcb1555"
dll_collection_id = "844ed942-28f4-e811-a2bd-c4346bcb1555"
input_collection_id = "dc81f29a-e773-e811-a2c0-c4346bcb7275"

village_nodes = [1,2]
forest_nodes = [3]

analyzers = (SpatialAnalyzer(spatial_channels=['Prevalence', 'New_Infections']),
             MigrationCountAnalyzer(forest_nodeid=forest_nodes[0]))


set_up_input_paths(cb, exe_collection_id, dll_collection_id, input_collection_id, burnin_id)

# Add case management --------------------------------------------------------------------------------------------
add_health_seeking(cb, start_day=0,
                   drug=['Artemether', 'Lumefantrine'],
                   nodes={"class": "NodeSetNodeList", "Node_List": village_nodes},
                   targets=[
                       {'trigger': 'NewClinicalCase', 'coverage': 0.4, 'agemin': 0, 'agemax': 5, 'seek': 1,
                        'rate': 0.3},
                       {'trigger': 'NewClinicalCase', 'coverage': 0.2, 'agemin': 5, 'agemax': 100, 'seek': 1,
                        'rate': 0.3},
                       {'trigger': 'NewSevereCase', 'coverage': 0.5, 'agemin': 0, 'agemax': 100, 'seek': 1,
                        'rate': 0.3}]
                   )


# ---- CUSTOM REPORTS ----
add_filtered_spatial_report(cb, start=365*(years-1), end=365*years,
                            channels=['Population', 'Prevalence', 'Adult_Vectors', 'PfHRP2_Prevalence',
                                      'Daily_Bites_Per_Human', 'New_Infections', 'Daily_EIR'])
event_trigger_list=['Received_Treatment']
add_event_counter_report(cb, event_trigger_list=event_trigger_list)
add_human_migration_report(cb)


builder = GenericSweepBuilder.from_dict({'Run_Number': range(num_seeds)})


# Run args
run_sim_args = {'config_builder': cb,
                'exp_builder': builder,
                'exp_name': exp_name
                }

if __name__ == "__main__":

    SetupParser.default_block = 'HPC'

    SetupParser.init()
    exp_manager = ExperimentManagerFactory.init()
    exp_manager.run_simulations(**run_sim_args)
    # Wait for the simulations to be done
    exp_manager.wait_for_finished(verbose=True)
    assert (exp_manager.succeeded())

    am = AnalyzeManager(exp_manager.experiment)
    for a in analyzers:
        am.add_analyzer(a)
    am.analyze()

