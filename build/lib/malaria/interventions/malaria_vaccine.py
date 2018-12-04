import copy, math, collections
from dtk.utils.Campaign.utils.RawCampaignObject import RawCampaignObject


def flatten(d, parent_key='', sep='_'):
    items = []
    for k, v in d.items():
        new_key = parent_key + sep + k if parent_key else k
        if isinstance(v, collections.MutableMapping):
            items.extend(flatten(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)


def add_vaccine(cb, vaccine_type='RTSS', vaccine_params={}, start_days=[0], coverage=1.0, repetitions=3, interval=60,
                nodes=[], target_group='Everyone', node_property_restrictions=[], ind_property_restrictions=[],
                trigger_condition_list=[], triggered_delay=0, listening_duration=-1, target_residents_only=1):

    if vaccine_type not in ['RTSS', 'PEV', 'TBV'] :
        raise ValueError('Requested vaccine type %s has not been specified' % vaccine_type)

    vaccine_dict = load_vaccines()
    vaccine = copy.deepcopy(vaccine_dict[vaccine_type])

    if vaccine_params :
        vaccine.update(vaccine_params)

    receiving_vaccine_event = {
        "class": "BroadcastEvent",
        "Broadcast_Event": "Received_Vaccine"
    }
    interventions = [vaccine, receiving_vaccine_event]

    node_cfg = {'Node_List': nodes, "class": "NodeSetNodeList"} if nodes else {"class": "NodeSetAll"}

    if trigger_condition_list:
        if triggered_delay > 0:
            actual_config = {
                "class": "DelayedIntervention",
                "Coverage": 1.0,
                "Delay_Distribution": "FIXED_DURATION",
                "Delay_Period": triggered_delay,
                "Actual_IndividualIntervention_Configs": interventions
            }
        else:
            actual_config = {
                            "class": "MultiInterventionDistributor",
                            "Intervention_List": interventions
                        }

        vaccine_event  = {
            "class": "CampaignEvent",
            "Start_Day": start_days[0],
            "Nodeset_Config": node_cfg,
            "Event_Coordinator_Config": {
                "class": "StandardInterventionDistributionEventCoordinator",
                "Intervention_Config": {
                    "class": "NodeLevelHealthTriggeredIV",
                    "Target_Demographic": "Everyone",
                    "Node_Property_Restrictions": node_property_restrictions,
                    "Property_Restrictions_Within_Node": ind_property_restrictions,
                    "Demographic_Coverage": coverage,
                    "Trigger_Condition_List": trigger_condition_list,
                    "Duration": listening_duration,
                    "Target_Residents_Only": target_residents_only,
                    "Actual_IndividualIntervention_Config": actual_config
                }
            }
        }

        if target_group != 'Everyone':
            vaccine_event['Event_Coordinator_Config']['Intervention_Config'].update({
                "Target_Demographic": "ExplicitAgeRanges",  # Otherwise default is Everyone
                "Target_Age_Min": target_group['agemin'],
                "Target_Age_Max": target_group['agemax']
            })

        cb.add_event(RawCampaignObject(vaccine_event))

    else:
        for start_day in start_days:
            vaccine_event = {
                "class": "CampaignEvent",
                "Start_Day": start_day,
                "Event_Coordinator_Config": {
                    "class": "StandardInterventionDistributionEventCoordinator",
                    "Target_Demographic": "Everyone",
                    "Node_Property_Restrictions": node_property_restrictions,
                    "Property_Restrictions_Within_Node": ind_property_restrictions,
                    "Demographic_Coverage": coverage,
                    "Intervention_Config": {
                        "class": "MultiInterventionDistributor",
                        "Intervention_List": interventions
                    },
                    "Number_Repetitions": repetitions,
                    "Timesteps_Between_Repetitions": interval
                },
                "Nodeset_Config": node_cfg
            }

            if target_group != 'Everyone':
                vaccine_event['Event_Coordinator_Config'].update({
                    "Target_Demographic": "ExplicitAgeRanges",  # Otherwise default is Everyone
                    "Target_Age_Min": target_group['agemin'],
                    "Target_Age_Max": target_group['agemax']
                })

            cb.add_event(RawCampaignObject(vaccine_event))

    return_params = flatten(vaccine_params, parent_key=vaccine_type)

    return_params.update({"{vaccine}_Coverage".format(vaccine=vaccine_type): coverage})

    return return_params

def load_vaccines() :
    # Pre-erythrocytic simple vaccine
    preerythrocytic_vaccine = {
        "class": "SimpleVaccine",
        "Vaccine_Type": "AcquisitionBlocking",
        "Vaccine_Take": 1.0,
        "Reduced_Acquire": 0.9,
        "Waning_Config": {
            "class": "WaningEffectExponential",
            "Decay_Time_Constant": (365 * 5) /math.log(2)
        },
        "Cost_To_Consumer": 15
    }

    # Transmission-blocking sexual-stage vaccine
    sexual_stage_vaccine = copy.deepcopy(preerythrocytic_vaccine)
    sexual_stage_vaccine.update({
        "Vaccine_Type": "TransmissionBlocking",
        "Reduced_Transmit": 0.9
    })

    # RTS,S simple vaccine
    rtss_simple_vaccine = copy.deepcopy(preerythrocytic_vaccine)
    rtss_simple_vaccine.update({
        "Reduced_Acquire": 0.8,  # 80% initial infection-blocking efficacy
        "Waning_Config": {
            "class": "WaningEffectExponential",
            "Decay_Time_Constant": (365 * 1.125) / math.log(2) # 13.5 month half-life
        },
        "Cost_To_Consumer": 15  # 3 doses * $5/dose
    })

    vaccine_dict = {'RTSS': rtss_simple_vaccine,
                    'PEV': preerythrocytic_vaccine,
                    'TBV': sexual_stage_vaccine}

    return vaccine_dict