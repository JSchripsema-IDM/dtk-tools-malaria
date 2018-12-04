import logging
import os
import numpy as np
import calendar
from calibtool.analyzers.Helpers import ento_data

from calibtool.study_sites.EntomologyCalibSite import EntomologyCalibSite
from calibtool.analyzers.ChannelBySeasonCohortAnalyzer import ChannelBySeasonCohortAnalyzer

logger = logging.getLogger(__name__)


class MagudeEntoCalibSite(EntomologyCalibSite):
    metadata = {
        'village': 'Magude',
        'months': [calendar.month_abbr[i] for i in range(1, 13)],
        'species': ['gambiae']
    }

    def get_reference_data(self, reference_type):
        super(MagudeEntoCalibSite, self).get_reference_data(reference_type)

        # Load the Parasitology CSV
        dir_path = os.path.dirname(os.path.realpath(__file__))
        reference_csv = os.path.join(dir_path, 'inputs', 'Mozambique_ento_data', 'mosquito_count_by_house_day.csv')
        reference_data = ento_data(reference_csv, self.metadata)

        return reference_data


    def get_analyzers(self):
        return [ChannelBySeasonCohortAnalyzer(site=self, seasons=self.metadata['months'])]


    def __init__(self):
        super(MagudeEntoCalibSite, self).__init__('Magude')
