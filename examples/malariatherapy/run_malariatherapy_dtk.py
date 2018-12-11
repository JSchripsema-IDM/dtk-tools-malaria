
"""
title: run_malariatherapy_dtk.py

description: An example script for running malariatherapy challenge bite style infections where
infection shapes are drawn using scalable transitions as described in the Malaria 2.0 work.

author: Jon Russell

date: 11/29/2018

notes and dependencies: Uses a special config 'from-cfg.json' in the bin directory to use the
updated immune model

Institute for Disease Modeling, Bellevue, WA
"""

from os import path
from dtk.utils.core.DTKConfigBuilder import DTKConfigBuilder
from dtk.generic.climate import set_climate_constant

from simtools.SetupParser import SetupParser
from simtools.ExperimentManager.ExperimentManagerFactory import ExperimentManagerFactory
from simtools.ModBuilder import  ModFn, ModBuilder
from simtools.Analysis.AnalyzeManager import AnalyzeManager

from malaria.interventions.malaria_challenge import add_challenge_trial
from malaria.reports.MalariaReport import add_patient_report

from analyze_infection_durations import DurationsAnalyzer
from immunity_transitions_configuration import set_transition_matrix

import json


def prepare_malariatherapy_configbuilder(config_path, immunity_forcing=True, years=1):
    # Setup -------------------------------------------------------------------------------------------
    cb = DTKConfigBuilder.from_files(config_path)
    cb.update_params({'Vector_Species_Names': [],
                      'Simulation_Duration': 365 * years,
                      'Demographics_Filenames': ['Malariatherapy_demographics.json']
                      })
    set_climate_constant(cb)

    # Add source of infection (challenge bite or forced EIR) ------------------------------------------
    add_challenge_trial(cb, start_day=0)

    # ---- CUSTOM REPORTS ----
    add_patient_report(cb)
    return cb


def set_immune_forcing_builder(transition_matrix=None, scale_factor_array=[2, 5, 10, 100]):
    builder = ModBuilder.from_combos(
        [ModFn(set_transition_matrix, transition_matrix, scale_factor)
         for scale_factor in scale_factor_array]
    )
    return builder


def run_experiment(configbuilder, experiment_name, experiment_builder, analyzers):
    run_sim_args = {'config_builder': configbuilder,
                    'exp_name': experiment_name,
                    'exp_builder': experiment_builder
                    }

    if not SetupParser.initialized:
        SetupParser.init('HPC')

    exp_manager = ExperimentManagerFactory.init()
    exp_manager.run_simulations(**run_sim_args)
    exp_manager.wait_for_finished(verbose=True)
    assert (exp_manager.succeeded())
    am = AnalyzeManager(exp_manager.experiment)
    for a in analyzers:
        am.add_analyzer(a)
    am.analyze()

def build_all_pieces_and_run(cfg_path, experiment_name, immunity_forcing=True,
                             scale_factor_file="scale_factor_array.json", years=1, debug=False):
    cb = prepare_malariatherapy_configbuilder(config_path=cfg_path, immunity_forcing=immunity_forcing)
    if debug:
        print(f"DEBUG: config builder created")
    analyzers = [DurationsAnalyzer()]
    if debug:
        print(f"DEBUG: analyzers list created")
    exp_builder = ''
    if immunity_forcing:
        transition_matrix = cb.config['parameters']['Parasite_Peak_Density_Probabilities']
        with open(scale_factor_file) as infile:
            scale_factor_array = json.load(infile)
        exp_builder = set_immune_forcing_builder(transition_matrix, scale_factor_array)
    if debug:
        print(f"DEBUG: experiment builder created")
    run_experiment(configbuilder=cb, experiment_name=experiment_name, experiment_builder=exp_builder, analyzers=analyzers)

if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument('-c', '--config', default="./input/from-cfg.json", help="config file to use")
    p.add_argument('-e', '--experimentname', default="Malariatherapy_2pt0_infections", help="experiment name to use")
    p.add_argument('-i', '--immunityforcing', dest='forceimmunity', action='store_true', help="force immunity TRUE (default)")
    p.add_argument('-n', '--notforceimmunity', dest='forceimmunity', action='store_false', help="force immunity FALSE")
    p.add_argument('-s', '--scalefactorfile', default='scale_factor_array.json', help="file to read scale factors from")
    p.set_defaults(forceimmunity=True)
    p.add_argument('-d', '--debug', action='store_true', help="turns on debugging")
    args = p.parse_args()

    if args.debug:
        print(f"DEBUG: Arguments: {args}\n")

    build_all_pieces_and_run(cfg_path=args.config,
                             experiment_name=args.experimentname,
                             immunity_forcing=args.forceimmunity,
                             scale_factor_file=args.scalefactorfile,
                             years=1, debug=args.debug)

