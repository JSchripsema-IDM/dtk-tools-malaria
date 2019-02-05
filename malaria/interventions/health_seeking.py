from dtk.utils.Campaign.utils.RawCampaignObject import RawCampaignObject

expire_recent_drugs = {"class": "PropertyValueChanger",
                       "Target_Property_Key": "DrugStatus",
                       "Target_Property_Value": "RecentDrug",
                       "Daily_Probability": 1.0,
                       "Maximum_Duration": 0,
                       'Revert': 0
                       }


def add_health_seeking(config_builder,
                       start_day=0,
                       # Note: potential for overlapping drug treatments in the same individual
                       targets=[{'trigger': 'NewClinicalCase', 'coverage': 0.8, 'agemin': 15, 'agemax': 70, 'seek': 0.4,
                                 'rate': 0.3},
                                {'trigger': 'NewSevereCase', 'coverage': 0.8, 'seek': 0.6, 'rate': 0.5}],
                       drug=['Artemether', 'Lumefantrine'],
                       dosing='FullTreatmentNewDetectionTech',
                       nodes={"class": "NodeSetAll"},
                       node_property_restrictions:list=None,
                       ind_property_restrictions:list=None,
                       disqualifying_properties:list=None,
                       drug_ineligibility_duration=0,
                       duration=-1,
                       repetitions=1,
                       tsteps_btwn_repetitions=365,
                       broadcast_event_name='Received_Treatment'):

    """
    Add health-seeking behavior when a triggering event occurs using 
    the **NodeLevelHealthTriggeredIV** class. By default, triggered
    when new clinical or severe malaria cases occur.

    Args:
        config_builder: The :py:class:`DTKConfigBuilder <dtk.utils.core.DTKConfigBuilder>` 
          containing the campaign configuration.
        start_day: The day on which to start distributing the intervention 
          (**Start_Day** parameter).
        targets: A list of dictionaries that targets individuals based on 
          triggering events. See the default for an example. The product of 
          coverage and seek is the value for the **Demographic_Coverage** 
          parameter. 
        drug: The drug to administer. Use a str for a single drug or
          a list of str for multiple drugs.
        dosing: The dosing for the drugs (**Dosing_Type** parameter).
        nodes: The dictionary of nodes to apply this intervention to. 
          For all nodes: ``{"class": "NodeSetAll"}``. For a subset 
          of nodes: ``{"class": "NodeSetNodeList", "Node_List": list_of_nodeIDs}``.
        node_property_restrictions: The node properties a node must have 
          to receive the intervention (**Node_Property_Restrictions** parameter).
          Formatted as a list of dicts: ``[{ "NodeProperty1" : "PropertyValue1" }, 
          {'NodeProperty2': "PropertyValue2"}, ...]``.
        ind_property_restrictions: The individual properties an individual
          must have to receive the intervention (**Property_Restrictions_Within_Node 
          parameter). Formatted as a list of dicts: ``[{ "IndividualProperty1" : "PropertyValue1" }, 
          {'IndividualProperty2': "PropertyValue2"}, ...]``.
        disqualifying_properties: The individual properties that an individual 
          cannot have to receive the intervention. Formatted as a list of strings: 
          ``["IndividualProperty1:PropertyValue1"]``.
        drug_ineligibility_duration: The number of days to change the individual
          property value of **DrugStatus** to RecentDrug after receiving an 
          intervention. Individuals with status RecentDrug will not receive
          drugs for treatment. The demographics file must define the IP 
          **DrugStatus** with possible values None and RecentDrug. 
        duration: The length of the intervention, in days.
        repetitions: The number of times to repeat the intervention.
        tsteps_btwn_repetitions: The time steps between the repetitions.
        broadcast_event_name: The event name that is broadcast (**Broadcast_Event**
          parameter).

    Returns:
      None
    """

    receiving_drugs_event = {
        "class": "BroadcastEvent",
        "Broadcast_Event": broadcast_event_name
    }

    if broadcast_event_name not in config_builder.config["parameters"]['Listed_Events']:
        config_builder.config["parameters"]['Listed_Events'].append(broadcast_event_name)

    expire_recent_drugs['Revert'] = drug_ineligibility_duration

    drug_config, drugs = get_drug_config(drug, dosing, receiving_drugs_event,
                                         drug_ineligibility_duration, expire_recent_drugs)

    for t in targets:

        actual_config = build_actual_treatment_cfg(t['rate'], drug_config, drugs)
        if disqualifying_properties:
            actual_config['Disqualifying_Properties'] = disqualifying_properties
        health_seeking_config = {
            "class": "StandardInterventionDistributionEventCoordinator",
            "Number_Repetitions": repetitions,
            "Timesteps_Between_Repetitions": tsteps_btwn_repetitions,
            "Intervention_Config": {
                "class": "NodeLevelHealthTriggeredIV",
                "Trigger_Condition_List": [t['trigger']],
                "Duration": duration,
                # "Tendency": t['seek'],
                "Demographic_Coverage": t['coverage'] * t['seek'],  # to be FIXED later for individual properties
                "Actual_IndividualIntervention_Config": actual_config
            }
        }

        if ind_property_restrictions:
            health_seeking_config['Intervention_Config']["Property_Restrictions_Within_Node"] = ind_property_restrictions

        if drug_ineligibility_duration > 0 :
            drugstatus = {"DrugStatus": "None"}
            if ind_property_restrictions :
                health_seeking_config['Intervention_Config']["Property_Restrictions_Within_Node"] = [
                    {**drugstatus, **x} for x in ind_property_restrictions]
            else :
                health_seeking_config['Intervention_Config']["Property_Restrictions_Within_Node"] = [drugstatus]

        if node_property_restrictions:
            health_seeking_config['Intervention_Config']['Node_Property_Restrictions'] = node_property_restrictions

        if all([k in t.keys() for k in ['agemin', 'agemax']]):
            health_seeking_config["Intervention_Config"].update({
                "Target_Demographic": "ExplicitAgeRanges",  # Otherwise default is Everyone
                "Target_Age_Min": t['agemin'],
                "Target_Age_Max": t['agemax']})

        health_seeking_event = {"class": "CampaignEvent",
                                "Start_Day": start_day,
                                "Event_Coordinator_Config": health_seeking_config,
                                "Nodeset_Config": nodes}

        config_builder.add_event(RawCampaignObject(health_seeking_event))


def add_health_seeking_by_chw(config_builder,
                              start_day=0,
                              targets=[{'trigger': 'NewClinicalCase', 'coverage': 0.8, 'agemin': 15, 'agemax': 70,
                                         'seek': 0.4, 'rate': 0.3},
                                       {'trigger': 'NewSevereCase', 'coverage': 0.8, 'seek': 0.6, 'rate': 0.5}],
                              drug=['Artemether', 'Lumefantrine'],
                              dosing='FullTreatmentNewDetectionTech',
                              nodeIDs:list=None,
                              node_property_restrictions:list=None,
                              ind_property_restrictions:list=None,
                              drug_ineligibility_duration=0,
                              duration=100000,
                              chw={}):

    """
    Add health-seeking behavior when a triggering event occurs using 
    the **CommunityHealthWorkerEventCoordinator** class. By default, triggered
    when new clinical or severe malaria cases occur.

    Args:
        config_builder: The :py:class:`DTKConfigBuilder <dtk.utils.core.DTKConfigBuilder>` 
          containing the campaign configuration.
        start_day: The day on which to start distributing the intervention 
          (**Start_Day** parameter).
        targets: A list of dictionaries that targets individuals based on 
          triggering events. See the default for an example. The product of 
          coverage and seek is the value for the **Demographic_Coverage** 
          parameter. 
        drug: The drug to administer. Use a str for a single drug or
          a list of str for multiple drugs.
        dosing: The dosing for the drugs (**Dosing_Type** parameter).
        nodeIDs: The list of nodes to apply this intervention to (**Node_List** 
          parameter). For all nodes, NodeSetAll. For a subset 
          of nodes, the list_of_nodeIDs.
        node_property_restrictions: The node properties a node must have 
          to receive the intervention (**Node_Property_Restrictions** parameter).
          Formatted as a list of dicts: ``[{ "NodeProperty1" : "PropertyValue1" }, 
          {'NodeProperty2': "PropertyValue2"}, ...]``.
        ind_property_restrictions: The individual properties an individual
          must have to receive the intervention (**Property_Restrictions_Within_Node 
          parameter). Formatted as a list of dicts: ``[{ "IndividualProperty1" : "PropertyValue1" }, 
          {'IndividualProperty2': "PropertyValue2"}, ...]``.
        drug_ineligibility_duration: The number of days to change the individual
          property value of **DrugStatus** to RecentDrug after receiving an 
          intervention. Individuals with status RecentDrug will not receive
          drugs for treatment. The demographics file must define the IP 
          **DrugStatus** with possible values None and RecentDrug. 
        duration: The length of the intervention, in days.
        chw: The dictionary of the community health worker configuration
          that is overlayed on the default.

    Returns:
      None
    """

    chw_config = {
        'class': 'CommunityHealthWorkerEventCoordinator',
        'Duration': duration,
        'Distribution_Rate': 5,
        'Waiting_Period': 7,
        'Days_Between_Shipments': 90,
        'Amount_In_Shipment': 1000,
        'Max_Stock': 1000,
        'Initial_Amount_Distribution_Type': 'FIXED_DURATION',
        'Initial_Amount': 1000,
        'Target_Demographic': 'Everyone',
        'Target_Residents_Only': 0,
        'Demographic_Coverage': 1,
        'Trigger_Condition_List': ['CHW_Give_Drugs'],
        'Property_Restrictions_Within_Node': []}

    if chw:
        chw_config.update(chw)

    receiving_drugs_event = {
        "class": "BroadcastEvent",
        "Broadcast_Event": 'Received_Treatment'
    }

    # NOTE: node property restrictions isn't working yet for CHWEC (3/29/17)
    if node_property_restrictions:
        chw_config['Node_Property_Restrictions'] = node_property_restrictions

    nodes = {"class": "NodeSetNodeList", "Node_List": nodeIDs} if nodeIDs else {"class": "NodeSetAll"}

    add_health_seeking(config_builder, start_day=start_day, targets=targets, drug=[], nodes=nodes,
                       node_property_restrictions=node_property_restrictions,
                       ind_property_restrictions=ind_property_restrictions,
                       duration=duration, broadcast_event_name='CHW_Give_Drugs')

    if drug_ineligibility_duration > 0:
        chw_config["Property_Restrictions_Within_Node"].append({"DrugStatus": "None"})

    expire_recent_drugs['Revert'] = drug_ineligibility_duration
    drug_config, drugs = get_drug_config(drug, dosing, receiving_drugs_event,
                                         drug_ineligibility_duration, expire_recent_drugs)
    actual_config = build_actual_treatment_cfg(0, drug_config, drugs)

    chw_config['Intervention_Config'] = actual_config

    chw_event = {"class": "CampaignEvent",
                 "Start_Day": start_day,
                 "Event_Coordinator_Config": chw_config,
                 "Nodeset_Config": nodes}

    config_builder.add_event(RawCampaignObject(chw_event))
    return


def get_drug_config(drug, dosing, receiving_drugs_event, drug_ineligibility_duration, expire_recent_drugs) :

    """
    Get the drug dosage configuration.

    Args:
      drug: The drug to administer. Use a str for a single drug or
          a list of str for multiple drugs.
      dosing: The dosing for the drugs (**Dosing_Type** parameter).
      receiving_drugs_event: The event that is broadcast when a drug
        is received (**Broadcast_Event** parameter).
      drug_ineligibility_duration: The number of days to prevent an 
        individual from receiving additional drugs after receiving a 
        drug. 
      expire_recent_drugs: The dictionary that defines the **PropertyValueChanger**
        configuration that is used to set the individual property **DrugStatus**
        to RecentDrug. 

    Returns:
      The dictionary containing the drug configuration and the list of
      drugs to distribute.
    """

    # if drug variable is a list, let's use MultiInterventionDistributor
    if isinstance(drug, str):
        # print('Just a single drug: ' + drug)
        drug_config = {"Cost_To_Consumer": 1,
                       "Drug_Type": drug,
                       "Dosing_Type": dosing,
                       "class": "AntimalarialDrug"}
        drugs = drug
    elif isinstance(drug, list):
        # print('Multiple drugs: ' + '+'.join(drug))
        drugs = []
        for d in drug:
            drugs.append({"Cost_To_Consumer": 1,
                          "Drug_Type": d,
                          "Dosing_Type": dosing,
                          "class": "AntimalarialDrug"})
        drugs.append(receiving_drugs_event)
        if drug_ineligibility_duration > 0 :
            drugs.append(expire_recent_drugs)
        drug_config = {"class": "MultiInterventionDistributor",
                       "Intervention_List": drugs}
    else:
        raise ValueError('Invalid drug input')

    return drug_config, drugs


def build_actual_treatment_cfg(rate, drug_config, drugs) :

"""
Build the drug treatment itself.

Args:
  rate: The rate of distribution (1/**Delay_Period**).
  drug_config: The dictionary describing the drug intervention (
    **AntimalarialDrug**, **MultiInterventionDistributor**, or
    **DelayedIntervention** class).
  drugs: The list of dictionaries that describes the drug intervention
    (**Actual_IndividualIntervention_Configs** parameter).
"""
    if rate > 0:
        actual_config = {
            "class": "DelayedIntervention",
            "Coverage": 1.0,
            "Delay_Distribution": "EXPONENTIAL_DURATION",
            "Delay_Period": 1.0 / rate,
            "Actual_IndividualIntervention_Configs": drugs
        }
    else:
        actual_config = drug_config

    return actual_config