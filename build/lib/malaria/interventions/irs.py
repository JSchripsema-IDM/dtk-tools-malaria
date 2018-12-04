import copy

from malaria.interventions.malaria_drug_campaigns import fmda_cfg
from dtk.interventions.irs import node_irs_config

def add_reactive_node_IRS(config_builder, start, duration=10000, trigger_coverage=1.0, irs_coverage=1.0,
                          node_selection_type='DISTANCE_ONLY',
                          reactive_radius=0, irs_ineligibility_duration=60,
                          delay=7, initial_killing=0.5, box_duration=90,
                          nodeIDs=[], node_property_restrictions=[]) :

    irs_config = copy.deepcopy(node_irs_config)
    irs_config['Killing_Config']['Decay_Time_Constant'] = box_duration
    irs_config['Killing_Config']['Initial_Effect'] = initial_killing
    irs_trigger_config = fmda_cfg(reactive_radius, node_selection_type, 'Spray_IRS')

    receiving_irs_event = {
        "class": "BroadcastEvent",
        "Broadcast_Event": "Node_Sprayed"
    }

    recent_irs = {"class": "NodePropertyValueChanger",
                  "Target_NP_Key_Value": "SprayStatus:RecentSpray",
                  "Daily_Probability": 1.0,
                  "Maximum_Duration": 0,
                  'Revert': irs_ineligibility_duration
                  }
    irs_config = [irs_config, receiving_irs_event, recent_irs]

    if not nodeIDs:
        nodes = { "class": "NodeSetAll" }
    else:
        nodes = { "class": "NodeSetNodeList", "Node_List": nodeIDs }

    no_spray = {'SprayStatus': 'None'}

    trigger_irs = { "Event_Name": "Trigger Reactive IRS",
                    "class": "CampaignEvent",
                    "Start_Day": start,
                    "Event_Coordinator_Config":
                    {
                        "class": "StandardInterventionDistributionEventCoordinator",
                        'Node_Property_Restrictions': [],
                        "Intervention_Config" : {
                            "class": "NodeLevelHealthTriggeredIV",
                            "Demographic_Coverage": trigger_coverage,
                            "Trigger_Condition_List": ["Received_Treatment"], # triggered by successful health-seeking
                            "Duration": duration,
                            "Actual_IndividualIntervention_Config" : {
                                "class": "DelayedIntervention",
                                "Delay_Distribution": "FIXED_DURATION",
                                "Delay_Period": delay,
                                "Actual_IndividualIntervention_Configs" : [irs_trigger_config]
                                }
                        }
                    },
                    "Nodeset_Config": nodes}

    distribute_irs = {  "Event_Name": "Distribute IRS",
                        "class": "CampaignEvent",
                        "Start_Day": start,
                        "Event_Coordinator_Config":
                        {
                            "class": "StandardInterventionDistributionEventCoordinator",
                            "Intervention_Config" : {
                                "class": "NodeLevelHealthTriggeredIV",
                                'Node_Property_Restrictions': [no_spray],
                                "Demographic_Coverage": irs_coverage,
                                "Trigger_Condition_List": ["Spray_IRS"],
                                "Blackout_Event_Trigger": "IRS_Blackout",
                                "Blackout_Period": 1,
                                "Blackout_On_First_Occurrence": 1,
                                "Actual_IndividualIntervention_Config" : {
                                    "Intervention_List" : irs_config,
                                    "class" : "MultiInterventionDistributor"
                                }
                            }
                        },
                        "Nodeset_Config": nodes
                    }

    if node_property_restrictions:
        trigger_irs['Event_Coordinator_Config']['Node_Property_Restrictions'].extend(node_property_restrictions)
        distribute_irs['Event_Coordinator_Config']['Intervention_Config']['Node_Property_Restrictions'] = [dict(no_spray.items() + x.items()) for x in node_property_restrictions]

    config_builder.add_event(trigger_irs)
    config_builder.add_event(distribute_irs)