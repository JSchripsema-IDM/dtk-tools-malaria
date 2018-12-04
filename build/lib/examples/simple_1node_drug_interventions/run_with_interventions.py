from calibtool.study_sites.site_setup_functions import summary_report_fn
from dtk.utils.core.DTKConfigBuilder import DTKConfigBuilder
from malaria.interventions.malaria_drug_campaigns import add_drug_campaign
from simtools.ExperimentManager.ExperimentManagerFactory import ExperimentManagerFactory
from simtools.ModBuilder import ModBuilder, ModFn
from simtools.SetupParser import SetupParser
from examples.simple_1node_drug_interventions.configure_sahel_intervention_system import configure_sahel_intervention_system


def add_smc_group(cb, coverage=1.0, start_days=[60, 60+365], agemax=10, drug='DP'):
    '''
    This function sets up an SMC campaign for children under a certain age. Drug parameters can be changed to include or exclude gametocyte killing.
    :param cb: config builder
    :param coverage: coverage for SMC
    :param start_days: campaign start day
    :param agemax: children under this age will receive SMC drugs
    :param drug: type of drug to be used in SMC campaign
    :return: tags for SMC campaign
    '''

    add_drug_campaign(cb, 'SMC', drug, start_days=start_days, repetitions=3, interval=30,
    coverage=coverage,
    target_group={'agemin': 0, 'agemax': agemax})

    return {'Coverage': coverage, 'Start': start_days[0], 'Intervention_type': 'SMC%i' %agemax}


def add_summary_report(cb, start_day=0):
    '''
    Add daily summary report to output
    :param cb: config builder
    :param start_day: start day for report
    :return: None
    '''

    summary_report_fn(start=start_day+1, interval=1.0, description='Daily_Report',
                      age_bins=[5.0, 10.0, 100.0])(cb)

    return None


sim_duration = 1    # in years
num_seeds = 1

serialization_path = './input'

expname = 'single_node_example_with_interventions'


# Initialize and setup config builder
cb = configure_sahel_intervention_system(sim_duration)

cb.update_params({'Serialized_Population_Filenames': ['serialized_sahel.dtk'],
                  'Serialized_Population_Path': serialization_path
                  })

# Set up interventions
intervention_days = [180]
coverages = [0.6, 0.7, 0.8, 0.9, 1.0]

SMC = [
            [
               ModFn(DTKConfigBuilder.set_param, 'Run_Number', seed),
               ModFn(DTKConfigBuilder.set_param, 'Simulation_Duration', smc_start_day+365),
               ModFn(add_smc_group,
                         start_days=[smc_start_day],
                         coverage=smc_coverage, drug=drug, agemax=agemax),
               ModFn(add_summary_report, start_day=smc_start_day),
            ]
           for smc_start_day in intervention_days
           for smc_coverage in coverages
           for seed in range(num_seeds)
           for agemax in [5]
           for drug in ['DP']
        ]

builder = ModBuilder.from_list(SMC)

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
