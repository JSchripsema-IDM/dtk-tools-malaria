import logging
import os
import numpy as np
import calendar
from calibtool.analyzers.Helpers import garki_ento_data

from calibtool.study_sites.EntomologyCalibSite import EntomologyCalibSite
from calibtool.analyzers.ChannelBySeasonCohortAnalyzer import ChannelBySeasonCohortAnalyzer

logger = logging.getLogger(__name__)


class GarkiEntoCalibSite(EntomologyCalibSite):

    def __init__(self, vname, spec):

        self.metadata = {
            'village': vname.replace('_', ' '),
            'months': [calendar.month_abbr[i] for i in range(1, 13)],
            'species': [spec]
        }

        super(GarkiEntoCalibSite, self).__init__(vname.replace('_', ' '))

    def get_reference_data(self, reference_type):
        super(GarkiEntoCalibSite, self).get_reference_data(reference_type)

        # Load the Parasitology CSV
        dir_path = os.path.dirname(os.path.realpath(__file__))
        reference_csv = os.path.join(dir_path, 'inputs', 'GarkiDB_data', 'GarkiDBentomology_MBR.csv')
        reference_data = garki_ento_data(reference_csv, self.metadata)

        return reference_data

    def get_analyzers(self):
        return [ChannelBySeasonCohortAnalyzer(site=self, seasons=self.metadata['months'])]