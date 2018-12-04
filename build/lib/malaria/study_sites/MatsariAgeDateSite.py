import logging
import os
import numpy as np
import pandas as pd
import itertools
from calibtool.analyzers.Helpers import grouped_df_date
from collections import OrderedDict

from calibtool.study_sites.DensityCalibSite import DensityCalibSite

logger = logging.getLogger(__name__)

# Primary difference from CalibSites is the use of dates instead of seasons


class MatsariAgeDateSite(DensityCalibSite):
    metadata = {
        'parasitemia_bins': [0.0, 16.0, 70.0, 409.0, np.inf],  # (, 0] (0, 16] ... (409, inf]
        'age_bins': [0, 1, 4, 8, 18, 28, 43, np.inf],  # (, 1] (1, 4] ... (43, inf],
        'seasons': ['DC', 'DH', 'W'],
        'seasons_by_month': {
            'May': 'DH2',
            'September': 'W2',
            'January': 'DC2'
        },
        'village': 'Matsari',
        'end_date': '1971-12-31',
        'start_date': '1970-11-01'
    }

    def get_reference_data(self, reference_type):
        super(MatsariAgeDateSite, self).get_reference_data(reference_type)

        dir_path = os.path.dirname(os.path.realpath(__file__))
        reference_csv = os.path.join(dir_path, 'inputs', 'GarkiDB_data', 'GarkiDBparasitology_dates.csv')

        df = pd.read_csv(reference_csv)
        df = df.loc[df['Village'] == self.metadata['village']]

        pfprBinsDensity = self.metadata['parasitemia_bins']
        uL_per_field = 0.5 / 200.0  # from Garki PDF - page 111 - 0.5 uL per 200 views
        pfprBins = 1 - np.exp(-np.asarray(pfprBinsDensity) * uL_per_field)
        pfprdict = dict(zip(pfprBins, pfprBinsDensity))

        mask = (df['Date'] > self.metadata['start_date']) & (df['Date'] < self.metadata['end_date'])
        df = df.loc[mask]

        bins = OrderedDict([
            ('Date', list(df['Date'])),
            ('Age Bin', self.metadata['age_bins']),
            ('PfPR Bin', pfprBins)
        ])
        bin_tuples = list(itertools.product(*bins.values()))
        index = pd.MultiIndex.from_tuples(bin_tuples, names=bins.keys())

        df = df.rename(columns={'Age': 'Age Bin'})

        df2 = grouped_df_date(df, pfprdict, index, 'Parasitemia', 'Gametocytemia')
        df3 = grouped_df_date(df, pfprdict, index, 'Gametocytemia', 'Parasitemia')
        dfJoined = df2.join(df3).fillna(0)
        dfJoined = pd.concat([dfJoined['Gametocytemia'], dfJoined['Parasitemia']])
        dfJoined.name = 'Counts'
        dftemp = dfJoined.reset_index()
        dftemp['Channel'] = 'Smeared PfPR by Gametocytemia and Age Bin'
        dftemp.loc[len(dftemp)/2:, 'Channel'] = 'Smeared PfPR by Parasitemia and Age Bin'
        dftempsumlist = list(dftemp.groupby(['Channel', 'Date', 'Age Bin'])['Counts'].sum())
        dftemplist = [[s]*len(dftemp['PfPR Bin'].unique()) for s in dftempsumlist]
        dftemp['Counts_tot'] = [item for sublist in dftemplist for item in sublist]
        # dftemp = dftemp.join(dftemp.groupby(['Channel', 'Date', 'Age Bin'])['Counts'].sum(),
        #                      on=['Channel', 'Date', 'Age Bin'],
        #                      rsuffix='_tot', dtype=float)
        dftemp['Counts'] = dftemp.groupby(['Channel', 'Date', 'Age Bin'])['Counts'].apply(lambda x: x / float(x.sum()))
        dftemp = dftemp.set_index(['Channel', 'Date', 'Age Bin', 'PfPR Bin'])

        dftemp = dftemp.reset_index()
        dftemp['Date'] = pd.to_datetime(dftemp['Date']).dt.strftime('%b')
        temppop = dftemp.groupby(['Channel', 'Date', 'Age Bin', 'PfPR Bin'])['Counts_tot'].apply(np.sum)
        dftemp = dftemp.groupby(['Channel', 'Date', 'Age Bin', 'PfPR Bin'])['Counts'].apply(np.mean).reset_index()
        dftemp['Counts_tot'] = list(temppop)
        dftemp['Date'] = pd.to_datetime(dftemp['Date'].apply(lambda x: '1970-' + x + '-15')).dt.strftime('%j').astype(
            'int')
        dftemp = dftemp.sort_values(by=['Channel', 'Date'])
        reference = dftemp.set_index(['Channel', 'Date', 'Age Bin', 'PfPR Bin'])

        logger.debug('\n%s', dftemp)

        return reference

    def get_setup_functions(self):
        setup_fns = super(MatsariAgeDateSite, self).get_setup_functions()

        return setup_fns

    def __init__(self):
        super(MatsariAgeDateSite, self).__init__('Matsari')