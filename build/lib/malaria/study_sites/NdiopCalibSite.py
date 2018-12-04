import logging

from malaria.study_sites.IncidenceCalibSite import IncidenceCalibSite
from malaria.study_sites.site_setup_functions import config_setup_fn, summary_report_fn, site_input_eir_fn, \
    add_treatment_fn

logger = logging.getLogger(__name__)

class update_params:
    def __init__(self, params):
        self.params = params

    def __call__(self, cb):
        return cb.update_params(self.params)

class NdiopCalibSite(IncidenceCalibSite):

    fine_age_bins = [
        0.08333, 0.5, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10,
        11, 12, 13, 14, 15, 20, 25, 30, 40, 50, 60, 100
    ]

    reference_dict = {

        # Digitized by K.McCarthy from data in:
        #   - Rogier et al. Parassitologia 1999
        #   - Trape et al. Am J Trop Med Hyg 1994
        #   - Rogier and Trape, Med Trop (Marseille) 1995
        # for K.McCarthy et al. Malaria Journal 2015, 14:6

        "Average Population by Age Bin": [
            31, 34, 31, 28, 28,
            21, 21, 21, 21, 21,
            15, 15, 15, 15, 15,
            62, 42, 42, 84, 39, 39, 50],
        "Age Bin": [
            1, 2, 3, 4, 5,
            6, 7, 8, 9, 10,
            11, 12, 13, 14, 15,
            20, 25, 30, 40, 50, 60, 100],
        "Annual Clinical Incidence by Age Bin": [
            1.9, 2.2, 2.6, 2.8, 2.9,
            3.0, 2.8, 2.7, 2.6, 2.6,
            2.5, 2.2, 2.1, 1.8, 1.5,
            1.0, 0.8, 0.6, 0.5, 0.4, 0.3, 0.4]
    }

    def get_setup_functions(self):
        setup_fns = super(NdiopCalibSite, self).get_setup_functions()
        setup_fns.append(config_setup_fn(duration=365 * 70 + 1))  # 60 years (with leap years)
        setup_fns.append(summary_report_fn(start=0, interval=365.0, age_bins=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 20, 25, 30, 40, 50, 60, 100]))
        setup_fns.append(site_input_eir_fn(self.name, birth_cohort=True))
        setup_fns.append(add_treatment_fn(start=0, drug=['Artemether'],
                                          targets=[{'trigger': 'NewClinicalCase',
                                                    'coverage': 1, 'seek': 0.5, 'rate': 0.3}]))
        setup_fns.append(update_params({'Demographics_Filenames': ['Calibration\\birth_cohort_demographics.compiled.json']}))

        return setup_fns

    def __init__(self):
        super(NdiopCalibSite, self).__init__('Ndiop')
