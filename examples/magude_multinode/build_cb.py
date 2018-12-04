# Simplified version of the Magude config builder, as a core geography example.

from examples.magude_multinode.core_cb_setup import basic_gridded_config_builder, set_executable
from examples.magude_multinode.site import add_magude_ento

# Run parameters
simulation_duration_days = 365*10

# Hardcoded:
def build_project_cb():
    cb = basic_gridded_config_builder()
    set_executable(cb, "./inputs/bin/")
    cb.set_input_files_root("./inputs/")
    cb.update_params({
        "Num_Cores": 2,
        "Simulation_Duration": simulation_duration_days,
        "Demographics_Filenames": ["demo.json"],

        "Air_Temperature_Filename": "Mozambique_30arcsec_air_temperature_daily.bin",
        "Land_Temperature_Filename": "Mozambique_30arcsec_air_temperature_daily.bin",
        "Rainfall_Filename": "Mozambique_30arcsec_rainfall_daily.bin",
        "Relative_Humidity_Filename": "Mozambique_30arcsec_relative_humidity_daily.bin",

        "Migration_Model": "FIXED_RATE_MIGRATION",
        "Migration_Pattern": "SINGLE_ROUND_TRIPS",

        "Enable_Local_Migration": 1,
        "x_Local_Migration": 0.2,
        "Local_Migration_Roundtrip_Duration": 2,  # mean of exponential days-at-destination distribution
        "Local_Migration_Roundtrip_Probability": 1,  # fraction that return
        "Local_Migration_Filename": "local_migration.bin",

        'Enable_Regional_Migration': 1,
        'x_Regional_Migration': 0.0405,
        'Regional_Migration_Roundtrip_Duration': 3,
        'Regional_Migration_Roundtrip_Probability': 1,
        'Regional_Migration_Filename': 'regional_migration.bin',


    })

    add_magude_ento(cb)

    # Draw from serialized file.  This is a serialized file run from a calibrated burnin
    cb.update_params({
        "Serialized_Population_Path": "//internal.idm.ctr/IDM/home/jsuresh/input/Magude_Core_Geography_Example/",
        'Serialized_Population_Filenames': ['state-00000-000.dtk','state-00000-001.dtk']
    })
    # [As of writing this code, serialization files could only be staged from COMPS]

    return cb
