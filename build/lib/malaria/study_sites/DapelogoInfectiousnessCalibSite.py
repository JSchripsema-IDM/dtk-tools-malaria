import logging
from collections import OrderedDict

import numpy as np
from calibtool.analyzers.Helpers import season_channel_age_density_infectiousness_json_to_pandas
from calibtool.study_sites.site_setup_functions import \
    config_setup_fn, survey_report_fn, summary_report_fn, add_treatment_fn, site_input_eir_fn

from calibtool.study_sites.InfectiousnessCalibSite import InfectiousnessCalibSite

logger = logging.getLogger(__name__)


class DapelogoInfectiousnessCalibSite(InfectiousnessCalibSite):
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

    # reference_dict = {'start_wet': {
    #                             'Infectiousness': [[[0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0],
    #                                                    [1, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0],
    #                                                    [1, 1, 0, 2, 0, 0], [0, 1, 0, 1, 0, 0],
    #                                                    [0, 0, 0, 1, 1, 0],
    #                                                    [0, 0, 0, 0, 0, 0]],
    #                                                   [[0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0],
    #                                                    [0, 0, 0, 0, 0, 0], [0, 0, 1, 0, 0, 0],
    #                                                    [0, 2, 1, 0, 1, 0], [1, 1, 3, 1, 0, 0],
    #                                                    [0, 0, 0, 0, 0, 0],
    #                                                    [0, 0, 0, 0, 0, 0]],
    #                                                   [[7, 5, 0, 0, 0, 0], [3, 0, 0, 0, 0, 0],
    #                                                    [2, 0, 0, 0, 0, 0], [2, 1, 0, 0, 0, 0],
    #                                                    [2, 1, 0, 0, 0, 0], [2, 2, 0, 0, 0, 0],
    #                                                    [0, 0, 0, 0, 0, 0],
    #                                                    [0, 0, 0, 0, 0, 0]]]
    #                           },
    #                     'peak_wet': {
    #                             'Infectiousness': [[[0, 0, 1, 0, 0, 0], [1, 0, 0, 0, 0, 0],
    #                                                                        [0, 0, 0, 0, 0, 0], [1, 1, 0, 0, 0, 0],
    #                                                                        [1, 0, 1, 0, 0, 0], [0, 0, 0, 2, 0, 0],
    #                                                                        [0, 0, 0, 0, 0, 0],
    #                                                                        [0, 0, 0, 0, 0, 0]],
    #                                                                       [[4, 0, 1, 0, 0, 0], [0, 0, 0, 0, 0, 0],
    #                                                                        [2, 0, 0, 0, 0, 0], [0, 0, 1, 0, 2, 1],
    #                                                                        [0, 0, 0, 0, 0, 0], [1, 0, 0, 0, 1, 1],
    #                                                                        [0, 0, 0, 0, 0, 0],
    #                                                                        [0, 0, 0, 0, 0, 0]],
    #                                                                       [[13, 1, 0, 0, 0, 0],
    #                                                                        [4, 0, 1, 0, 0, 0], [1, 0, 0, 0, 0, 0],
    #                                                                        [0, 0, 0, 0, 1, 0], [1, 0, 1, 0, 0, 0],
    #                                                                        [1, 0, 0, 1, 0, 0], [0, 0, 0, 0, 0, 0],
    #                                                                        [0, 0, 0, 0, 0, 0]]]
    #                           },
    #                     'end_wet': {
    #                            'Infectiousness': [[[2, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0],
    #                                                                        [1, 0, 0, 0, 0, 0], [1, 0, 0, 1, 0, 0],
    #                                                                        [1, 0, 0, 1, 0, 0], [0, 0, 0, 1, 0, 1],
    #                                                                        [0, 0, 1, 0, 0, 0],
    #                                                                        [0, 0, 0, 0, 0, 0]],
    #                                                                       [[2, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0],
    #                                                                        [1, 0, 0, 1, 0, 0], [3, 0, 0, 0, 0, 0],
    #                                                                        [2, 0, 2, 0, 0, 0], [1, 1, 0, 0, 0, 0],
    #                                                                        [1, 0, 0, 0, 0, 0],
    #                                                                        [0, 0, 0, 0, 0, 0]],
    #                                                                       [[13, 1, 0, 0, 0, 0],
    #                                                                        [2, 0, 0, 0, 0, 0], [1, 1, 0, 0, 0, 0],
    #                                                                        [3, 0, 0, 0, 0, 0], [4, 0, 0, 0, 0, 0],
    #                                                                        [0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0],
    #                                                                        [0, 0, 0, 0, 0, 0]]]
    #                           }
    #                     }


############# INFECTIOUSNESS WITH SMEARING #############
    reference_dict = {'start_wet': {
        'Smeared Infectiousness by smeared Gametocytemia and Age Bin': [[[0, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0],
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
            'Smeared Infectiousness by smeared Gametocytemia and Age Bin': [[[0, 0, 1, 0, 0, 0], [1, 0, 0, 0, 0, 0],
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
            'Smeared Infectiousness by smeared Gametocytemia and Age Bin': [[[2, 0, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0],
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
        super(DapelogoInfectiousnessCalibSite, self).get_reference_data(reference_type)

        reference_bins = OrderedDict([
            ('Age Bin', self.metadata['age_bins']),
            ('PfPR Bin', self.metadata['parasitemia_bins']),
            ('Infectiousness Bin', self.metadata['fraction_infected_bins'])
        ])
        reference_data = season_channel_age_density_infectiousness_json_to_pandas(self.reference_dict, reference_bins)

        return reference_data

    def get_setup_functions(self):
        setup_fns = super(DapelogoInfectiousnessCalibSite, self).get_setup_functions()
        setup_fns.append(config_setup_fn(duration=365 * 70))  # 60 years (with leap years)
        setup_fns.append(summary_report_fn(interval=365.0 / 12, description='Monthly_Report',
                                           parasitemia_bins=[0, 0.5, 5, 50, 500, 5000, 50000, 500000],
                                           infection_bins=[0, 5, 20, 50, 80, 100],
                                           age_bins=[5, 15, 100]))
        setup_fns.append(site_input_eir_fn(self.name, birth_cohort=True))
        setup_fns.append(lambda cb: cb.update_params({'Demographics_Filenames': [
            'Calibration\\birth_cohort_demographics.compiled.json'],
        'Antigen_Switch_Rate_LOG':-9.530186548,
        'Base_Gametocyte_Production_Rate':0.024177457,
        'Falciparum_MSP_Variants':6,
        'Falciparum_Nonspecific_Types':56,
        'Falciparum_PfEMP1_Variants':1473,
        'Gametocyte_Stage_Survival_Rate':0.667841154,
        'MSP1_Merozoite_Kill_Fraction':0.444193352,
        'Max_Individual_Infections':3,
        'Nonspecific_Antigenicity_Factor':0.262812768}))

        return setup_fns

    def __init__(self):
        super(DapelogoInfectiousnessCalibSite, self).__init__('Dapelogo')
