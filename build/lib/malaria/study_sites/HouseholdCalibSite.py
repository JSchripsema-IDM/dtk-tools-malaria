import logging
from collections import OrderedDict
from abc import ABCMeta

import numpy as np
import pandas as pd
from calibtool.CalibSite import CalibSite
from calibtool.study_sites.site_setup_functions import *

from calibtool.analyzers.PrevalenceByRoundAnalyzer import PrevalenceByRoundAnalyzer
from calibtool.analyzers.PositiveFractionByDistanceAnalyzer import PositiveFractionByDistanceAnalyzer

logger = logging.getLogger(__name__)


class HouseholdCalibSite(CalibSite):

    __metaclass__ = ABCMeta

    metadata = {
        'rounddays': [],
        'distance_testday': 0,
        'msat_offset': 20,
        'msat_day': 165,
        'regions': [],
        'intervention_coverage_fname': '',
        'master_df_fname': '',
        'region_nodelist_fname': '',
        'distance_matrix_fname': '',
        'ignore_nodes': [],
        'burnin': 50,
        'sim_years': 2,
        'worknode_id': 10001,
        'numnodes': 0
    }

    reference_dict = {
        "risk_by_distance": {
            "prevalence": 0.0,
            "risks": [0, 0, 0],
            'distances': [0, 0.05, 0.2]
        },
        "prevalence_by_round": {
            "prev": [0] * 6,
            "round": [1, 2, 3, 4, 5, 6],
            "grid_cell": ['all'] * 6,
            'sim_date': [0] * 6
        }
    }

    def get_setup_functions(self):
        return [
            species_param_fn(species='arabiensis', param='Larval_Habitat_Types',
                             value={"TEMPORARY_RAINFALL": 1e10,
                                    "CONSTANT": 2e6
                                    }),
            species_param_fn(species="arabiensis", param="Indoor_Feeding_Fraction", value=0.5),
            species_param_fn(species='funestus', param='Larval_Habitat_Types',
                             value={"LINEAR_SPLINE": {
                                 "Capacity_Distribution_Per_Year": {
                                     "Times": [0.0, 30.417, 60.833, 91.25, 121.667, 152.083,
                                               182.5, 212.917, 243.333, 273.75, 304.167, 334.583],
                                     "Values": [0.2, 0.5, 1.5, 1.0,
                                                1.0, 1.0, 0.5, 0.5, 0.3, 0.2,
                                                0.1, 0.1]
                                 },
                                 "Max_Larval_Capacity": 3e10
                             },
                                 "CONSTANT": 2e6,
                                 "WATER_VEGETATION": 2e6}),
            update_params({
                "Geography": "Household",
                "Enable_Climate_Stochasticity": 0, # daily in raw data series
                'Enable_Nondisease_Mortality' : 1,
                "Vector_Sampling_Type": "TRACK_ALL_VECTORS",
                "Enable_Vector_Aging": 1,
                "Enable_Vector_Mortality": 1,
                "Birth_Rate_Dependence" : "FIXED_BIRTH_RATE",
                "Enable_Demographics_Other": 0,
                "Enable_Demographics_Initial": 1,
                "Enable_Vital_Dynamics" : 1,
                "Enable_Vector_Migration": 1,
                "Enable_Vector_Migration_Local": 1,
                "Enable_Vector_Migration_Regional" : 1,
                "Vector_Migration_Modifier_Equation" : "EXPONENTIAL",
                "x_Vector_Migration_Local" : 100,
                "x_Vector_Migration_Regional" : 0.1,
                "Vector_Migration_Habitat_Modifier": 3.8,
                "Vector_Migration_Food_Modifier" : 0,
                "Vector_Migration_Stay_Put_Modifier" : 10,
                "Enable_Spatial_Output" : 0,
                # "Spatial_Output_Channels" : ["Population", 'New_Diagnostic_Prevalence'],
                "Report_Detection_Threshold_Blood_Smear_Parasites": 40,
                "Allow_NodeID_Zero": 1,
                "Enable_Default_Reporting": 0,  # turn off inset chart
                "Disable_IP_Whitelist": 1,
                "Disable_NP_Whitelist": 1,
                "Vector_Species_Names" : ['arabiensis', 'funestus'],
                "logLevel_SimulationEventContext": "ERROR",
                "logLevel_VectorHabitat" : "ERROR",
                "logLevel_NodeVector" : "ERROR",
                "logLevel_JsonConfigurable" : "ERROR",
                "logLevel_MosquitoRelease" : "ERROR",
                "logLevel_VectorPopulationIndividual" : "ERROR",
                "logLevel_LarvalHabitatMultiplier" : "ERROR",
                "logLevel_StandardEventCoordinator" : "ERROR",
                'logLevel_NodeLevelHealthTriggeredIV' : 'ERROR',
                'logLevel_NodeEventContext' : 'ERROR',
                "Enable_Migration_Heterogeneity": 1,
                "Migration_Model": "FIXED_RATE_MIGRATION",
                "Migration_Pattern": "SINGLE_ROUND_TRIPS",
                "Enable_Local_Migration": 1,
                "Enable_Regional_Migration": 0,
                "Regional_Migration_Filename":"",
                "Local_Migration_Roundtrip_Duration"       : 3.0,
                "Local_Migration_Roundtrip_Probability"    : 1.0,
                "x_Local_Migration" : 0.1,
                "Enable_Sea_Migration": 1,
                "x_Sea_Migration" : 0.15,
                "Sea_Migration_Roundtrip_Duration"         : 30.0,
                "Sea_Migration_Roundtrip_Probability"      : 1.0
            })
        ]

    def get_worknode_setup_functions(self):
        return [
            add_treatment_fn(start=365 * (self.metadata['burnin'] - 5),
                             targets=[
                                 {'trigger': 'NewClinicalCase', 'coverage': 1, 'agemin': 15, 'agemax': 200, 'seek': 0.3,
                                  'rate': 0.3},
                                 {'trigger': 'NewClinicalCase', 'coverage': 1, 'agemin': 0, 'agemax': 15, 'seek': 0.45,
                                  'rate': 0.3},
                                 {'trigger': 'NewSevereCase', 'coverage': 1, 'seek': 0.8, 'rate': 0.5}],
                             drug_ineligibility_duration=14,
                             node_property_restrictions=[{'NodeType': 'Work'}]),
            add_drug_campaign_fn('MSAT', 'AL', [365 * (self.metadata['burnin'] + x) + self.metadata['rounddays'][0] for x in [0,1]],
                                 repetitions=3, interval=60, coverage=0.6, delay=self.metadata['msat_offset'],
                                 drug_ineligibility_duration=14, diagnostic_type='Other', diagnostic_threshold=40,
                                 node_property_restrictions=[{'NodeType' : 'Work'}]),

        ]


    def get_reference_data(self, reference_type):
        site_ref_type = ['prevalence_by_round', 'risk_by_distance']

        if reference_type not in site_ref_type:
            raise Exception("%s does not support %s reference_type, only %s.",
                            self.__class__.__name__, reference_type, site_ref_type.join(' and '))

        # if reference_type == 'prevalence_by_round' :
        #         return pd.DataFrame(self.reference_dict[reference_type])
        return self.reference_dict[reference_type]

    def get_region_list(self):
        return self.metadata['regions']

    def get_ignore_node_list(self):
        return self.metadata['ignore_nodes']

    def get_distance_matrix(self):
        try :
            return pd.read_csv(self.metadata['distance_matrix_fname'])
        except IOError :
            return None

    def get_analyzers(self):
        return [PrevalenceByRoundAnalyzer(site=self),
                PositiveFractionByDistanceAnalyzer(site=self, testday=self.metadata['distance_testday'])
                ]
