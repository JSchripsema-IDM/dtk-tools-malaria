import logging
from abc import abstractmethod
import pandas as pd
import numpy as np
from simtools.Analysis.BaseAnalyzers import BaseCalibrationAnalyzer

from malaria.analyzers.Helpers import convert_annualized, convert_to_counts, age_from_birth_cohort, aggregate_on_index
from scipy.stats import binom
from dtk.utils.parsers.malaria_summary import summary_channel_to_pandas

from calibtool.LL_calculators import gamma_poisson_pandas, beta_binomial_pandas

logger = logging.getLogger(__name__)


class ChannelByAgeCohortAnalyzer(BaseCalibrationAnalyzer):
    """
    Base class implementation for similar comparisons of age-binned reference data to simulation output.
    """
    site_ref_type = None

    @abstractmethod
    def __init__(self, site, weight=1, compare_fn=None, **kwargs):
        super(ChannelByAgeCohortAnalyzer, self).__init__(weight=weight)
        self.filenames = ['output/MalariaSummaryReport_Annual_Report.json']
        self.population_channel = 'Average Population by Age Bin'
        self.compare_fn = compare_fn
        self.site = site
        self.reference = site.get_reference_data(self.site_ref_type)

        ref_channels = self.reference.columns.tolist()
        if len(ref_channels) != 2:
            raise Exception('Expecting two channels from reference data: %s' % ref_channels)
        try:
            ref_channels.pop(ref_channels.index(self.population_channel))
            self.channel = ref_channels[0]
        except ValueError:
            raise Exception('Population channel (%s) missing from reference data: %s' %
                            (self.population_channel, ref_channels))

        # Convert reference columns to those needed for likelihood comparison
        # Trials = Person Years; Observations = Incidents
        self.reference = pd.DataFrame({'Trials': self.reference[self.population_channel],
                                       'Observations': (self.reference[self.population_channel]
                                                        * self.reference[self.channel])})

    def filter(self, simulation):
        """
        This analyzer only needs to analyze simulations for the site it is linked to.
        N.B. another instance of the same analyzer may exist with a different site
        and correspondingly different reference data.
        """
        return simulation.tags.get('__site__', False) == self.site.name

    def select_simulation_data(self, data, simulation):
        """
        Extract data from output data and accumulate in same bins as reference.
        """

        # Load data from simulation
        data = data[self.filenames[0]]

        # Get channels by age and time series
        channel_series = summary_channel_to_pandas(data, self.channel)
        population_series = summary_channel_to_pandas(data, self.population_channel)
        channel_data = pd.concat([channel_series, population_series], axis=1)

        # Convert Average Population to Person Years
        person_years = convert_annualized(channel_data[self.population_channel],
                                          start_day=channel_series.Start_Day,
                                          reporting_interval=channel_series.Reporting_Interval)
        channel_data['Trials'] = person_years

        # Calculate Incidents from Annual Incidence and Person Years
        channel_data['Observations'] = convert_to_counts(channel_data[self.channel], channel_data.Trials)

        # Reset multi-index and perform transformations on index columns
        df = channel_data.reset_index()
        df = age_from_birth_cohort(df)  # calculate age from time for birth cohort

        # Re-bin according to reference and return single-channel Series
        sim_data = aggregate_on_index(df, self.reference.index, keep=['Observations', 'Trials'])

        sim_data.sample = simulation.tags.get('__sample_index__')
        sim_data.sim_id = simulation.id

        return sim_data

    @staticmethod
    def join_reference(sim, ref):
        sim.columns = sim.columns.droplevel(0)  # drop sim 'sample' to match ref levels
        return pd.concat({'sim': sim, 'ref': ref}, axis=1).dropna()

    def compare(self, sample):
        """
        Assess the result per sample, in this case the likelihood
        comparison between simulation and reference data.
        """
        return self.compare_fn(self.join_reference(sample, self.reference))

    def finalize(self, all_data):
        """
        Calculate the output result for each sample.
        """
        selected = list(all_data.values())

        # Stack selected_data from each parser, adding unique (sim_id) and shared (sample) levels to MultiIndex
        combine_levels = ['sample', 'sim_id', 'channel']
        combined = pd.concat(selected, axis=1,
                             keys=[(s.tags.get('__sample_index__'), s.id) for s in all_data.keys()],
                             names=combine_levels)

        data = combined.groupby(level=['sample', 'channel'], axis=1).mean()

        return data.groupby(level='sample', axis=1).apply(self.compare)

    @staticmethod
    def error_bars(df):
        return (np.sqrt(df.Observations) / df.Trials).tolist()

    @classmethod
    def plot_comparison(cls, fig, data, **kwargs):
        ax = fig.gca()
        df = pd.DataFrame.from_dict(data, orient='columns')
        incidence = df.Observations / df.Trials
        age_bin_left_edges = [0] + df['Age Bin'][:-1].tolist()
        age_bin_centers = 0.5 * (df['Age Bin'] + age_bin_left_edges)
        if kwargs.pop('reference', False):
            logger.debug('age_bin_centers: %s', age_bin_centers)
            logger.debug('incidence: %s', incidence)
            ax.errorbar(age_bin_centers, incidence, yerr=cls.error_bars(df), **kwargs)
        else:
            fmt_str = kwargs.pop('fmt', None)
            args = (fmt_str,) if fmt_str else ()
            ax.plot(age_bin_centers, incidence, *args, **kwargs)
        ax.set(xlabel='Age (years)', ylabel=cls.site_ref_type.replace('_by_age', '').replace('_', ' ').title())


class PrevalenceByAgeCohortAnalyzer(ChannelByAgeCohortAnalyzer):
    """
    Compare reference prevalence-by-age measurements to simulation output.

    N.B. Using the logic that converts annualized incidence and average populations to incidents and person years,
    implicitly introduces a 1-year time constant for correlations in repeat prevalence measurements.
    """

    site_ref_type = 'prevalence_by_age'

    def __init__(self, site, weight=1, compare_fn=beta_binomial_pandas, **kwargs):
        super(PrevalenceByAgeCohortAnalyzer, self).__init__(site, weight, compare_fn, **kwargs)

    @staticmethod
    def error_bars(df):
        """
        Return 68% (1-sigma) binomial confidence interval.
        pyplot.errorbar expects a 2xN array of unsigned offsets relative to points
        """
        errs = [binom.interval(0.68, n, p=k/n, loc=-k) / n for n, k in zip(df.Trials, df.Observations)]
        return np.abs(np.array(errs).T)


class IncidenceByAgeCohortAnalyzer(ChannelByAgeCohortAnalyzer):
    """
    Compare reference incidence-by-age measurements to simulation output.
    """

    site_ref_type = 'annual_clinical_incidence_by_age'

    def __init__(self, site, weight=1, compare_fn=gamma_poisson_pandas, **kwargs):
        super(IncidenceByAgeCohortAnalyzer, self).__init__(site, weight, compare_fn, **kwargs)

