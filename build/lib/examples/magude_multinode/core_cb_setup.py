import pandas as pd
import numpy as np
import math
import os

from dtk.interventions.input_EIR import add_InputEIR
from dtk.utils.core.DTKConfigBuilder import DTKConfigBuilder
from dtk.vector.species import set_species_param
from malaria import infection, immunity, symptoms


def basic_gridded_config_builder(immunity_params="prashanth"):
    cb = DTKConfigBuilder.from_defaults('MALARIA_SIM')

    # Reduce StdOut size and prevent DTK from spitting out too many messages
    cb.update_params({
        "logLevel_default": "WARNING",
        "Enable_Log_Throttling": 1,
        "Memory_Usage_Warning_Threshold_Working_Set_MB": 50000,
        "Memory_Usage_Halting_Threshold_Working_Set_MB": 60000,
        "logLevel_JsonConfigurable": "WARNING",
        "Disable_IP_Whitelist": 1
    })

    cb.update_params(immunity.params)
    cb.update_params(infection.params)
    cb.update_params(symptoms.params)

    if immunity_params == 'prashanth':
        cb.update_params({
            'Antigen_Switch_Rate': pow(10, -9.116590124),
            'Base_Gametocyte_Production_Rate': 0.06150582,
            'Base_Gametocyte_Mosquito_Survival_Rate': 0.002011099,
            'Falciparum_MSP_Variants': 32,
            'Falciparum_Nonspecific_Types': 76,
            'Falciparum_PfEMP1_Variants': 1070,
            'Gametocyte_Stage_Survival_Rate': 0.588569307,
            'MSP1_Merozoite_Kill_Fraction': 0.511735322,
            'Max_Individual_Infections': 3,
            'Nonspecific_Antigenicity_Factor': 0.415111634
        })
    elif immunity_params == "jaline":
        cb.update_params({
            'Base_Gametocyte_Production_Rate': 0.044,
            "Gametocyte_Stage_Survival_Rate": 0.82,
            'Antigen_Switch_Rate': 2.96e-9,
            'Falciparum_PfEMP1_Variants': 1112,
            'Falciparum_MSP_Variants': 7,
            'MSP1_Merozoite_Kill_Fraction': 0.43,
            'Falciparum_Nonspecific_Types': 90,
            'Nonspecific_Antigenicity_Factor': 0.42,
            'Base_Gametocyte_Mosquito_Survival_Rate': 0.00088,
            "Max_Individual_Infections": 5
        })



    cb.update_params({
        "Climate_Model": "CLIMATE_CONSTANT",
        "Base_Air_Temperature": 27,
        "Base_Land_Temperature": 27,
        "Migration_Model": "NO_MIGRATION",
        "Enable_Immunity_Distribution": 0,
        "Enable_Immunity_Initialization_Distribution": 0,
        "Immunity_Initialization_Distribution_Type": "DISTRIBUTION_OFF"
    })

    cb.update_params({
        "Enable_Demographics_Other": 1,
        "Enable_Demographics_Builtin": 0,
        "Valid_Intervention_States": [],
        "Report_Detection_Threshold_PfHRP2": 40.0,
        "Report_Detection_Threshold_Blood_Smear_Parasites": 0,
        "Parasite_Smear_Sensitivity": 0.025,
        "Birth_Rate_Dependence": "FIXED_BIRTH_RATE", # Match demographics file for constant population size (with exponential age distribution)
        "Enable_Nondisease_Mortality": 1,
    })

    # Intervention events
    intervene_events_list = ["Bednet_Got_New_One","Bednet_Using","Bednet_Discarded"]

    cb.update_params({
        "Report_Event_Recorder": 0,
        "Report_Event_Recorder_Ignore_Events_In_List": 0,
        "Listed_Events": intervene_events_list,
        "Report_Event_Recorder_Events": intervene_events_list
    })


    # Basic entomology
    set_species_param(cb, 'arabiensis', 'Indoor_Feeding_Fraction', 0.5)
    set_species_param(cb, 'arabiensis', 'Adult_Life_Expectancy', 20)
    set_species_param(cb, 'arabiensis', 'Anthropophily', 0.65)

    set_species_param(cb, 'funestus', "Indoor_Feeding_Fraction", 0.9)
    set_species_param(cb, 'funestus', 'Adult_Life_Expectancy', 20)
    set_species_param(cb, 'funestus', 'Anthropophily', 0.65)

    return cb


def set_executable(cb, bin_folder):
    cb.set_experiment_executable(os.path.join(bin_folder, "Eradication.exe"))
    cb.set_dll_root(bin_folder)
