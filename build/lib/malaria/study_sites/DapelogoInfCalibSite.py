import logging
from collections import OrderedDict

import numpy as np
from calibtool.analyzers.Helpers import season_channel_age_density_json_to_pandas
from calibtool.study_sites.site_setup_functions import \
    config_setup_fn, survey_report_fn, summary_report_fn, add_treatment_fn, site_input_eir_fn

from calibtool.study_sites.DensityCalibSite import DensityCalibSite

logger = logging.getLogger(__name__)


class DapelogoInfCalibSite(DensityCalibSite):
    metadata = {
        'fraction_infected_bins': [0, 5, 20, 50, 80, 100],
        'parasitemia_bins': [0, 0.5, 5, 50, 500, 5000, 50000, 500000],  # (, 0] (0, 50] ... (50000, ]
        'age_bins': [5, 15, np.inf],  # (, 5] (5, 15] (15, ]
        'seasons_by_month': {  # Collection dates from raw data in Ouedraogo et al. JID 2015
            'July': 'start_wet',  # 29 June - 30 July '07 => [180 - 211]
            'September': 'peak_wet',  # 3 Sept - 9 Oct '07 => [246 - 282]
            'January': 'end_wet'  # (a.k.a. DRY) 10 Jan - 2 Feb '08 => [10 - 33]
        }
    }

    reference_dict = {'start_wet': {
                                'infectiousness_by_age_and_season':
                                      [[2, 2, 0, 4, 1, 0], [1, 3, 5, 1, 1, 0], [18, 9, 0, 0, 0, 0]],
                                'density_and_infectiousness_by_age_and_season': [[[0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0],
                                                       [1, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0],
                                                       [1, 1, 0, 2, 0, 0], [0, 1, 0, 1, 0, 0],
                                                       [0, 0, 0, 1, 1, 0],
                                                       [0, 0, 0, 0, 0, 0]],
                                                      [[0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0],
                                                       [0, 0, 0, 0, 0, 0], [0, 0, 1, 0, 0, 0],
                                                       [0, 2, 1, 0, 1, 0], [1, 1, 3, 1, 0, 0],
                                                       [0, 0, 0, 0, 0, 0],
                                                       [0, 0, 0, 0, 0, 0]],
                                                      [[7, 5, 0, 0, 0, 0], [3, 0, 0, 0, 0, 0],
                                                       [2, 0, 0, 0, 0, 0], [2, 1, 0, 0, 0, 0],
                                                       [2, 1, 0, 0, 0, 0], [2, 2, 0, 0, 0, 0],
                                                       [0, 0, 0, 0, 0, 0],
                                                       [0, 0, 0, 0, 0, 0]]]
                              },
                        'peak_wet': {
                                'infectiousness_by_age_and_season':
                                      [[3, 1, 2, 2, 0, 0], [9, 0, 2, 0, 3, 0], [20, 1, 2, 1, 1, 0]],
                                'density_and_infectiousness_by_age_and_season': [[[0, 0, 1, 0, 0, 0], [1, 0, 0, 0, 0, 0],
                                                                           [0, 0, 0, 0, 0, 0], [1, 1, 0, 0, 0, 0],
                                                                           [1, 0, 1, 0, 0, 0], [0, 0, 0, 2, 0, 0],
                                                                           [0, 0, 0, 0, 0, 0],
                                                                           [0, 0, 0, 0, 0, 0]],
                                                                          [[4, 0, 1, 0, 0, 0], [0, 0, 0, 0, 0, 0],
                                                                           [2, 0, 0, 0, 0, 0], [0, 0, 1, 0, 2, 1],
                                                                           [0, 0, 0, 0, 0, 0], [1, 0, 0, 0, 1, 1],
                                                                           [0, 0, 0, 0, 0, 0],
                                                                           [0, 0, 0, 0, 0, 0]],
                                                                          [[13, 1, 0, 0, 0, 0],
                                                                           [4, 0, 1, 0, 0, 0], [1, 0, 0, 0, 0, 0],
                                                                           [0, 0, 0, 0, 1, 0], [1, 0, 1, 0, 0, 0],
                                                                           [1, 0, 0, 1, 0, 0], [0, 0, 0, 0, 0, 0],
                                                                           [0, 0, 0, 0, 0, 0]]]
                              },
                        'end_wet': {
                               'infectiousness_by_age_and_season':
                                      [[5, 0, 1, 3, 0, 0], [10, 1, 2, 1, 0, 0], [23, 2, 0, 0, 0, 0]],
                               'density_and_infectiousness_by_age_and_season': [[[2, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0],
                                                                           [1, 0, 0, 0, 0, 0], [1, 0, 0, 1, 0, 0],
                                                                           [1, 0, 0, 1, 0, 0], [0, 0, 0, 1, 0, 1],
                                                                           [0, 0, 1, 0, 0, 0],
                                                                           [0, 0, 0, 0, 0, 0]],
                                                                          [[2, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0],
                                                                           [1, 0, 0, 1, 0, 0], [3, 0, 0, 0, 0, 0],
                                                                           [2, 0, 2, 0, 0, 0], [1, 1, 0, 0, 0, 0],
                                                                           [1, 0, 0, 0, 0, 0],
                                                                           [0, 0, 0, 0, 0, 0]],
                                                                          [[13, 1, 0, 0, 0, 0],
                                                                           [2, 0, 0, 0, 0, 0], [1, 1, 0, 0, 0, 0],
                                                                           [3, 0, 0, 0, 0, 0], [4, 0, 0, 0, 0, 0],
                                                                           [0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0],
                                                                           [0, 0, 0, 0, 0, 0]]]
                              }
                        }

    def get_reference_data(self, reference_type):
        super(DapelogoInfCalibSite, self).get_reference_data(reference_type)

        reference_bins = OrderedDict([
            ('Age Bin', self.metadata['age_bins']),
            ('PfPR Bin', self.metadata['parasitemia_bins']),
            ('Percent Infected', self.metadata['fraction_infected_bins'])
        ])
        reference_data = season_channel_age_density_json_to_pandas(self.reference_dict, reference_bins)

        return reference_data

    def get_setup_functions(self):
        setup_fns = super(DapelogoInfCalibSite, self).get_setup_functions()
        setup_fns.append(config_setup_fn(duration=365 * 5))  # 60 years (with leap years)
        setup_fns.append(survey_report_fn(days=15, interval=1.0))
        setup_fns.append(summary_report_fn(interval=365.0 / 12, description='Monthly_Report',
                                           parasitemia_bins=[0, 50, 500, 5000, 50000, 5000000],
                                           age_bins=[5, 15, 100]))
        setup_fns.append(add_treatment_fn(start=0, drug=['Artemether'],
                                          targets=[{'trigger': 'NewClinicalCase',
                                                    'coverage': 1, 'seek': 0.15, 'rate': 0.3}]))
        setup_fns.append(site_input_eir_fn(self.name, birth_cohort=True))
        setup_fns.append(lambda cb: cb.update_params({'Demographics_Filenames': [
            'Calibration\\birth_cohort_demographics.compiled.json']}))

        return setup_fns

    def __init__(self):
        super(DapelogoInfCalibSite, self).__init__('Dapelogo')

