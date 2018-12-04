import random
from dtk.utils.Campaign.utils.RawCampaignObject import RawCampaignObject
from dtk.interventions.triggered_campaign_delay_event import triggered_campaign_delay_event

positive_broadcast = {
        "class": "BroadcastEvent",
        "Broadcast_Event": "TestedPositive"
        }


negative_broadcast = {
        "class": "BroadcastEvent",
        "Broadcast_Event": "TestedNegative"
        }

def add_diagnostic_survey(cb, coverage=1, repetitions=1, tsteps_btwn=365, target='Everyone', start_day=0,
                          diagnostic_type='TRUE_PARASITE_DENSITY', diagnostic_threshold=40, event_name="Diagnostic Survey",
                          node_cfg={"class": "NodeSetAll"}, positive_diagnosis_configs=[], negative_diagnosis_configs=[],
                          received_test_event='Received_Test', IP_restrictions=[], NP_restrictions=[],
                          pos_diag_IP_restrictions=[], neg_diag_IP_restrictions=[], trigger_condition_list=[],
                          listening_duration=-1, triggered_campaign_delay=0 ):
    """
    Function to add recurring prevalence surveys with configurable diagnostic
    When using "trigger_condition_list", the diagnostic is triggered by the words listed

    :param cb: Configuration builder holding the interventions
    :param repetitions: Number of repetitions
    :param tsteps_btwn:  Timesteps between repetitions
    :param target: Target demographic. Default is 'Everyone'
    :param start_day: Start day for the outbreak
    :param coverage: probability an individual receives the diagnostic
    :param diagnostic_type:
        BLOOD_SMEAR
        PCR
        PF_HRP2
        TRUE_PARASITE_DENSITY
        HAS_FEVER
    :param diagnostic_threshold :
        Detection_Threshold becomes a parameter required by all types. The units of the threshold depend on the diagnostic type selected.
        BLOOD_SMEAR
            Use the SusceptibilityMalaria::CheckParasiteCountWithTest() (or at least logic) to get a parasite density to check against the threshold
        PCR
            Use the ReportUtilitiesMalaria::NASBADensityWithUncertainty() method to calculate a measured parasite density and check against the threshold
        PF_HRP2
            Add a new method to get the PfHRP2 value and check against the threshold
        TRUE_PARASITE_DENSITY
            Check the true/actual parasite density against the threshold
        HAS_FEVER
            Check the person's fever against the threshold
    :param nodes: nodes to target.
    # All nodes: {"class": "NodeSetAll"}.
    # Subset of nodes: {"class": "NodeSetNodeList", "Node_List": list_of_nodeIDs}
    :param positive_diagnosis_configs: list of events to happen to individual who receive a positive result from test
    :param received_test_event: string for individuals to broadcast upon receiving diagnostic
    :param IP_restrictions: list of IndividualProperty restrictions to restrict who takes action upon positive diagnosis
    :param NP_restrictions: node property restrictions
    :param trigger_condition_list: list of strings that will trigger a diagnostic survey.
    :param listening_duration: for diagnostics that are listening for trigger_condition_list, how long after start day to stop listening for the event
    :param triggered_campaign_delay: delay of running the campaign/intervention after receiving a trigger from the trigger_condition_list
    :return: nothing
    """

    # OLD version of DTK, without PfHRP2-enabled MalariaDiagnostic:
    # diagnostic_type options: Microscopy, NewDetectionTech, Other
    # intervention_cfg = {
    #                     "Diagnostic_Type": diagnostic_type,
    #                     "Detection_Threshold": diagnostic_threshold,
    #                     "class": "MalariaDiagnostic"
    #                     }

    intervention_cfg = {
                        "MalariaDiagnostic_Type": diagnostic_type,
                        "Detection_Threshold": diagnostic_threshold, 
                        "class": "MalariaDiagnostic"                                          
                        }

    intervention_cfg["Event_Or_Config"] = "Config"
    intervention_cfg["Positive_Diagnosis_Config"] = {
        "Intervention_List": positive_diagnosis_configs + [positive_broadcast],
        "class": "MultiInterventionDistributor"
    }
    if pos_diag_IP_restrictions:
        intervention_cfg["Positive_Diagnosis_Config"]["Property_Restrictions_Within_Node"] = pos_diag_IP_restrictions

    intervention_cfg["Negative_Diagnosis_Config"] = {
        "Intervention_List" : negative_diagnosis_configs + [negative_broadcast] ,
        "class" : "MultiInterventionDistributor"
        }
    if neg_diag_IP_restrictions :
        intervention_cfg["Negative_Diagnosis_Config"]["Property_Restrictions_Within_Node"] =neg_diag_IP_restrictions

    if trigger_condition_list:
        if repetitions > 1 or triggered_campaign_delay > 0:
            # create a trigger for each of the delays.
            trigger_condition_list = [triggered_campaign_delay_event(cb, start_day, nodeIDs=node_cfg,
                                                                     triggered_campaign_delay=triggered_campaign_delay + x * tsteps_btwn,
                                                                     trigger_condition_list=trigger_condition_list,
                                                                     listening_duration=listening_duration,
                                                                     node_property_restrictions=NP_restrictions) for x in range(repetitions)]
        survey_event = {"class": "CampaignEvent",
                        "Start_Day": start_day,
                        "Event_Name": event_name,
                        "Nodeset_Config": node_cfg,
                        "Event_Coordinator_Config": {
                            "class": "StandardInterventionDistributionEventCoordinator",
                            "Number_Distributions": -1,
                            "Intervention_Config":
                                {
                                    "class": "NodeLevelHealthTriggeredIV",
                                    "Trigger_Condition_List": trigger_condition_list,
                                    "Target_Residents_Only": 1,
                                    "Duration": listening_duration,
                                    "Demographic_Coverage": coverage,
                                    "Target_Demographic": target,
                                    "Property_Restrictions_Within_Node": IP_restrictions,
                                    "Node_Property_Restrictions": NP_restrictions,
                                    "Actual_IndividualIntervention_Config":
                                        {
                                            "class": "MultiInterventionDistributor",
                                            "Intervention_List": [
                                                {
                                                 "class": "BroadcastEvent",
                                                 "Broadcast_Event": received_test_event
                                                },
                                                intervention_cfg
                                            ]
                                        }
                                 },
                            }
                        }

        if isinstance(target, dict) and all([k in target.keys() for k in ['agemin', 'agemax']]):
            survey_event["Event_Coordinator_Config"]['Intervention_Config'].update({
                "Target_Demographic": "ExplicitAgeRanges",
                "Target_Age_Min": target['agemin'],
                "Target_Age_Max": target['agemax']})

        cb.add_event(RawCampaignObject(survey_event))

    else:
        survey_event = { "class" : "CampaignEvent",
                         "Start_Day": start_day,
                         "Event_Name" : event_name,
                         "Event_Coordinator_Config": {
                             "class": "StandardInterventionDistributionEventCoordinator",
                             "Node_Property_Restrictions": NP_restrictions,
                             "Property_Restrictions_Within_Node": IP_restrictions,
                             "Number_Distributions": -1,
                             "Number_Repetitions": repetitions,
                             "Timesteps_Between_Repetitions": tsteps_btwn,
                             "Demographic_Coverage": coverage,
                             "Intervention_Config": {
                                 "Intervention_List" : [
                                     { "class": "BroadcastEvent",
                                     "Broadcast_Event": received_test_event },
                                      intervention_cfg ] ,
                                "class" : "MultiInterventionDistributor" }
                             },
                         "Nodeset_Config": node_cfg
                         }

        if isinstance(target, dict) and all([k in target.keys() for k in ['agemin','agemax']]) :
            survey_event["Event_Coordinator_Config"].update({
                    "Target_Demographic": "ExplicitAgeRanges",
                    "Target_Age_Min": target['agemin'],
                    "Target_Age_Max": target['agemax'] })
        else :
            survey_event["Event_Coordinator_Config"].update({
                    "Target_Demographic": target } ) # default is Everyone
        cb.add_event(RawCampaignObject(survey_event))
    return
