import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib as mpl
import os
from simtools.Analysis.BaseAnalyzers import BaseAnalyzer

mpl.rcParams['pdf.fonttype'] = 42


class MigrationCountAnalyzer(BaseAnalyzer) :

    def __init__(self):
        super(MigrationCountAnalyzer, self).__init__(filenames=['output/ReportHumanMigrationTracking.csv'])

    def select_simulation_data(self, data, simulation):

        mdf = data[self.filenames[0]]

        mdf = mdf[mdf['MigrationType'] != 'home']
        mdf = mdf[mdf['Event'] == 'Emigrating']
        d = { m_type : [len(gdf)/2] for m_type, gdf in mdf.groupby('MigrationType')}
        df = pd.DataFrame(d)
        return df

    def finalize(self, all_data):

        selected = [data for sim, data in all_data.items()]
        if len(selected) == 0:
            print("No data have been returned... Exiting...")
            return

        df = pd.concat(selected).reset_index(drop=True)

