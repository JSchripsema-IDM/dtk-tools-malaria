from malaria.interventions.malaria_drugs import drug_params


def configure_adherent_drug(cb, cost=1, doses=[], dose_interval=1,
                            dosing_type="FullTreatmentCourse", adherence_config={}, non_adherence_options=["NEXT_UPDATE"],
                            non_adherence_distribution=[1], max_dose_consideration_duration=40,
                            took_dose_event="Took_Dose"):
    """
        Not setting adherence_config will make the person take the whole drug (same effect as AntimalarialDrug class)
    :param cb: The :py:class:`DTKConfigBuilder <dtk.utils.core.DTKConfigBuilder>` holding the campaign that
    will receive the IRS event
    :param cost: Sets the ``Cost_To_Consumer`` parameter
    :param doses: a list of drug lists for each dose
    ex: [
        [ "DrugA", "DrugB" ],
        [ "DrugA", "DrugB" ],
        [], <--an empty dose, the person would be "skipping" taking anything that day
        [ "DrugC" ],
        [ "DrugD", "DrugD" ]
    ]
    :param dont_allow_duplicates: If an individual's container has an intervention, set to 1 to prevent them from
    receiving another copy of the intervention.
    :param dose_interval: interval between taking defined doses, in dt.
    :param dosing_type: currently, this is one of the DrugUsageType enums, but might change in the future
    :param adherence_config: a dictionary defining WaningEffects or WaningEffectCombo if not defined: all drugs taken
    ex:  {
        "class" : "WaningEffectCombo",
        "Effect_List" : [
            {
                "class": "WaningEffectMapLinearAge",
                "Initial_Effect" : 1.0,
                "Durability_Map" :
                {
                    "Times"  : [ 0.0,  12.99999,  13.0, 125.0 ],
                    "Values" : [ 0.0,   0.0,       1.0,   1.0 ]
                }
            },
            {
                "class": "WaningEffectMapCount",
                "Initial_Effect" : 1.0,
                "Durability_Map" :
                {
                    "Times"  : [ 1.0, 2.0, 3.0 ],
                    "Values" : [ 0.9, 0.7, 0.5 ]
                }
            },
            {
                "class": "WaningEffectExponential",
                "Initial_Effect": 1.0,
                "Decay_Time_Constant" : 7
            }
        ]
    }
    :param took_dose_event: an event that gets sent out every time a dose is taken
    :param non_adherence_options:  This is an array of enums where each enum defines what happens when the user is not adherent.
            if empty, NEXT_UPDATE is used. options: ["STOP", "NEXT_UPDATE", "NEXT_DOSAGE_TIME", "LOST_TAKE_NEXT"]
    :param non_adherence_distribution:  An array of probabilities. There must be one value in this array for each value
            in non_adherence_options. The sum of these values must equal 1.0.
    :param max_dose_consideration_duration: Max_Dose_Consideration_Duration The maximum number of days that an individual will  consider taking the doses of the drug
    :return: the configured AdherentDrug class dictionary
    """
    # built-in default so we can run this function by just putting in the config builder.
    if not adherence_config:
        adherence_config = {  # the default is for person to take everything not matter what age
            "class": "WaningEffectMapLinearAge",
            "Initial_Effect": 1.0,
            "Durability_Map":
                {
                    "Times": [0.0, 125.0],
                    "Values": [1.0, 1.0]
                }
        }

    # "SPA"
    if not doses:
        doses = [["Sulfadoxine", "Pyrimethamine",'Amodiaquine'],
                 ['Amodiaquine'],
                 ['Amodiaquine']]

    already_added = []
    for dose in doses:
        for drug in dose:
            if drug not in already_added:
                cb.config["parameters"]["Malaria_Drug_Params"][drug] = drug_params[drug]
                already_added.append(drug)

    cb.set_param("PKPD_Model", "CONCENTRATION_VERSUS_TIME")

    cb.config["parameters"]["Malaria_Drug_Params"][drug] = drug_params[drug]
    adherent_drug = {
            "class": "AdherentDrug",
            "Cost_To_Consumer": cost,
            "Doses": doses,
            "Dosing_Type": dosing_type,
            "Dose_Interval": dose_interval,
            "Adherence_Config": adherence_config,
            "Non_Adherence_Options": non_adherence_options,
            "Non_Adherence_Distribution": non_adherence_distribution,
            "Max_Dose_Consideration_Duration": max_dose_consideration_duration,
            "Took_Dose_Event": took_dose_event
        }
    return adherent_drug

