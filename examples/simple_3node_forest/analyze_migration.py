import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from simtools.Analysis.BaseAnalyzers import BaseAnalyzer

# requires malaria-toolbox installed
from plotting.colors import load_color_palette


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
        num_migration_types = len(adf['MigrationType'].unique())

        sns.set_style('white', {'axes.linewidth' : 0.5})
        palette = load_color_palette()
        fig = plt.figure('Migration', figsize=(16,7))
        fig.subplots_adjust(right=0.98, left=0.05, wspace=0.25)

        for m, (mig, mdf) in enumerate(adf.groupby('MigrationType')) :
            ax = fig.add_subplot(num_migration_types, 4, m*4+1)
            num_events = mdf.groupby('Run_Number')['Event'].agg(len).values
            sns.distplot(num_events, ax=ax, color=palette[m], label=mig)
            ax.set_xlabel('number of trips')
            ax.set_ylabel('frac of sims')
            ax.legend()

            ax = fig.add_subplot(num_migration_types, 4, m*4+2)
            for r, rdf in mdf.groupby('Run_Number') :
                sns.kdeplot(rdf['AgeYears'], ax=ax, color=palette[m], linewidth=0.5, alpha=0.5, label='')
            sns.kdeplot(mdf['AgeYears'], ax=ax, color=palette[m], label='')
            ax.set_xlabel('Traveler age')
            ax.set_ylabel('fraction of trips')
            ax.set_xlim(-5, 205)

            ax = fig.add_subplot(num_migration_types, 4, m*4+3)
            for r, rdf in mdf.groupby('Run_Number') :
                trip_durations = []
                grouped = rdf.groupby('IndividualID')
                for gn, gdf in grouped :
                    t = gdf['Time'].values
                    d = [t[2*x+1] - t[2*x] for x in range(int(len(t)/2))]
                    trip_durations.extend(d)

                sns.kdeplot(trip_durations, ax=ax, linewidth=0.5, color=palette[m])
            ax.set_xlabel('days at destination')
            ax.set_ylabel('fraction of trips')

            ax = fig.add_subplot(num_migration_types, 4, m*4+4)
            if mig == 'intervention' :
                for r, rdf in mdf.groupby('Run_Number') :
                    sns.kdeplot(rdf[rdf['To_NodeID'] == self.forest_nodeid]['Time'], ax=ax,
                                color=palette[2], label='', linewidth=0.5, alpha=0.5)
                sns.kdeplot(mdf[mdf['To_NodeID'] == self.forest_nodeid]['Time'], ax=ax,
                            color=palette[2], label='to forest')
                for r, rdf in mdf.groupby('Run_Number') :
                    sns.kdeplot(rdf[rdf['From_NodeID'] == self.forest_nodeid]['Time'], ax=ax,
                                color=palette[3], label='', linewidth=0.5, alpha=0.5)
                sns.kdeplot(mdf[mdf['From_NodeID'] == self.forest_nodeid]['Time'], ax=ax,
                            color=palette[3], label='from forest')
            else :
                for r, rdf in mdf.groupby('Run_Number'):
                    sns.kdeplot(rdf['Time'], ax=ax,
                                color=palette[3], label='', linewidth=0.5, alpha=0.5)
                sns.kdeplot(mdf['Time'], ax=ax, label='',
                            color=palette[3])
            ax.set_xlim(-5,370)
            ax.set_xlabel('travel day')
            ax.set_ylabel('fraction of trips')

        plt.show()
