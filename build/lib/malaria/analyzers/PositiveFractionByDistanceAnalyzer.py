
import logging

import pandas as pd

from calibtool import LL_calculators
from calibtool.analyzers.Helpers import get_spatial_report_data_at_date, get_risk_by_distance
from calibtool.analyzers.BaseCalibrationAnalyzer import BaseCalibrationAnalyzer


logger = logging.getLogger(__name__)

class PositiveFractionByDistanceAnalyzer(BaseCalibrationAnalyzer):

    required_reference_types = ['risk_by_distance']
    filenames = ['output/SpatialReportMalariaFiltered_New_Diagnostic_Prevalence.bin',
                 'output/SpatialReportMalariaFiltered_Population.bin']

    x = 'distance'
    y = 'Risk of RDT Positive'

    data_group_names = ['sample', 'sim_id', 'channel']

    def __init__(self, site, weight=1, compare_fn=LL_calculators.euclidean_distance, **kwargs):
        super(PositiveFractionByDistanceAnalyzer, self).__init__(site, weight, compare_fn)
        self.testday = kwargs.get('testday')
        self.reference = site.get_reference_data('risk_by_distance')
        self.ignore_nodes = site.get_ignore_node_list()
        self.distmat = site.get_distance_matrix()

    def filter(self, sim_metadata):
        '''
        This analyzer only needs to analyze simulations for the site it is linked to.
        N.B. another instance of the same analyzer may exist with a different site
             and correspondingly different reference data.
        '''
        return sim_metadata.get('__site__', False) == self.site.name

    def apply(self, parser):
        '''
        Extract data from output data and measure risk of RDT+ by distance from RDT+.
        '''
        prev_data = get_spatial_report_data_at_date(parser.raw_data[self.filenames[0]], self.testday)
        prev_data.rename(columns={ 'data' : 'prev' }, inplace=True )
        pop_data = get_spatial_report_data_at_date(parser.raw_data[self.filenames[1]], self.testday)
        pop_data.rename(columns={ 'data' : 'pop' } , inplace=True)
        df = pd.merge(prev_data, pop_data, on='node')

        if any(self.ignore_nodes) :
            df = df[~df['node'].isin(self.ignore_nodes)]
            df = df.reset_index(drop=True)
            
        df['pos'] = df['prev']*df['pop']
        ref_distance = self.reference['distances']
        
        positive_fraction = get_risk_by_distance(df, ref_distance, self.distmat)
        
        channel_data = pd.DataFrame({ self.y : positive_fraction + [df['pos'].sum()/df['pop'].sum()]},
                                      index=ref_distance+[1000])

        channel_data.index.name = self.x
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
        self.data = stacked.groupby(level=['sample', self.x]).mean()
        logger.debug(self.data)

    def compare(self, sample):
        '''
        Assess the result per sample, in this case the likelihood
        comparison between simulation and reference data.
        '''
        return self.compare_fn(self.reference['risks'] + [self.reference['prevalence']],
                               sample[self.y].tolist())

    def finalize(self):
        '''
        Calculate the output result for each sample.
        '''
        self.result = self.data.groupby(level='sample').apply(self.compare)
        logger.debug(self.result)

    def cache(self):
        '''
        Return a cache of the minimal data required for plotting sample comparisons
        to reference comparisons.
        '''

        cache = self.data.copy()
        cache = cache[[self.y]].reset_index(level=self.x)
        sample_dicts = [df.to_dict(orient='list') for idx, df in cache.groupby(level='sample', sort=True)]
        logger.debug(sample_dicts)

        return {'samples': sample_dicts, 'ref': self.reference, 'axis_names': [self.x, self.y]}

    def uid(self):
        ''' A unique identifier of site-name and analyzer-name. '''
        return '_'.join([self.site.name, self.name])

    @classmethod
    def plot_comparison(cls, fig, data, **kwargs):
        from matplotlib.ticker import FixedLocator

        ax = fig.gca()
        fmt_str = kwargs.pop('fmt', None)
        args = (fmt_str,) if fmt_str else ()
        ref = False
        if kwargs.pop('reference', False): # this seems switched around to me? but is working properly
            ref = True

        if ref:
            numpoints = len(data['distances'])+1
            ax.plot(range(numpoints), data['risks'] + [data['prevalence']], *args, **kwargs)
            ax.xaxis.set_major_locator(FixedLocator(range(numpoints)))
            ax.set_xticklabels(['hh'] + [str(i) for i in data['distances'][1:]] + ['all'])
        else :
            numpoints = len(data['distance'])
            ax.plot(range(numpoints), data['Risk of RDT Positive'], *args, **kwargs)

        ax.set(xlabel='distance from RDT+', ylabel='risk of RDT+')
