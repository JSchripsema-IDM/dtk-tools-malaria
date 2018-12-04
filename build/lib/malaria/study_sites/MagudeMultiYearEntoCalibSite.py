import logging
import os
import numpy as np
import calendar
from calibtool.analyzers.Helpers import multi_year_ento_data, multi_year_ento_data_clustered

from calibtool.study_sites.EntomologyCalibSite import EntomologyCalibSite
from calibtool.analyzers.ChannelByMultiYearSeasonCohortAnalyzer import ChannelByMultiYearSeasonCohortAnalyzer

logger = logging.getLogger(__name__)


class MagudeMultiYearEntoCalibSite(EntomologyCalibSite):

    def __init__(self, spec, hfca=None, **kwargs):
        self.metadata = {
        'village': 'Magude',
        'months': [calendar.month_abbr[i] for i in range(1, 13)],
        'species': [spec],
        'HFCA': hfca,
         }
        if 'throwaway' in kwargs:
            self.throwaway = kwargs['throwaway']
        self.duration = int(max(self.get_reference_data('entomology_by_season').reset_index()['Month']) / 12) + 1
        super(MagudeMultiYearEntoCalibSite, self).__init__('Magude')


    def get_reference_data(self, reference_type):
        super(MagudeMultiYearEntoCalibSite, self).get_reference_data(reference_type)

        # Load the Parasitology CSV
        dir_path = os.path.dirname(os.path.realpath(__file__))
        if not self.metadata['HFCA']:
            reference_csv = os.path.join(dir_path, 'inputs', 'Mozambique_ento_data', 'mosquito_count_by_house_day.csv')
            reference_data = multi_year_ento_data(reference_csv, self.metadata)
        else:
            reference_csv = os.path.join(dir_path, 'inputs', 'Mozambique_ento_data', 'cluster_mosquito_counts_per_house_by_month.csv')
            reference_data = multi_year_ento_data_clustered(reference_csv, self.metadata)

        return reference_data


    def get_analyzers(self):
        return [
            ChannelByMultiYearSeasonCohortAnalyzer(site=self, seasons=self.metadata['months'], duration=self.duration,
                                                   throwaway=self.throwaway)]

