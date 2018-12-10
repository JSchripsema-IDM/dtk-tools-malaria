import seaborn as sns
import pandas as pd
import matplotlib.pyplot as plt
from simtools.Analysis.BaseAnalyzers import BaseAnalyzer
from statsmodels.nonparametric.smoothers_lowess import lowess


class PfPRAnalyzer(BaseAnalyzer):

    def __init__(self, expt_name, report_names=["AnnualAverage"], sweep_variables=None, working_dir="."):
        super(PfPRAnalyzer, self).__init__(working_dir=working_dir,
                                        filenames=["output/MalariaSummaryReport_{name}.json".format(name=name)
                                                      for name in report_names]
                                           )
        self.sweep_variables = sweep_variables or ["Run_Number"]
        self.sitenames=report_names
        self.expt_name = expt_name

    def select_simulation_data(self, data, simulation):
        colname = "initial_prev" if self.dir_name == "initial" else "final_prev"

        simdata = []

        for site_name in self.sitenames:

            try:
                channeldata = data["output/MalariaSummaryReport_{name}.json".format(name=site_name)]["DataByTime"]["PfPR_2to10"]
            except:
                print("file not found for sim" + simulation.id)

            tempdata = pd.DataFrame({colname: channeldata,
                                    "Site_Name": site_name})
            tempdata = tempdata[-2:-1]
            simdata.append(tempdata)
        simdata = pd.concat(simdata)

        for sweep_var in self.sweep_variables:
            if sweep_var in simulation.tags.keys():
                simdata[sweep_var] = simulation.tags[sweep_var]
        return simdata

    def finalize(self, all_data):

        selected = [data for sim, data in all_data.items()]
        if len(selected) == 0:
            print("No data have been returned... Exiting...")
            return

        df = pd.concat(selected).reset_index(drop=True)

        datachannel = 'PfPR2to10'

        num_interventions = len(df['intervention'].unique())
        num_sites = len(df['Site_Name'].unique())

        sns.set_style('whitegrid', {'axes.linewidth': 0.5})
        fig = plt.figure('%s PfPR' % self.expt_name, figsize=(15, 10))
        axes = [fig.add_subplot(num_interventions, num_sites, d + 1) for d in range(num_interventions*num_sites)]
        palette = sns.color_palette('Blues')

        baseline = df[all([df['%s_coverage' % x] == 0 for x in df['intervention'].unique()])]

        for s, (site, sdf) in enumerate(df.groupby('Site_Name')):
            sdf = sdf.sort_values(by='PfPR2to10')
            for i, (intervention, idf) in enumerate(sdf.groupby('intervention')):
                ax = axes[s*num_sites+i]
                for c, (coverage, cdf) in enumerate(idf.groupby('%s_coverage' % intervention)) :
                    xvar = [y for x, y in zip(cdf[datachannel].values, baseline[datachannel].values) if (y > 0)]
                    yvar = [x for x, y in zip(cdf[datachannel].values, baseline[datachannel].values) if (y > 0)]
                    ys = lowess(yvar, xvar, frac=0.2)[:, 1]
                    ax.plot(xvar, ys, '-', color=palette[c], label=coverage)
                ax.set_xlabel('%s no intervention' % datachannel)
                ax.set_ylabel('%s with intervention' % datachannel)
                ax.set_title(intervention)

        axes[-1].legend()
        plt.show()
