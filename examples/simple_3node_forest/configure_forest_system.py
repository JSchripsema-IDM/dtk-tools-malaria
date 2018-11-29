from dtk.utils.core.DTKConfigBuilder import DTKConfigBuilder
from dtk.vector.species import set_params_by_species, update_species_param
from dtk.interventions.property_change import change_individual_property_at_age
from dtk.interventions.migrate_to import add_migration_event
from dtk.interventions.outbreakindividual import recurring_outbreak
from simtools.Utilities.Experiments import retrieve_experiment
import os


def standard_cb_updates(cb, years, geog_name):

    cb.update_params({

        'Simulation_Duration' : 365*years,
        'x_Temporary_Larval_Habitat': 0.5,

        # Spatial output
        'Enable_Spatial_Output': 0,
        'Spatial_Output_Channels': ['Population', 'Prevalence', 'Adult_Vectors', 'Daily_Bites_Per_Human'],
    })

    cb.update_params({
        'Geography': geog_name,
        # Demographics
        'Birth_Rate_Dependence': 'FIXED_BIRTH_RATE',

        'Demographics_Filenames': ['%s_demographics_clean.json' % geog_name,
                                   '%s_demographics_overlay_v2.json' % geog_name],
        "Air_Temperature_Filename": '%s_air_temperature_daily.bin' % geog_name,
        "Land_Temperature_Filename": '%s_air_temperature_daily.bin' % geog_name,
        "Rainfall_Filename": '%s_rainfall_daily.bin' % geog_name,
        "Relative_Humidity_Filename": '%s_relative_humidity_daily.bin' % geog_name,

        # Migration
        'Migration_Model': 'FIXED_RATE_MIGRATION',
        'Enable_Local_Migration': 1,
        'Migration_Pattern': 'SINGLE_ROUND_TRIPS',
        'Local_Migration_Roundtrip_Duration': 5,
        'Local_Migration_Roundtrip_Probability': 0.95,
        'x_Local_Migration': 0.1, # 1 -> 46 trips per person per year

        'Local_Migration_Filename': '%s_Local_Migration.bin' % geog_name,

        # Individual/Node Properties
        "Disable_IP_Whitelist": 1,
        'Disable_NP_Whitelist': 1,
        'Enable_Property_Output': 1,

        # Misc
        'logLevel_VectorHabitat': 'WARNING',
        'logLevel_JsonConfigurable': 'WARNING',
        'logLevel_ReportUtilities': 'ERROR',
        'Enable_Demographics_Other': 0
    })


def update_vector_params(cb):

    set_params_by_species(cb.params, ['minimus', 'dirus'])
    update_species_param(cb, 'minimus', 'Larval_Habitat_Types', {'WATER_VEGETATION': 2e7}, overwrite=True)
    update_species_param(cb, 'minimus', 'Acquire_Modifier', 0.8, overwrite=False)
    update_species_param(cb, 'minimus', 'Adult_Life_Expectancy', 25, overwrite=False) # target: 12
    update_species_param(cb, 'dirus', 'Larval_Habitat_Types', {'CONSTANT': 1e7, 'TEMPORARY_RAINFALL' : 7e7}, overwrite=True)
    update_species_param(cb, 'dirus', 'Adult_Life_Expectancy', 30, overwrite=False) # target: 14
    update_species_param(cb, 'minimus', 'Anthropophily', 0.5, overwrite=False)
    update_species_param(cb, 'dirus', 'Anthropophily', 0.5, overwrite=False)

    capacity_dist_per_year = {
        "Times" : [0, 1, 245, 275, 364],
        "Values" : [0.2, 0.2, 0.7, 3, 3]
    }
    linear_spline = {"LINEAR_SPLINE": {
        "Capacity_Distribution_Number_Of_Years": 1,
        "Capacity_Distribution_Over_Time": capacity_dist_per_year,
                          "Max_Larval_Capacity": 3e7
                      }
                     }
    update_species_param(cb, 'minimus', 'Larval_Habitat_Types', linear_spline, overwrite=False)


def add_forest_migration(cb, start, years, forest, non_forest,
                         mig_type='one_season') :

    if mig_type == 'one_season' :
        months_of_mig = 5
    elif mig_type == 'planting' :
        months_of_mig = 1
        second_season_offset = 6
    else :
        print('Warning: Unrecognized migration type %s' % mig_type)
        return

    # add seasonal migration to forest nodes
    for node_id in forest:
        nodes_from = non_forest
        for year in range(years):

            add_migration_event(cb, nodeto=node_id,
                                duration_at_node_distr_type='GAUSSIAN_DURATION',
                                start_day=year*365 + start,
                                coverage=0.5,
                                duration_of_stay=30,
                                duration_of_stay_2=10,
                                duration_before_leaving_distr_type='GAUSSIAN_DURATION',
                                duration_before_leaving=3,
                                duration_before_leaving_2=0.75,
                                repetitions=4*months_of_mig,  # NORMALLY 5 months of migration (4*5)
                                tsteps_btwn=7,  # send a pulse every week
                                # target=target_ages,
                                nodesfrom={'class': 'NodeSetNodeList',
                                           'Node_List': nodes_from},
                                ind_property_restrictions=[{"ForestGoing": "LovesForest"}])
            if mig_type == 'planting' :
                add_migration_event(cb, nodeto=node_id,
                                    duration_at_node_distr_type='GAUSSIAN_DURATION',
                                    start_day=year * 365 + start + second_season_offset*30,  # start in august of each year + 6m for end of planting
                                    coverage=0.5,
                                    duration_of_stay=30,
                                    duration_of_stay_2=10,
                                    duration_before_leaving_distr_type='GAUSSIAN_DURATION',
                                    duration_before_leaving=3,
                                    duration_before_leaving_2=0.75,
                                    repetitions=4 * months_of_mig,  # 1 month of migration
                                    tsteps_btwn=7,  # send a pulse every week
                                    # target=target_ages,
                                    nodesfrom={'class': 'NodeSetNodeList',
                                               'Node_List': nodes_from},
                                    ind_property_restrictions=[{"ForestGoing": "LovesForest"}])
    return { 'Forest_Migration_Start_Day' : start}


def configure_forest_system(years=100, migration_start_day=91, migration_type='one_season') :

    # General
    village_nodes = [1, 2]
    forest_nodes = [3]
    geog_name = "Ratanikiri_3node"

    cb = DTKConfigBuilder.from_defaults('MALARIA_SIM')

    standard_cb_updates(cb, years, geog_name)
    update_vector_params(cb)

    # For the forest: add Individual Properties so only some people travel to forest nodes
    change_individual_property_at_age(cb, 'ForestGoing', 'LovesForest', coverage=0.7,
                                      change_age_in_days=15*365, revert=20*365)
    add_forest_migration(cb, migration_start_day, years, forest_nodes, village_nodes, mig_type=migration_type)
    recurring_outbreak(cb, start_day=(91 + 30), outbreak_fraction=0.2,
                       nodes={"class": "NodeSetNodeList", 'Node_List': forest_nodes})
    return cb


def set_up_input_paths(cb, exe_collection_id, dll_collection_id, input_collection_id, burnin_id='') :

    cb.set_exe_collection(exe_collection_id)
    cb.set_dll_collection(dll_collection_id)
    cb.set_input_collection(input_collection_id)

    if burnin_id :
        expt = retrieve_experiment(burnin_id)
        serialized_file_path = [sim.get_path() for sim in expt.simulations][0]

        cb.update_params( {
            'Serialized_Population_Path' : os.path.join(serialized_file_path, 'output'),
            'Serialized_Population_Filenames' : ['state-36500.dtk']
        })