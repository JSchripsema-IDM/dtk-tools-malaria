import logging
import os
import numpy as np
import pandas as pd
import itertools
from calibtool.analyzers.Helpers import grouped_df_date
from collections import OrderedDict

logger = logging.getLogger(__name__)


class GarkiSites(object):

    def __init__(self, vname):
        #
        # self.metadata = {
        #         'parasitemia_bins': [0, 50, 500, 5000, 50000, np.inf],  # (, 0] (0, 50] ... (50000, ]
        #         'age_bins': [0, 5, 15, np.inf],  # (, 5] (5, 15] (15, ],
        #         'start_date': '1970-11-01',
        #         'end_date': '1971-12-31',
        #         'village': [vname]
        #     }
        self.metadata = {'fields_positive': [0, 0.04, 0.16, 0.64, 1 - 1e-16],
                         'parasitemia_bins': [0.0, 16.0, 70.0, 409.0, 4000000.0],
                         'age_bins': [0, 1, 4, 8, 18, 28, 43, np.inf], 'seasons': ['DC', 'DH', 'W'],
                         'end_date': '1971-12-31', 'start_date': '1970-11-01', 'village': [vname.replace('_', ' ')]}

        # fields_positive = self.metadata['fields_positive']
        # uL_per_field = 0.5 / 200.0  # from Garki PDF - page 111 - 0.5 uL per 200 views
        # pfprBinsDensity = abs(np.log(1 - np.asarray(fields_positive))) / uL_per_field
        # self.metadata['parasitemia_bins'] = list(pfprBinsDensity)

        dir_path = os.path.dirname(os.path.realpath(__file__))
        self.reference_csv = os.path.join(dir_path, 'inputs', 'GarkiDB_data', 'GarkiDBparasitology_dates.csv')

    def get_reference_data(self):
        """
        A function to convert Garki reference data locally stored in a csv file generate by code:

        https://github.com/pselvaraj87/Malaria-GarkiDB

        The data in the csv file is stored as:

          1          Patient_id  Village      Date       Age     Age Bins      Parasitemia  Gametocytemia
          2 0           4464     Batakashi      1970-11-01  0.00547945205479  1.0          0.0               0.0
          3 1           2230     Ajura          1970-11-01  0.0493150684932   1.0          0.005             0.0
          4 2           6995     Rafin Marke    1970-11-01  0.0821917808219   1.0          0.0               0.0
          5 3           5407     Ungwar Balco   1970-11-01  0.120547945205    1.0          0.0               0.0
          6 4           4988     Ungwar Balco   1970-11-01  0.104109589041    1.0          0.005             0.0
          7 5           9282     Kargo Kudu     1970-11-01  0.145205479452    1.0          0.0075            0.0
          8 6           2211     Ajura          1970-11-01  0.134246575342    1.0          0.0               0.0
          ...
          ...

        to a Pandas dataframe with Multi Index:

        Channel                            Date         Age Bin   PfPR Bin
        PfPR by Gametocytemia and Age Bin  1970-11-01       5       0             0
                                                                    50            0
                                                                    500           0
                                                                    5000          5
          ...

        """
        df = pd.read_csv(self.reference_csv)
        df = df.loc[df['Village'].isin(self.metadata['village'])]

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
        dftemp['Channel'] = 'PfPR by Gametocytemia and Age Bin'
        dftemp.loc[len(dftemp)/2:, 'Channel'] = 'PfPR by Parasitemia and Age Bin'
        dftemp = dftemp.join(dftemp.groupby(['Channel', 'Date', 'Age Bin'])['Counts'].sum(),
                             on=['Channel', 'Date', 'Age Bin'],
                             rsuffix='_tot')
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

        logger.debug('\n%s', dftemp)

        return dftemp, self.metadata
