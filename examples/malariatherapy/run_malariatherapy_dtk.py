
#title: run_malariatherapy_dtk.py
#
#description: An example script for running malariatherapy challenge bite style infections where infection shapes
# are drawn using scalable transitions as decsribed in the Malaria 2.0 work. 
#
#author: Jon Russell
#
#date: 11/29/2018
#
#notes and dependencies: Uses a special config 'from-cfg.json' in the bin directory to use the updates immune model
#
#Institute for Disease Modeling, Bellevue, WA



import os
from dtk.utils.core.DTKConfigBuilder import DTKConfigBuilder
from dtk.generic.climate import set_climate_constant
from simtools.SetupParser import SetupParser
from simtools.ExperimentManager.ExperimentManagerFactory import ExperimentManagerFactory
from malaria.interventions.malaria_challenge import add_challenge_trial
from malaria.reports.MalariaReport import add_patient_report
from simtools.ModBuilder import  ModFn, ModBuilder
from immunity_transitions_configuration import set_transition_matrix


# General
working_dir =  r'C:/IDM/dtk-tools-malaria/examples/malariatherapy/'
exp_name = 'Malariatherapy_2pt0_infections'
years = 1  # length of simulation, in years
immunity_forcing_on = 1
config_path = os.path.join(working_dir, 'input/from-cfg.json')

# Setup ----------------------------------------------------------------------------------------------------------
cb = DTKConfigBuilder.from_files(config_path)
cb.update_params({'Vector_Species_Names' : [],
                  'Simulation_Duration' : 365*years,
                  'Demographics_Filenames' : ['Malariatherapy_demographics.json']
                  })
set_climate_constant(cb)

# Specify immune parameters --------------------------------------------------------------------------------------
if immunity_forcing_on == 1:

    #Pull the naive transitin matrix values from the config
    transition_matrix = cb.config['parameters']['Parasite_Peak_Density_Probabilities']
    #Sepcify the scaling of the transitio matrix to be applied (representing increasing immune pressure)
    scale_factor_array = [2,5,10,100]

    builder = ModBuilder.from_combos(
        [ModFn(set_transition_matrix, transition_matrix, scale_factor) for scale_factor in scale_factor_array]
    )
else:
    builder = ''

# Add source of infection (challenge bite or forced EIR) --------------------------------------------------------
add_challenge_trial(cb,start_day=0)

# ---- CUSTOM REPORTS ----
add_patient_report(cb)

# Run args
run_sim_args = {'config_builder': cb,
                'exp_name': exp_name,
                'exp_builder': builder
                }

if __name__ == "__main__":

    if not SetupParser.initialized:
        SetupParser.init('HPC')

    exp_manager = ExperimentManagerFactory.init()
    exp_manager.run_simulations(**run_sim_args)
    exp_manager.wait_for_finished(verbose=True)
    assert (exp_manager.succeeded())
