import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib as mpl
import os
from simtools.Analysis.BaseAnalyzers import BaseAnalyzer

from simtools.Analysis.AnalyzeManager import AnalyzeManager
from simtools.SetupParser import SetupParser

from plotting.colors import load_color_palette

mpl.rcParams['pdf.fonttype'] = 42


class MigrationCountAnalyzer(BaseAnalyzer) :

    def __init__(self, forest_nodeid):
        super(MigrationCountAnalyzer, self).__init__(filenames=['output/ReportHumanMigrationTracking.csv'])
        self.sweep_variables = ['Run_Number']
        self.forest_nodeid = forest_nodeid

    def select_simulation_data(self, data, simulation):

        mdf = data[self.filenames[0]]

        mdf = mdf[mdf['MigrationType'] != 'home']
        mdf = mdf[mdf['Event'] == 'Emigrating']
        for sweep_var in self.sweep_variables:
            if sweep_var in simulation.tags.keys():
                mdf[sweep_var] = simulation.tags[sweep_var]
            else:
                mdf[sweep_var] = 0
        return mdf

    def finalize(self, all_data):

        selected = [data for sim, data in all_data.items()]
        if len(selected) == 0:
            print("No data have been returned... Exiting...")
            return

        adf = pd.concat(selected).reset_index(drop=True)
        migration_types = len(adf['MigrationType'].unique())

        sns.set_style('white', {'axes.linewidth' : 0.5})
        palette = load_color_palette()
        fig = plt.figure('Migration')
        for m, (mig, mdf) in enumerate(adf.groupby('MigrationType')) :
            ax = fig.add_subplot(migration_types, 4, m*4+1)
            num_events = mdf.groupby('Run_Number')['Event'].agg(len).values
            sns.distplot(num_events, ax=ax, color=palette[m], label=mig)
            ax.set_xlabel('number of trips')
            ax.set_ylabel('frequency')

            df = adf[adf['Run_Number'] == 0]
            df = df[df['MigrationType'] == mig]
            # df = df[(df['From_NodeID'] == self.forest_nodeid) | (df['To_NodeID'] == self.forest_nodeid)]

            df['time in year'] = df['Time'].apply(lambda x : x % 365)
            df['month in year'] = df['time in year'].apply(lambda x: int(x/30))

            # trip_durations = []
            # grouped = df.groupby('IndividualID')
            # for gn, gdf in grouped :
            #     t = gdf['Time'].values
            #     d = [t[2*x+1] - t[2*x] for x in range(len(t)/2)]
            #     trip_durations.extend(d)
            #
            # ax.hist(trip_durations, linewidth=0, bins=20, color='#7AC4AD')
            # ax.set_xlabel('days in forest')
            # ax.set_ylabel('number of trips')

            ax = fig.add_subplot(migration_types, 4, m * 4 + 2)
            # #df = df[df['Time'] >= 365]
            # ax = fig.add_subplot(1,3,2)
            grouped = df[df['To_NodeID'] == self.forest_nodeid].groupby('month in year')
            ax.bar([gn for gn, gdf in grouped], [len(gdf) for gn, gdf in grouped], align='center',
                   linewidth=0, color='#7AC4AD')
            #ax.set_xlim(-1,53)
            ax.set_xlabel('month departing to forest')
            #
            ax = fig.add_subplot(migration_types, 4, m * 4 + 3)
            grouped = df[df['From_NodeID'] == self.forest_nodeid].groupby('month in year')
            ax.bar([gn for gn, gdf in grouped], [len(gdf) for gn, gdf in grouped], align='center',
                   linewidth=0, color='#7AC4AD')
            #ax.set_xlim(-1,53)
            ax.set_xlabel('month returning from forest')

        plt.show()


if __name__ == '__main__':

    SetupParser.init("HPC")
    am = AnalyzeManager(exp_list='a2743ddf-30f4-e811-a2bd-c4346bcb1555', analyzers=MigrationCountAnalyzer(forest_nodeid=3),
                        force_analyze=True)

    print(am.experiments)
    am.analyze()
