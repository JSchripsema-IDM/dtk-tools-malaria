import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from simtools.Analysis.BaseAnalyzers import BaseAnalyzer

# requires malaria-toolbox installed
from sim_output_processing.spatial_output_dataframe import construct_spatial_output_df
from plotting.colors import load_color_palette


def top95(x) :
    return np.percentile(x, 95)
def bot5(x) :
    return np.percentile(x, 5)


class SpatialAnalyzer(BaseAnalyzer):

    def __init__(self, spatial_channels, working_dir='.'):
        super(SpatialAnalyzer, self).__init__(working_dir=working_dir,
                                              filenames=['output/SpatialReportMalariaFiltered_%s.bin' % x for x in spatial_channels]
                                           )
        self.sweep_variables = ['Run_Number']
        self.spatial_channels = spatial_channels

    def select_simulation_data(self, data, simulation):

        simdata = construct_spatial_output_df(data['output/SpatialReportMalariaFiltered_%s.bin' % self.spatial_channels[0]],
                                              self.spatial_channels[0])
        if len(self.spatial_channels) > 1:
            for ch in self.spatial_channels[1:]:
                simdata = pd.merge(left=simdata,
                                   right=construct_spatial_output_df(data['output/SpatialReportMalariaFiltered_%s.bin' % ch], ch),
                                   on=['time', 'node'])

        for sweep_var in self.sweep_variables:
            if sweep_var in simulation.tags.keys():
                simdata[sweep_var] = simulation.tags[sweep_var]
            else:
                simdata[sweep_var] = 0
        return simdata

    def finalize(self, all_data):

        selected = [data for sim, data in all_data.items()]
        if len(selected) == 0:
            print("No data have been returned... Exiting...")
            return

        df = pd.concat(selected).reset_index(drop=True)
        num_nodes = len(df['node'].unique())
        num_channels = len(self.spatial_channels)

        sns.set_style('white', {'axes.linewidth' : 0.5})
        palette = load_color_palette()
        fig = plt.figure('Spatial Outputs')
        for c, channel in enumerate(self.spatial_channels) :
            gdf = df.groupby(['node', 'time'])[channel].agg([np.mean, top95, bot5]).reset_index()
            for n, (node, ndf) in enumerate(gdf.groupby('node')) :
                ax = fig.add_subplot(num_channels, num_nodes, c*num_nodes + n + 1)
                ax.plot(ndf['time'], ndf['mean'], color=palette[n], label=node)
                ax.fill_between(ndf['time'], ndf['bot5'], ndf['top95'], color=palette[n], alpha=0.3, linewidth=0)
                if n == 0 :
                    ax.set_ylabel(channel)
                if c == 0 :
                    ax.set_title('node %d' % node)
                if c == num_channels - 1 :
                    ax.set_xlabel('day')

        plt.show()