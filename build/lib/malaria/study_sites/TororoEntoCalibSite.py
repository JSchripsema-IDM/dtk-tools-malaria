import logging
import os
import numpy as np
import calendar
from calibtool.analyzers.Helpers import garki_ento_data

from calibtool.study_sites.EntomologyCalibSite import EntomologyCalibSite

logger = logging.getLogger(__name__)


class TororoEntoCalibSite(EntomologyCalibSite):

    def __init__(self, spec):

        self.metadata = {
            'village': 'Tororo',
            'months': [calendar.month_abbr[i] for i in range(1, 13)],
            'species': [spec]
        }

        super(GarkiEntoCalibSite, self).__init__('Tororo')

    def get_reference_data(self, reference_type):
        super(GarkiEntoCalibSite, self).get_reference_data(reference_type)

        # Load the Parasitology CSV
        dir_path = os.path.dirname(os.path.realpath(__file__))
        reference_csv = os.path.join(dir_path, 'inputs', 'Uganda', 'rough_entomology_Tororo_by_month.csv')
        reference_data = uganda_ento_data(reference_csv, self.metadata)

        return reference_data