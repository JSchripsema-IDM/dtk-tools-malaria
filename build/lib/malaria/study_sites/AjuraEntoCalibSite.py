import logging
import os
import numpy as np
import calendar
from calibtool.analyzers.Helpers import garki_multi_year_ento_data

from calibtool.study_sites.EntomologyCalibSite import EntomologyCalibSite
from calibtool.analyzers.ChannelByMultiYearSeasonCohortAnalyzer import ChannelByMultiYearSeasonCohortAnalyzer

logger = logging.getLogger(__name__)


class AjuraEntoCalibSite(EntomologyCalibSite):

    def __init__(self, spec, **kwargs):

        self.metadata = {
            'village': 'Ajura',
            'months': [calendar.month_abbr[i] for i in range(1, 13)],
            'species': [spec]
        }
        if 'throwaway' in kwargs:
            self.throwaway = kwargs['throwaway']    # Include throwaway as kwarg
        self.duration = int(max(self.get_reference_data('entomology_by_season').reset_index()['Month']) / 12) + 1

        super(AjuraEntoCalibSite, self).__init__('Ajura')


    def get_reference_data(self, reference_type):
        super(AjuraEntoCalibSite, self).get_reference_data(reference_type)

        # Load the Parasitology CSV
        dir_path = os.path.dirname(os.path.realpath(__file__))
        reference_csv = os.path.join(dir_path, 'inputs', 'GarkiDB_data', 'GarkiDBentomology_MBR_multiyear.csv')
        reference_data = garki_multi_year_ento_data(reference_csv, self.metadata, time_limit=60)
        # self.duration = int(max(refernce_data.reset_index()['Month']) / 12) + 1

        return reference_data


    def get_analyzers(self):
        return [ChannelByMultiYearSeasonCohortAnalyzer(site=self, seasons=self.metadata['months'], duration=self.duration, throwaway=self.throwaway)]