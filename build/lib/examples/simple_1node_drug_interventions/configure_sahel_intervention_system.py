from dtk.generic.climate import set_climate_constant
from dtk.utils.core.DTKConfigBuilder import DTKConfigBuilder
from dtk.vector.species import update_species_param, set_species_param


def standard_cb_updates(cb, years):

    cb.update_params({
        'Simulation_Duration' : 365*years,

        'x_Temporary_Larval_Habitat': 0.2,
        'Base_Population_Scale_Factor': 0.1,
    })

    cb.update_params({
        # Demographics
        'Birth_Rate_Dependence': 'FIXED_BIRTH_RATE',
        "Death_Rate_Dependence": "NONDISEASE_MORTALITY_BY_AGE_AND_GENDER",
        "Demographics_Filenames": ['single_node_demographics.json'],

        # Individual/Node Properties
        "Disable_IP_Whitelist": 1,
        "Enable_Vital_Dynamics": 1,
        "Enable_Birth": 1,
        'Enable_Default_Reporting': 1,

        # Misc
        'logLevel_default': 'ERROR',
        'Enable_Demographics_Other': 0
    })

    # Set climate
    set_climate_constant(cb)


def update_vector_params(cb):
    cb.update_params({"Vector_Species_Names": ['gambiae']})
    set_species_param(cb, 'gambiae', 'Larval_Habitat_Types',
                      {"LINEAR_SPLINE": {
                          "Capacity_Distribution_Per_Year": {
                              "Times": [0.0, 30.417, 60.833, 91.25, 121.667, 152.083,
                                        182.5, 212.917, 243.333, 273.75, 304.167, 334.583],
                              "Values": [3, 0.8, 1.25, 0.1, 2.7, 8, 4, 35, 6.8, 6.5, 2.6, 2.1]
                          },
                          "Max_Larval_Capacity": 1e9
                      }})
    set_species_param(cb, "gambiae", "Indoor_Feeding_Fraction", 0.9)
    set_species_param(cb, "gambiae", "Adult_Life_Expectancy", 20)


def configure_sahel_intervention_system(years=100):

    # General

    cb = DTKConfigBuilder.from_defaults('MALARIA_SIM')

    standard_cb_updates(cb, years)
    update_vector_params(cb)

    return cb