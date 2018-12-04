import os
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import copy
from sympy import Matrix


def probability_shifting_module(TM, immune_stimulation_threshold,row_scale_factor,column_scale_factor):
    number_of_bin_edges = max([len(i) for i in TM])
    bin_numbers = np.arange(0, number_of_bin_edges)
    new_TM = copy.copy(TM)
    rows_to_cycle_through = np.arange(immune_stimulation_threshold, max(bin_numbers) + 1)
    # define a row scaling factor that represents the changing force of immunity across current density classes
    for row in rows_to_cycle_through:
        Old_column_values = [x for x in TM[row]]
        Bin_decreases = [np.log10(column_scale_factor * row_scale_factor * bin) for bin in bin_numbers]
        New_column_values = [Old_column_values[i] / Bin_decreases[i] for i in range(len(Old_column_values))]

        Net_zero_column_change = sum(
            [abs(New_column_values[j] - Old_column_values[j]) for j in np.arange(1, len(Old_column_values))])
        New_column_values[0] = Old_column_values[0] + Net_zero_column_change
        new_TM[row] = New_column_values

    return(TM,new_TM)

def set_transition_matrix(cb,TM,scale_factor,immune_stim_threshold = 1):
    old_TM, shifted_TM = probability_shifting_module(TM,immune_stim_threshold, row_scale_factor= scale_factor,column_scale_factor= scale_factor)
    cb.update_params({"Parasite_Peak_Density_Probabilities": shifted_TM,
                      ".Scale_Factor": scale_factor})

    return {"scale_factor": scale_factor}
