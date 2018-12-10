import seaborn as sns
import pandas as pd
import matplotlib.pyplot as plt
from simtools.Analysis.BaseAnalyzers import BaseAnalyzer


class PfPRAnalyzer(BaseAnalyzer):

    def __init__(self, expt_name, report_names=["AnnualAverage"], sweep_variables=None, working_dir="."):
        super(PfPRAnalyzer, self).__init__(working_dir=working_dir,
                                        filenames=["output/MalariaSummaryReport_{name}.json".format(name=name)
                                                      for name in report_names]
                                           )
        self.sweep_variables = sweep_variables or ["Run_Number"]
        self.sitenames=report_names
        self.expt_name = expt_name
        self.data_channel = "PfPR_2to10"

    def select_simulation_data(self, data, simulation):

        simdata = []

        for site_name in self.sitenames:

            try:
                channeldata = data["output/MalariaSummaryReport_{name}.json".format(name=site_name)]["DataByTime"][self.data_channel]
            except:
                print("file not found for sim" + simulation.id)

            tempdata = pd.DataFrame({self.data_channel: channeldata,
                                    "Site_Name": site_name})
            tempdata = tempdata[-2:-1]
            simdata.append(tempdata)
        simdata = pd.concat(simdata)

        for sweep_var in self.sweep_variables:
            if sweep_var in simulation.tags.keys():
                simdata[sweep_var] = simulation.tags[sweep_var]
        for tag in simulation.tags :
            if 'coverage' in tag :
                simdata[tag] = simulation.tags[tag]
        return simdata

    def finalize(self, all_data):

        selected = [data for sim, data in all_data.items()]
        if len(selected) == 0:
            print("No data have been returned... Exiting...")
            return

        df = pd.concat(selected).reset_index(drop=True)

        num_interventions = len(df['intervention'].unique())
        num_sites = len(df['Site_Name'].unique())

        sns.set_style('whitegrid', {'axes.linewidth': 0.5})
        fig = plt.figure('%s PfPR' % self.expt_name, figsize=(15, 10))
        axes = [fig.add_subplot(num_interventions, num_sites, d + 1) for d in range(num_interventions*num_sites)]
        palette = sns.color_palette('Blues')

        for s, (site, sdf) in enumerate(df.groupby('Site_Name')):
            for i, (intervention, idf) in enumerate(sdf.groupby('intervention')):
                idf = idf.sort_values(by=self.data_channel)
                baseline = idf[idf['%s_coverage' % intervention] == 0]
                ax = axes[i*num_sites + s]
                for c, (coverage, cdf) in enumerate(idf.groupby('%s_coverage' % intervention)) :
                    print(c, baseline[self.data_channel], cdf[self.data_channel])
                    exit()
                    ax.plot(baseline[self.data_channel], cdf[self.data_channel], '-', color=palette[c], label=coverage)
                ax.set_xlabel('%s no intervention' % self.data_channel)
                ax.set_ylabel('%s with intervention' % self.data_channel)
                ax.set_title('%s %s' % (site, intervention))

        axes[-1].legend()
        plt.show()


if __name__ == "__main__":

    from simtools.Analysis.AnalyzeManager import AnalyzeManager
    from simtools.SetupParser import SetupParser

    SetupParser.default_block = 'HPC'
    SetupParser.init()
    sites = pd.read_csv("site_details.csv")

    analyzer = PfPRAnalyzer(expt_name='global_int_ex_test',
                              report_names=sites["name"].tolist(),
                              sweep_variables=["Run_Number",
                                               "x_Temporary_Larval_Habitat",
                                               "intervention"
                                               ])

    am = AnalyzeManager('9fafe8d6-cefc-e811-a2bd-c4346bcb1555', analyzers=analyzer)
    am.analyze()