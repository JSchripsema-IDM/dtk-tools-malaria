params = {
    "Infection_Updates_Per_Timestep": 8, ###
    "Enable_Superinfection": 1,

    "Mean_Sporozoites_Per_Bite": 11,
    "Base_Sporozoite_Survival_Fraction": 0.25,
    "Base_Incubation_Period": 7, ###
    "Merozoites_Per_Hepatocyte": 15000,

    "Antibody_IRBC_Kill_Rate": 1.596,
    "RBC_Destruction_Multiplier": 3.29,  # 3.5756
    "Merozoites_Per_Schizont": 16,
    "Parasite_Switch_Type": "RATE_PER_PARASITE_7VARS",

    # 150305 calibration by JG to Burkina data + 6 of Kevin's sites
    # N.B: severe disease re-calibration not done
    # 'Base_Gametocyte_Production_Rate': 0.044,
    # "Gametocyte_Stage_Survival_Rate": 0.82,
    # 'Antigen_Switch_Rate': 2.96e-9,
    # 'Falciparum_PfEMP1_Variants': 1112,
    # 'Falciparum_MSP_Variants': 7,
    # 'MSP1_Merozoite_Kill_Fraction': 0.43,
    # 'Falciparum_Nonspecific_Types': 90,
    # 'Nonspecific_Antigenicity_Factor': 0.42,
    # 'Base_Gametocyte_Mosquito_Survival_Rate': 0.00088,
    # "Max_Individual_Infections": 5,

    #180824 Prashanth parameters [description?]
    'Antigen_Switch_Rate': pow(10, -9.116590124),
    'Base_Gametocyte_Production_Rate': 0.06150582,
    'Base_Gametocyte_Mosquito_Survival_Rate': 0.002011099,
    'Falciparum_MSP_Variants': 32,
    'Falciparum_Nonspecific_Types': 76,
    'Falciparum_PfEMP1_Variants': 1070,
    'Gametocyte_Stage_Survival_Rate': 0.588569307,
    'MSP1_Merozoite_Kill_Fraction': 0.511735322,
    'Max_Individual_Infections': 3,
    'Nonspecific_Antigenicity_Factor': 0.415111634,

    "Number_Of_Asexual_Cycles_Without_Gametocytes": 1,
    "Base_Gametocyte_Fraction_Male": 0.2,
    "Enable_Sexual_Combination": 0
}
