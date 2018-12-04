
# Add filtered reports to separate this node out
import pandas as pd
from malaria.reports.MalariaReport import add_filtered_spatial_report, add_event_counter_report, add_filtered_report


def add_all_reports(cb):
    add_event_counter_report(cb, event_trigger_list=["Received_Treatment"])
    add_filtered_spatial_report(cb, channels=["Population", "True_Prevalence"])

    # Filtered report just for work node, and just for catchment:
    regional_EIR_node_label = 100000
    # Quick and dirty way to get sorted, unique list of grid cells in catchment:
    df = pd.read_csv("./inputs/grid_all_healthseek_events.csv")
    catch_node_ids = list(set(list(df["grid_cell"])))

    add_filtered_report(cb, nodes=[regional_EIR_node_label], description='Work')
    add_filtered_report(cb, nodes=catch_node_ids, description='Catchment')
