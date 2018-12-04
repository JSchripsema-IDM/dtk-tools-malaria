import logging
import pandas as pd
import os

from calibtool.study_sites.site_setup_functions import *
from malaria.study_sites.HouseholdCalibSite import HouseholdCalibSite

logger = logging.getLogger(__name__)


class MapatizyaCalibSite(HouseholdCalibSite):

    prev_by_round = [0.0523, 0.0405, 0.0213, 0.0352, 0.0188, 0.0257]
    risks = [0.123, 0.095, 0.038]

    def __init__(self):
        super(MapatizyaCalibSite, self).__init__('Mapatizya')


    def update_metadata(self):
        setup_file_dir = 'C:/Users/jgerardin/Dropbox/Malaria Team Folder/projects/zambia_households/simulation_setup'

        self.metadata.update( {
            'intervention_coverage_fname': os.path.join(setup_file_dir, 'mapatizya_filled_all_hs_itn_cov.json'),
            'master_df_fname': os.path.join(setup_file_dir, 'mapatizya_filled_all.csv'),
            'distance_matrix_fname': os.path.join(setup_file_dir, 'mapatizya_filled_all_r1_distance_matrix.csv'),
            'msat_by_grid_cell_fname': os.path.join(setup_file_dir, 'mapatizya_hh_msat_coverage.csv')
        } )
        self.metadata.update( { 'rounddays' : [x*60 +self.metadata['msat_day'] - self.metadata['msat_offset'] for x in range(3)] +
                                              [365 + x*60 +self.metadata['msat_day'] - self.metadata['msat_offset'] for x in range(3)],
                                'sp_report_record_start' : 365*self.metadata['burnin']+self.metadata['msat_day']-
                                                     self.metadata['msat_offset'],
                                'distance_testday' : 0,
                                'regions' : ['all'],
                                'numnodes' : 1721,
                                'days_in_month' : [0, 31, 59, 214, 61],
                                'scale_by_month' : [0.6, 0.9, 1, 0.8],
                                } )
        rdf = pd.read_csv(self.metadata['master_df_fname'])
        self.metadata['ignore_nodes'] = list(rdf[~(rdf['in_r1'] == 1)]['ids'].values)
        self.metadata['ignore_nodes'].append(self.metadata['worknode_id'])
        self.reference_dict['prevalence_by_round'].update( {'sim_date' : self.metadata['rounddays'],
                                                            'prev' : self.prev_by_round})
        self.reference_dict['risk_by_distance'].update({'prevalence' : self.prev_by_round[0],
                                                        'risks' : self.risks})

    def get_setup_functions(self):

        self.update_metadata()

        # # prior to 2012 round 1
        itn_dates = [x/12. for x in [96, 36, 24, 12, 6, 3, 0]]
        itn_dates_2012 = [365 * (self.metadata['burnin'] - date) + self.metadata['msat_day'] for date in itn_dates]
        itn_fracs_2012 = [0.821, 0.013, 0.017, 0.015, 0.118, 0.017]
        # # between 2012 r1 and 2013 r1
        itn_dates = [x/12. for x in [12, 8, 6, 3, -6]]
        itn_dates_2013 = [365 * (self.metadata['burnin'] + 1 - date) + self.metadata['msat_day'] for date in itn_dates]
        itn_fracs_2013 = [0.57, 0.25, 0.07, 0.1]
        # # 2014 June mass distribution
        itn_dates = [x/12. for x in [18, 12, 6, 3, 0]]
        itn_dates_2014 = [365 * (self.metadata['burnin'] + 2 - date) + 335 for date in itn_dates]
        itn_fracs_2014 = [0.057, 0.485, 0.404, 0.054]

        cs = HouseholdCalibSite('Mapatizya')
        base_setup_functions = cs.get_setup_functions()
        work_node_setup_functions = cs.get_worknode_setup_functions()
        msat_setup_functions = self.get_msat_setup_functions()

        site_setup_functions = [
            update_params( {
                "Air_Temperature_Filename": "Household/Mapatizya/Mapatizya_filled_all_air_temperature_daily.bin",
                "Land_Temperature_Filename": "Household/Mapatizya/Mapatizya_filled_all_air_temperature_daily.bin",
                "Rainfall_Filename": "Household/Mapatizya/Mapatizya_filled_all_rainfall_daily.bin",
                "Relative_Humidity_Filename": "Household/Mapatizya/Mapatizya_filled_all_humidity_daily.bin",

                "Local_Migration_Filename": "Household/Mapatizya_Local_Human_Migration.bin",
                "Sea_Migration_Filename": "Household/Mapatizya_Work_Migration.bin",
                "Vector_Migration_Filename_Local": "Household/Mapatizya_Local_Vector_Migration.bin",
                "Vector_Migration_Filename_Regional": "Household/Mapatizya_Regional_Vector_Migration.bin",
                "x_Local_Migration": 2.2,
                "x_Sea_Migration": 1,

                "Demographics_Filenames": ['Household/Mapatizya_filled_demographics_all_prop_NPwork_CHWcatch_access.json']
            } ),
            config_setup_fn(duration=365 * (self.metadata['burnin'] + self.metadata['sim_years'])),
            filtered_report_fn(start=365 * self.metadata['burnin'],
                               end=365 * (self.metadata['burnin'] + self.metadata['sim_years']),
                               nodes=range(self.metadata['numnodes'])),
            # event_counter_report_fn(['Received_Campaign_Drugs'],
            #                         start=365 * self.metadata['burnin'],
            #                         duration=365 * self.metadata['sim_years'],
            #                         nodes={'Node_List': list(range(self.metadata['numnodes'])),
            #                                "class": "NodeSetNodeList"}),
            filtered_report_fn(start=365 * self.metadata['burnin'],
                               end=365 * (self.metadata['burnin'] + self.metadata['sim_years']),
                               nodes=[self.metadata['worknode_id']], description='worknode'),
            filtered_spatial_report_fn(start=self.metadata['sp_report_record_start'],
                                       end=self.metadata['sp_report_record_start']+1,
                                       channels=["Population", 'New_Diagnostic_Prevalence'],
                                       nodes=[x for x in range(self.metadata['numnodes']) if x not in self.metadata['ignore_nodes']]),
            add_itn_by_node_id_fn(self.metadata['intervention_coverage_fname'], itn_dates_2012, itn_fracs_2012, 'itn2012cov',
                                  waning={'Usage_Config': {"Expected_Discard_Time": 270}}),
            add_itn_by_node_id_fn(self.metadata['intervention_coverage_fname'], itn_dates_2013, itn_fracs_2013, 'itn2013cov',
                                  waning={'Usage_Config': {"Expected_Discard_Time": 270}}),
            add_itn_by_node_id_fn(self.metadata['intervention_coverage_fname'], itn_dates_2014, itn_fracs_2014, 'itn2014cov',
                                  waning={'Usage_Config': {"Expected_Discard_Time": 270}}),
            # add_drug_campaign_fn('MSAT', 'AL',
            #                      [365 * (self.metadata['burnin'] + x) + self.metadata['rounddays'][0] for x in [0, 1]],
            #                      repetitions=3, interval=60, coverage=0.5, delay=self.metadata['msat_offset'],
            #                      drug_ineligibility_duration=14, diagnostic_type='Other', diagnostic_threshold=40,
            #                      node_property_restrictions=[{'NodeType': 'Local'}]),
            add_seasonal_HS_by_NP_fn(self.metadata['intervention_coverage_fname'], channel='hscov',
                                     start_day=(self.metadata['burnin']-5)*365,
                                     days_in_month=self.metadata['days_in_month'],
                                     scale_by_month=self.metadata['scale_by_month'],
                                     duration_years=5+self.metadata['sim_years']),

        ]

        return base_setup_functions + site_setup_functions + work_node_setup_functions + msat_setup_functions

    def get_msat_setup_functions(self):
        df = pd.read_csv(self.metadata['msat_by_grid_cell_fname'])
        setup_fns = [
            add_drug_campaign_fn('MSAT', 'AL',
                                 [365 * self.metadata['burnin'] + date],
                                 repetitions=3, interval=60, coverage=cov, delay=self.metadata['msat_offset'],
                                 drug_ineligibility_duration=14, diagnostic_type='Other', diagnostic_threshold=40,
                                 nodes=[int(x) for x in gdf['ids']],
                                 node_property_restrictions=[{'NodeType': 'Local'}])
            for (date, cov), gdf in df.groupby(['simdate', 'cov_rd'])
        ]
        return setup_fns

