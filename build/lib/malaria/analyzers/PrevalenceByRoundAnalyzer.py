
import logging

import pandas as pd

from calibtool import LL_calculators
from calibtool.analyzers.BaseCalibrationAnalyzer import BaseCalibrationAnalyzer

logger = logging.getLogger(__name__)


class PrevalenceByRoundAnalyzer(BaseCalibrationAnalyzer):

    required_reference_types = ['prevalence_by_round']

    y = 'New Diagnostic Prevalence'

    data_group_names = ['sample', 'sim_id', 'channel']

    def __init__(self, site, weight=1, compare_fn=LL_calculators.euclidean_distance, **kwargs):
        super(PrevalenceByRoundAnalyzer, self).__init__(site, weight, compare_fn)
        self.reference = site.get_reference_data('prevalence_by_round')
        self.refdf = pd.DataFrame(self.reference)
        self.regions = site.get_region_list()
        # self.regions = self.reference['grid_cell'].unique()
        self.filenames = ['output/ReportMalariaFiltered.json']
        region_filenames = ['output/ReportMalariaFiltered' + x + '.json' for x in self.regions if x != 'all']
        if 'all' in self.regions :
            self.filenames += region_filenames
            # self.regions.insert(0, self.regions.pop(self.regions.index('all')))
        else :
            self.filenames = region_filenames

    def filter(self, sim_metadata):
        '''
        This analyzer only needs to analyze simulations for the site it is linked to.
        N.B. another instance of the same analyzer may exist with a different site
             and correspondingly different reference data.
        '''
        return sim_metadata.get('__site__', False) == self.site.name

    def apply(self, parser):
        '''
        Extract data from output data
        '''
        dfs = []
        set_N = False
        if 'N' not in self.refdf.columns:
            set_N = True
            Ndf = pd.DataFrame()

        for i, region in enumerate(self.regions) :
            data = [parser.raw_data[self.filenames[i]]['Channels'][self.y]['Data'][x] for x in self.refdf['sim_date'].values]
            pop = [parser.raw_data[self.filenames[i]]['Channels']['Statistical Population']['Data'][x] for x in self.refdf['sim_date'].values]

            df = pd.DataFrame({ self.y: data},
                                index=self.refdf['sim_date'].values)
            df.region = region
            df.index.name = 'sim_date'
            dfs.append(df)

            if set_N :
                t = pd.DataFrame({ 'grid_cell' : [region]*len(pop),
                                   'N' : pop})
                t['sim_date'] = self.refdf['sim_date']
                Ndf = pd.concat([Ndf, t])

        if set_N :
            self.refdf = pd.merge(left=self.refdf, right=Ndf, on=['grid_cell', 'sim_date'])

        c = pd.concat(dfs, axis=1, keys=self.regions, names=['region'])
        channel_data = c.stack(['region'])
        channel_data.sample = parser.sim_data.get('__sample_index__')
        channel_data.sim_id = parser.sim_id

        return channel_data

    def combine(self, parsers):
        '''
        Combine the simulation data into a single table for all analyzed simulations.
        '''
        selected = [p.selected_data[id(self)] for p in parsers.values() if id(self) in p.selected_data]
        combined = pd.concat(selected, axis=1,
                             keys=[(d.sample, d.sim_id) for d in selected],
                             names=self.data_group_names)
        stacked = combined.stack(['sample', 'sim_id'])
        self.data = stacked.groupby(level=['sample', 'region', 'sim_date']).mean()
        logger.debug(self.data)

    def compare(self, sample):
        '''
        Assess the result per sample, in this case the likelihood
        comparison between simulation and reference data.
        '''
        return sum([self.compare_fn(self.refdf[self.refdf['grid_cell']==region]['prev'].values,
                                    df[self.y].tolist()) for (region, df) in sample.groupby(level='region')])

    def finalize(self):
        '''
        Calculate the output result for each sample.
        '''
        self.result = self.data.groupby(level='sample').apply(self.compare)
        logger.debug(self.result)

    def cache(self):
    #     '''
    #     Return a cache of the minimal data required for plotting sample comparisons
    #     to reference comparisons.
    #     '''
        cache = self.data.copy()

        sample_dicts = []
        for idx, df in cache.groupby(level='sample', sort=True) :
            d = { 'region' : self.regions,
                   self.y : [sdf[self.y].values.tolist() for jdx, sdf in df.groupby(level='region') ] }
            sample_dicts.append(d)

        logger.debug(sample_dicts)
        return {'samples': sample_dicts, 'ref': self.reference, 'axis_names': ['region', self.y]}

    def uid(self):
        ''' A unique identifier of site-name and analyzer-name. '''
        return '_'.join([self.site.name, self.name])

    @classmethod
    def plot_comparison(cls, fig, data, **kwargs):
        fmt_str = kwargs.pop('fmt', None)
        args = (fmt_str,) if fmt_str else ()
        ref = False
        if kwargs.pop('reference', False): # this seems switched around to me? but is working properly
            ref = True
        if ref:
            if isinstance(data, str) :
                from io import StringIO
                data = pd.read_csv(StringIO(data), sep='\s+')
            else :
                data = pd.DataFrame(data)
            region_list = data['grid_cell'].unique()
            data = { r : rdf['prev'].values for r,rdf in data.groupby('grid_cell')}
        else :
            region_list = data['region']
            channelname = [x for x in data.keys() if 'region' not in x][0]
        numregions = len(region_list)

        for i, region in enumerate(region_list) :
            ax = fig.add_subplot(max([1, (numregions+1)/2]), min([numregions, 2]), i+1)
            if ref :
                ax.plot(range(1, len(data[region])+1), data[region], *args, **kwargs)
            else :
                ax.plot(range(1, len(data[channelname][i]) + 1), data[channelname][i], *args, **kwargs)
            ax.set_title(region)

        ax = fig.add_subplot(111)
        ax.set(xlabel='round')
        if not ref :
            ax.set(ylabel=channelname)
