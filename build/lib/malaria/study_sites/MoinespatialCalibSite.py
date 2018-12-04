import logging
import os
import numpy as np
import calendar
from calibtool.analyzers.Helpers import ento_spatial_data

from calibtool.study_sites.EntomologySpatialCalibSite import EntomologySpatialCalibSite
import glob

logger = logging.getLogger(__name__)

class update_params:
    def __init__(self, params):
        self.params = params

    def __call__(self, cb):
        return cb.update_params(self.params)


class MoineSpatialCalibSite(EntomologySpatialCalibSite):
    metadata = {
        'village': 'Magude',
        'hf': 'Moine',
        'months': [calendar.month_abbr[i] for i in range(1, 13)],
        'species': ['funestus']
    }

    def get_setup_functions(self):
        setup_fns = super(MoineSpatialCalibSite, self).get_setup_functions()

        specs = ['funestus']

        # setup_fns.append(vector_stats_report_fn())
        setup_fns.append(update_params(
            {
              'Antigen_Switch_Rate': pow(10, -9.116590124),
              'Base_Gametocyte_Production_Rate': 0.06150582,
              'Base_Gametocyte_Mosquito_Survival_Rate': 0.002011099,
              'Base_Population_Scale_Factor': 1,

              "Air_Temperature_Filename": "Mozambique_30arcsec_air_temperature_daily.bin",
              'Demographics_Filenames': ['Moine_demographics.json'],
              "Land_Temperature_Filename": "Mozambique_30arcsec_air_temperature_daily.bin",
              "Rainfall_Filename": "Mozambique_30arcsec_rainfall_daily.bin",
              "Relative_Humidity_Filename": "Mozambique_30arcsec_relative_humidity_daily.bin",
              "Enable_Climate_Stochasticity": 1,

              "Birth_Rate_Dependence": "FIXED_BIRTH_RATE",

              "Death_Rate_Dependence": "NONDISEASE_MORTALITY_BY_AGE_AND_GENDER",
              "Disable_IP_Whitelist": 1,

              "Enable_Vital_Dynamics": 1,
              "Enable_Birth": 1,
              'Enable_Default_Reporting': 0,
              'Enable_Demographics_Other': 1,
              # 'Enable_Property_Output': 1,

              'Falciparum_MSP_Variants': 32,
              'Falciparum_Nonspecific_Types': 76,
              'Falciparum_PfEMP1_Variants': 1070,
              'Gametocyte_Stage_Survival_Rate': 0.588569307,

              'Load_Balance_Filename':'Moine_loadbalance_24procs.bin',
            # "Vector_Migration_Filename_Local": os.path.join(geography, prefix + '_vector_migration.bin'),
              'Local_Migration_Filename': 'Moine_migration.bin',
              'Enable_Local_Migration': 0,
              'Migration_Pattern': 'NO_MIGRATION', # human migration
              # 'Local_Migration_Roundtrip_Duration': 2, # mean of exponential days-at-destination distribution
              # 'Local_Migration_Roundtrip_Probability': 0.95, # fraction that return

              'MSP1_Merozoite_Kill_Fraction': 0.511735322,
              'Max_Individual_Infections': 3,
              'Nonspecific_Antigenicity_Factor': 0.415111634,

              'x_Temporary_Larval_Habitat': 1,
              'logLevel_default': 'ERROR',

              "Vector_Species_Names": specs
             }))

        return setup_fns

    def get_reference_data(self, reference_type):
        super(MoineSpatialCalibSite, self).get_reference_data(reference_type)

        # Load the Parasitology CSV
        dir_path = os.path.dirname(os.path.realpath(__file__))
        reference_csv = os.path.join(dir_path, 'inputs', 'Mozambique_ento_data', 'mosquito_count_by_house_day.csv')
        hhs_hfs_csv = os.path.join(dir_path, 'inputs', 'Mozambique_ento_data', 'hh_by_health_facility.csv')
        hhs_csv = os.path.join(dir_path, 'inputs', 'Mozambique_ento_data', 'census_mda_households.csv')
        reference_data = ento_spatial_data(reference_csv, hhs_hfs_csv, hhs_csv, self.metadata)

        return reference_data

    def __init__(self):
        super(MoineSpatialCalibSite, self).__init__('Moine')
