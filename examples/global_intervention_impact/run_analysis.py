import os
import sys
import pandas as pd
sys.path.append(os.path.dirname(__file__))

from simtools.Analysis.AnalyzeManager import AnalyzeManager
from pfpr_analyzer import PfPRAnalyzer

if __name__ == "__main__":

    sites = pd.read_csv("site_details.csv")

    experiments = {
                   "atsb_llin_v4" :"71dbee13-b0fc-e811-a2bd-c4346bcb1555"
                   }

    for expt_name, exp_id in experiments.items():
        am = AnalyzeManager(exp_list=exp_id, analyzers=[PfPRAnalyzer(expt_name=expt_name,
                                                                     report_names = sites["name"].tolist(),
                                                                      sweep_variables=["Run_Number",
                                                                                       "x_Temporary_Larval_Habitat",
                                                                                       "intervention",
                                                                                       "intervention_coverage"
                                                                                       ])
                                                        ],
                            force_analyze=True)

    am.analyze()