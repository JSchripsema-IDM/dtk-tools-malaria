# Magude config builder

import numpy as np
import seaborn as sns
import pandas as pd

from malaria.reports.MalariaReport import add_filtered_report, add_event_counter_report, add_filtered_spatial_report
from dtk.interventions.input_EIR import add_InputEIR
from dtk.vector.species import set_species_param

from malaria_toolbox import GriddedConfigBuilder


class MozambiqueExperiment(GriddedConfigBuilder):

    def __init__(self,
                 sim_start_date,
                 sim_length_days,
                 num_cores=1,
                 demo_fp='demo.json',
                 local_migration_on=True,
                 regional_EIR_node_migration_on=True,
                 use_climate_files=False,
                 verbose=True,
                 healthseek_fn=None,
                 itn_fn=None,
                 irs_fn=None,
                 msat_fn=None,
                 mda_fn=None,
                 stepd_fn=None,
                 filter_length_days=5475, #15 years
                 regional_EIR_node_label=100000,
                 regional_EIR_node_lat=-25.045777,
                 regional_EIR_node_lon=32.786861,
                 regional_EIR_scale_factor=0.5):

        # For now, assume that we are only/always running Magude
        # self.catch = catch
        self.catch = 'Magude-Sede-Facazissa'
        self.regional_EIR_node_migration_on = regional_EIR_node_migration_on
        self.regional_EIR_node_label = regional_EIR_node_label
        self.regional_EIR_node_lat = regional_EIR_node_lat
        self.regional_EIR_node_lon = regional_EIR_node_lon
        self.regional_EIR_scale_factor = regional_EIR_scale_factor
        self.filter_length_days = filter_length_days

        catch_cells = MozambiqueExperiment.find_cells_for_this_catchment(self.catch)

        super().__init__(sim_start_date,
                         sim_length_days,
                         num_cores=num_cores,
                         demo_fp=demo_fp,
                         local_migration_on= local_migration_on,
                         use_climate_files=use_climate_files,
                         climate_region="Mozambique",
                         verbose=verbose)

        self.mozambique_setup()


    def add_ento_to_cb(self):
        # Vector properties:
        self.cb.update_params({'Vector_Species_Names': ['arabiensis', 'funestus']})

        # Arabiensis
        set_species_param(self.cb, 'arabiensis', 'Indoor_Feeding_Fraction', 0.5)
        set_species_param(self.cb, 'arabiensis', 'Adult_Life_Expectancy', 20)
        set_species_param(self.cb, 'arabiensis', 'Anthropophily', 0.65)
        set_species_param(self.cb, 'arabiensis', 'Larval_Habitat_Types',
                          {
                              "LINEAR_SPLINE": {
                                  "Capacity_Distribution_Number_Of_Years": 1,
                                  "Capacity_Distribution_Over_Time": {
                                      # "Capacity_Distribution_Per_Year": {
                                      "Times": [0.0, 30.417, 60.833, 91.25, 121.667, 152.083, 182.5, 212.917, 243.333, 273.75, 304.167, 334.583],
                                      "Values": [1]*12
                                      # "Values": [0.0429944166751962,
                                      #            0.145106159922212,
                                      #            0.220520011001099,
                                      #            0.318489404300663,
                                      #            0.0617610600835594,
                                      #            0.0462380862878181,
                                      #            0.0367590381502996,
                                      #            0.02474944109524821,
                                      #            0.0300445801767523,
                                      #            0.021859890543704,
                                      #            0.0261404367939001,
                                      #            0.0253992634551118
                                      #            ]
                                  },
                                  "Max_Larval_Capacity": pow(10, 8.42) # Uncertain-- this exponent is what we calibrate for
                              }
                          })


        # Funestus
        set_species_param(self.cb, 'funestus', "Indoor_Feeding_Fraction", 0.9)
        set_species_param(self.cb, 'funestus', 'Adult_Life_Expectancy', 20)
        set_species_param(self.cb, 'funestus', 'Anthropophily', 0.65)
        set_species_param(self.cb, 'funestus', 'Larval_Habitat_Types', {
            "WATER_VEGETATION": 2e3,
            "LINEAR_SPLINE": {
                "Capacity_Distribution_Number_Of_Years": 1,
                "Capacity_Distribution_Over_Time": {
                    # "Capacity_Distribution_Per_Year": {
                    "Times": [0.0, 30.417, 60.833, 91.25, 121.667, 152.083, 182.5, 212.917, 243.333, 273.75, 304.167, 334.583],

                    # Prashanth's new spline: stand-alone
                    "Values": [1] * 12
                    # "Values": [0.00100058388478598,
                    #            0.0555791772797765,
                    #            0.0136439353956828,
                    #            0.0819954534745384,
                    #            0.0987507679669904,
                    #            0.08541870494461,
                    #            0.126723162372031,
                    #            0.0847818298332663,
                    #            0.249125024283648,
                    #            0.105551476581602,
                    #            0.0564097715821499,
                    #            0.0423232369866486
                    #            ]
                },
                "Max_Larval_Capacity": pow(10, 7.44) # Uncertain-- this exponent was what we calibrate for
            }
        })


    def add_filtered_reports(self):
        # Special filtered reports that select out the end of the simulation, which will be comparable for both burnins and serialization runs

        if self.filter_length_days > self.sim_length_days:
            print("WARNING: specified filter {} is larger than simulation length {}".format(self.filter_length_days, self.sim_length_days))
            print("Hence, will not create any filtered reports.")
        else:
            print("Adding special filtered reports for last {} days of simulation".format(self.filter_length_days))
            # Spatial filtered report for grid-level prevalence comparison.  Filter always selects out the last filter_length_days
            add_filtered_spatial_report(self.cb,
                                        start=self.sim_length_days - self.filter_length_days,
                                        end=self.sim_length_days,
                                        channels=['Population', 'True_Prevalence'])

            # Nonspatial version is for HF-level incidence comparison
            add_filtered_report(self.cb,
                                start=self.sim_length_days - self.filter_length_days,
                                end=self.sim_length_days)

            # Add filter report for prevalence in each bairro
            bairro_df = MozambiqueExperiment.find_bairros_for_this_catchment(self.catch)
            foo = bairro_df.groupby('bairro')

            for (bairro_num,df) in foo:
                add_filtered_report(self.cb,
                                    start=self.filter_time_start,
                                    end=(self.filter_time_start + self.filter_duration),
                                    nodes=[int(x) for x in df['grid_cell'].values],
                                    description=str(int(bairro_num)))

            bairro_dict = MozambiqueExperiment.find_bairros_for_this_catchment(self.catch)
            for bairro_name in bairro_dict["bairro_name_list"]:
                add_filtered_report(self.cb,
                                    start=self.filter_time_start,
                                    end=(self.filter_time_start+self.filter_duration),
                                    nodes=bairro_dict[bairro_name],
                                    description=bairro_name)



    def mozambique_setup(self):
        self.africa_setup()
        self.add_ento_to_cb()
        self.add_filtered_reports()

        # Local migration amplitude:
        self.cb.update_params({
            "x_Local_Migration": 4
        })

        # Regional migration node
        if self.regional_EIR_node_migration_on:
            self.add_regional_EIR_node()



    def add_regional_EIR_node(self):
        # From Jaline

        self.cb.update_params({
            'Enable_Regional_Migration': 1,
            'Regional_Migration_Roundtrip_Duration': 3,
            'Regional_Migration_Roundtrip_Probability': 1,
            'x_Regional_Migration': 0.0405,
            'Regional_Migration_Filename': 'Migration/_Regional_Migration.bin',
        })

        monthly_profile = [12.1, 23.9, 33.5, 14.8, 6.8, 4.9, 3.3, 3.8, 3.5, 3.3, 2.8, 4.3]
        add_InputEIR(self.cb,
                     monthlyEIRs=[x * self.EIR_scale_factor for x in monthly_profile],
                     nodes={'class': 'NodeSetNodeList', 'Node_List': [self.EIR_node_label]},
                     start_day=self.EIR_start_day)


        add_filtered_report(self.cb, nodes=[self.EIR_node_label], description='Work')
        # add_filtered_report(self.cb, nodes=grid_cell_ids, description=catchment)



    def larval_params_func_for_calibration(self, grid_cells):
        return {"LINEAR_SPLINE": np.ones_like(grid_cells)}
                # "WATER_VEGETATION": np.ones_like(grid_cells),
                # "TEMPORARY_RAINFALL": np.ones_like(grid_cells)}


    # Grid-cell/Node ID
    @staticmethod
    def find_cells_for_this_catchment(catch, base='../../'):
        # Find which grid cells correspond to a given HFCA
        df = pd.read_csv(base + "data/mozambique/grid_lookup_with_neighborhood.csv")

        if catch == 'all':
            return np.array(df['grid_cell'])
        else:
            df_catch = df[df['catchment'] == catch]
            return np.array(df_catch['grid_cell'])

    @staticmethod
    def find_pops_for_catch(catch, base='../../'):
        cells = MozambiqueExperiment.find_cells_for_this_catchment(catch, base=base)

        pop_df = pd.read_csv(base + "data/mozambique/grid_population")

        return np.array(pop_df[np.in1d(pop_df['node_label'],cells)]['pop'])


    @staticmethod
    def find_bairros_for_this_catchment(catch, base='../../'):
        bairro_csv = base + "data/mozambique/grid_lookup_with_neighborhood.csv"
        bairro_data = pd.read_csv(bairro_csv)

        return_data = bairro_data[bairro_data["catchment"]==catch]
        return return_data



    @staticmethod
    def catch_3_yr_spline(catch, species, dropbox_base="C:/Users/jsuresh/Dropbox (IDM)/Malaria Team Folder/projects/Mozambique/entomology_calibration/"):
        # Read spline directly from mini-CSV files generated by Jaline/Caitlin

        def load_raw_spline(csv_df):
            spline = np.zeros(36)
            raw_spline = np.array(csv_df["Values"])
            spline[4:35] = raw_spline[1:-1] # Throw out first and last entry
            return spline

        def fill_out_spline(spline):
            spline[0:4] = 0.5 * (spline[12:16] + spline[24:28])
            spline[35] = 0.5 * (spline[11]+spline[23])
            return spline
        # def fill_out_spline(spline):
        #     # Account for the fact that we only really trust the data from indices 4-35 (May 15 - Nov 17)
        #     # Reconstruct shape and amplitude of missing data by inferring from other
        #     year1_factor = spline[4:11].sum()
        #     year2_factor = spline[16:23].sum()
        #     year3_factor = spline[28:35].sum()
        #
        #     spline_inferred = spline.copy()
        #
        #     spline_inferred[0:4] = year1_factor * 0.5 * (spline[12:16] / year2_factor + spline[24:28] / year3_factor)
        #     spline_inferred[35] = year3_factor * 0.5 * (spline[11] / year1_factor + spline[23] / year2_factor)
        #
        #     return spline_inferred


        ento_base = dropbox_base + "Multi_year_calibration_by_HFCA_180404/best_180410/"
        # ento_base = dropbox_base + "Multi_year_calibration_by_HFCA_180404/best_180409/"



        if species == "arabiensis":
            species = "gambiae"


        if species == "funestus":
            df = pd.read_csv(ento_base + "funestus.csv")
            spline = fill_out_spline(load_raw_spline(df))
        elif species == "gambiae":
            if catch == "Panjane-Caputine":
                df = pd.read_csv(ento_base + "{}_{}.csv".format("Panjane", species))
                spline = fill_out_spline(load_raw_spline(df))
            elif catch == "Magude-Sede-Facazissa":
                df = pd.read_csv(ento_base + "{}_{}.csv".format("Magude-Sede", species))
                spline = fill_out_spline(load_raw_spline(df))
            elif catch != "Moine" and catch != "Mahel":
                df = pd.read_csv(ento_base + "{}_{}.csv".format(catch, species))
                spline = fill_out_spline(load_raw_spline(df))
            elif catch == "Moine" or catch == "Mahel":
                panjane_df = pd.read_csv(ento_base + "{}_{}.csv".format("Panjane", species))
                chichuco_df = pd.read_csv(ento_base + "{}_{}.csv".format("Chichuco", species))
                panjane_spline = fill_out_spline(load_raw_spline(panjane_df))
                chichuco_spline = fill_out_spline(load_raw_spline(chichuco_df))

                spline = (panjane_spline + chichuco_spline)/2.

        # Return associated times:
        times_1yr = np.array([0.0, 30.417, 60.833, 91.25, 121.667, 152.083, 182.5, 212.917, 243.333, 273.75, 304.167, 334.583])
        times = np.append(times_1yr, times_1yr + 365)
        times = np.append(times, times_1yr + 365 * 2)
        times = list(times)

        return [times, list(spline)]





    @staticmethod
    def catch_3_yr_spline_GatesReview(catch, species, dropbox_base="C:/Users/jsuresh/Dropbox (IDM)/Malaria Team Folder/projects/Mozambique/entomology_calibration/"):
        # Read spline directly from mini-CSV files generated by Jaline/Caitlin

        def load_raw_spline(csv_df):
            spline = np.zeros(36)
            raw_spline = np.array(csv_df["Values"])
            spline[4:35] = raw_spline[1:-1] # Throw out first and last entry
            return spline

        def fill_out_spline(spline):
            spline[0:4] = 0.5 * (spline[12:16] + spline[24:28])
            spline[35] = 0.5 * (spline[11]+spline[23])
            return spline
        # def fill_out_spline(spline):
        #     # Account for the fact that we only really trust the data from indices 4-35 (May 15 - Nov 17)
        #     # Reconstruct shape and amplitude of missing data by inferring from other
        #     year1_factor = spline[4:11].sum()
        #     year2_factor = spline[16:23].sum()
        #     year3_factor = spline[28:35].sum()
        #
        #     spline_inferred = spline.copy()
        #
        #     spline_inferred[0:4] = year1_factor * 0.5 * (spline[12:16] / year2_factor + spline[24:28] / year3_factor)
        #     spline_inferred[35] = year3_factor * 0.5 * (spline[11] / year1_factor + spline[23] / year2_factor)
        #
        #     return spline_inferred


        ento_base = dropbox_base + "Multi_year_calibration_by_HFCA_180404/best_180410/"
        # ento_base = dropbox_base + "Multi_year_calibration_by_HFCA_180404/best_180409/"



        if species == "arabiensis":
            species = "gambiae"


        if species == "funestus":
            df = pd.read_csv(ento_base + "funestus.csv")
            spline = fill_out_spline(load_raw_spline(df))
        elif species == "gambiae":
            if catch == "Panjane-Caputine":
                df = pd.read_csv(ento_base + "{}_{}.csv".format("Panjane", species))
                spline = fill_out_spline(load_raw_spline(df))
            elif catch == "Magude-Sede-Facazissa":
                df = pd.read_csv(ento_base + "{}_{}.csv".format("Magude-Sede", species))
                spline = fill_out_spline(load_raw_spline(df))
            elif catch != "Moine" and catch != "Mahel":
                df = pd.read_csv(ento_base + "{}_{}.csv".format(catch, species))
                spline = fill_out_spline(load_raw_spline(df))
            elif catch == "Moine" or catch == "Mahel":
                panjane_df = pd.read_csv(ento_base + "{}_{}.csv".format("Panjane", species))
                chichuco_df = pd.read_csv(ento_base + "{}_{}.csv".format("Chichuco", species))
                panjane_spline = fill_out_spline(load_raw_spline(panjane_df))
                chichuco_spline = fill_out_spline(load_raw_spline(chichuco_df))

                spline = (panjane_spline + chichuco_spline)/2.

        # Return associated times:
        times_1yr = np.array([0.0, 30.417, 60.833, 91.25, 121.667, 152.083, 182.5, 212.917, 243.333, 273.75, 304.167, 334.583])
        times = np.append(times_1yr, times_1yr + 365)
        times = np.append(times, times_1yr + 365 * 2)
        times = list(times)

        return [times, list(spline)]




    @staticmethod
    def LL_compression(LL):
        # Mapping from real numbers to [0,1] which compresses possible range of LL values.

        def LL_compression_sigmoid(x,x0=-30,x1=-2,y0=0.1,y1=0.9):
            g = np.log(y1/y0)
            a = 2*g/(x1-x0)
            b = -g*(x0+x1)/(x1-x0)

            return np.exp(a*x+b)/(np.exp(a*x+b)+1)

        return LL_compression_sigmoid(LL)


    @staticmethod
    def save_figs_for_caitlin(fig,savefile):
        # Get current date, to add "0418", etc.
        with sns.axes_style("darkgrid"):
            fig.savefig(savefile + ".png")

        with sns.axes_style("white"):
            fig.savefig(savefile + ".pdf")


#################################################################################################
# INTERVENTIONS (ADDITIONS TO CAMPAIGN FILE)

def add_healthseeking(self, cb, healthseek_fn):
    # Implement basic health-seeking behavior for all individuals in simulation

    # Event information files
    healthseek_events = pd.read_csv(self.healthseek_fn)
    healthseek_events['simday'] = [convert_to_day(x, self.sim_start_date, "%Y-%m-%d") for x in
                                   healthseek_events.fulldate]
    healthseek_events = healthseek_events[np.in1d(healthseek_events['grid_cell'], self.demo_cells)]
    healthseek_events.reset_index(inplace=True)

    binned_and_grouped = self.try_campaign_compression(healthseek_events)

    for table, group in binned_and_grouped:
        node_list = group['grid_cell']
        if sorted(node_list) == self.demo_cells:
            node_dict = {"class": "NodeSetAll"}
        else:
            node_dict = {"class": "NodeSetNodeList", "Node_List": node_list}

        add_health_seeking(cb,
                           start_day=float(table['simday']),
                           targets=[{'trigger': 'NewClinicalCase',
                                     'coverage': float(table['cov_newclin_youth']),
                                     'agemin': 0,
                                     'agemax': 5,
                                     'seek': 1,
                                     'rate': 0.3},
                                    {'trigger': 'NewClinicalCase',
                                     'coverage': float(table['cov_newclin_adult']),
                                     'agemin': 5,
                                     'agemax': 100,
                                     'seek': 1,
                                     'rate': 0.3},
                                    {'trigger': 'NewSevereCase',
                                     'coverage': float(table['cov_severe_youth']),
                                     'agemin': 0,
                                     'agemax': 5,
                                     'seek': 1, 'rate': 0.5},
                                    {'trigger': 'NewSevereCase',
                                     'coverage': float(table['cov_severe_adult']),
                                     'agemin': 5,
                                     'agemax': 100,
                                     'seek': 1,
                                     'rate': 0.5}],
                           drug=['Artemether', 'Lumefantrine'],
                           dosing='FullTreatmentNewDetectionTech',
                           nodes=node_dict,
                           duration=float(table['duration']))


def add_itns(self, cb):
    # def convert_to_birth_itn_df(itn_df):
    #     # Go by row:
    #

    itn_events = pd.read_csv(self.itn_fn)
    itn_events['simday'] = [convert_to_day(x, self.sim_start_date, "%Y-%m-%d") for x in itn_events.fulldate]
    itn_events = itn_events[np.in1d(itn_events['grid_cell'], self.demo_cells)]
    itn_events.reset_index(inplace=True)

    binned_and_grouped = self.try_campaign_compression(itn_events[itn_events['simday'] >= 0])

    for table, group in binned_and_grouped:
        node_list = group['grid_cell']
        if sorted(node_list) == self.demo_cells:
            nodeIDs = []
        else:
            nodeIDs = node_list

        # Regular bednet distribution
        add_ITN_age_season(cb,
                           start=float(row['simday']),
                           age_dep={'youth_cov': float(table['age_cov']),
                                    'youth_min_age': 5,
                                    'youth_max_age': 20},
                           coverage_all=float(table['cov_all']),
                           as_birth=False,
                           seasonal_dep={'min_cov': float(table['min_season_cov']),
                                         'max_day': 1},
                           discard={'halflife1': 260,
                                    'halflife2': 2106,
                                    'fraction1': float(table['fast_fraction'])},
                           nodeIDs=nodeIDs)

    # Separately handle birth nets:
    birth_itn_events = itn_events.copy(deep=True)
    for r, row in itn_events.iterrows():
        pass
        # birth_itn_events[]
    # For each node, find earliest and last

    for r, row in itn_events.iterrows():
        # Add non-birth nets
        add_ITN_age_season(cb, start=float(row['simday']),
                           age_dep={'youth_cov': float(row['age_cov']), 'youth_min_age': 5,
                                    'youth_max_age': 20},
                           coverage_all=float(row['cov_all']),
                           as_birth=False,
                           seasonal_dep={'min_cov': float(row['min_season_cov']), 'max_day': 1},
                           discard={'halflife1': 260, 'halflife2': 2106,
                                    'fraction1': float(row['fast_fraction'])},
                           nodeIDs=[row['grid_cell']])
        # Add birth nets
        try:
            birth_duration = float(itn_events['simday'][itn + 1] - itn_events['simday'][itn] - 1)
        except:
            birth_duration = -1

        if itn < (len(itn_events) - 1) and (itn_events['grid_cell'][itn + 1] == itn_events['grid_cell'][itn]):
            birth_duration = float(itn_events['simday'][itn + 1] - itn_events['simday'][itn] - 1)
        else:
            birth_duration = -1

        add_ITN_age_season(cb, start=float(itn_events['simday'][itn]),
                           age_dep={'youth_cov': float(itn_events['age_cov'][itn]), 'youth_min_age': 5,
                                    'youth_max_age': 20},
                           coverage_all=float(itn_events['cov_all'][itn]),
                           as_birth=True,
                           seasonal_dep={'min_cov': float(itn_events['min_season_cov'][itn]), 'max_day': 60},
                           discard={'halflife1': 260, 'halflife2': 2106,
                                    'fraction1': float(itn_events['fast_fraction'][itn])},
                           duration=birth_duration,
                           nodeIDs=[itn_events['grid_cell'][itn]])


def add_irs(self, cb):
    irs_events = pd.read_csv(self.irs_fn)
    irs_events['simday'] = [convert_to_day(x, start_date, date_format) for x in irs_events.fulldate]
    irs_events = irs_events[np.in1d(irs_events['grid_cell'], self.demo_cells)]
    irs_events.reset_index(inplace=True)

    binned_and_grouped = self.try_campaign_compression(irs_events)

    for table, group in binned_and_grouped:
        node_list = group['grid_cell']
        if sorted(node_list) == self.demo_cells:
            nodeIDs = []
        else:
            nodeIDs = node_list

        add_IRS(cb, start=int(table['simday']),
                coverage_by_ages=[{'coverage': float(table['cov_all'])}],
                waning={"Killing_Config": {
                    "Initial_Effect": float(table['killing']),
                    "Decay_Time_Constant": float(table['exp_duration']),
                    "Box_Duration": float(table['box_duration']),
                    "class": "WaningEffectBoxExponential"
                }},
                nodeIDs=nodeIDs)


def add_msat(self, cb):
    msat_events = pd.read_csv(self.msat_fn)
    msat_events['simday'] = [convert_to_day(x, start_date, date_format) for x in msat_events.fulldate]
    msat_events = msat_events[np.in1d(msat_events['grid_cell'], self.demo_cells)]
    msat_events.reset_index(inplace=True)

    for msat in range(len(msat_events)):
        add_drug_campaign(cb, campaign_type='MSAT', drug_code='AL',
                          start_days=[float(msat_events['simday'][msat])],
                          coverage=msat_events['cov_all'][msat], repetitions=1, interval=60,
                          nodes=[nodeid_lookup[msat_events['grid_cell'][msat]]])


def add_mda(self, cb):
    mda_events = pd.read_csv(self.mda_fn)
    mda_events['simday'] = [convert_to_day(x, start_date, date_format) for x in mda_events.fulldate]
    mda_events = mda_events[np.in1d(mda_events['grid_cell'], self.demo_cells)]
    mda_events.reset_index(inplace=True)

    for mda in range(len(mda_events)):
        add_drug_campaign(cb, campaign_type='MDA', drug_code='DP',
                          start_days=[float(mda_events['simday'][mda])],
                          coverage=float(mda_events['cov_all'][mda]), repetitions=1, interval=60,
                          nodes=[nodeid_lookup[mda_events['grid_cell'][mda]]])


def add_rcd(self, cb):
    stepd_events = pd.read_csv(self.stepd_fn)
    stepd_events['simday'] = [convert_to_day(x, start_date, date_format) for x in stepd_events.fulldate]
    stepd_events = stepd_events[np.in1d(stepd_events['grid_cell'], self.demo_cells)]
    stepd_events.reset_index(inplace=True)

    for sd in range(len(stepd_events)):
        # cov = np.min([1.,float(rcd_people_num) / float(pop_lookup[stepd_events['grid_cell'][sd]])])
        add_drug_campaign(cb, campaign_type='rfMSAT', drug_code='AL',
                          start_days=[float(stepd_events['simday'][sd])],
                          coverage=float(stepd_events['coverage'][sd]),
                          trigger_coverage=float(stepd_events['trigger_coverage'][sd]),
                          # coverage=cov,
                          interval=float(stepd_events['interval'][sd]),
                          nodes=[nodeid_lookup[stepd_events['grid_cell'][sd]]])


def try_campaign_compression(self, intervention_df, bin_fidelity=0.05):
    # Because implementing things on a grid_cell level leads to enormous campaign files, try to group things together wherever possible
    def round_nearest(x, a):
        return round(round(x / a) * a, -int(math.floor(math.log10(a))))

    binned_intervention_df = intervention_df.copy(deep=True)

    # Bin all fields other than grid_cell and date:
    field_list = list(intervention_df.columns)
    field_list.remove(['grid_cell', 'fulldate', 'simday'])

    # Bin these fields with bin width = bin_fidelity
    for field in field_list:
        binned_intervention_df[field] = intervention_df[field].map(lambda x: round_nearest(x, bin_fidelity))

    # Group by the new binned fields, as well as by date
    grouped_by_fields = ['simday'] + field_list
    binned_and_grouped = binned_intervention_df.groupby(grouped_by_fields)

    return binned_and_grouped


def implement_interventions(self, cb):
    include_healthseek = False
    include_itn = False
    include_irs = False
    include_msat = False
    include_mda = False
    include_rcd = False

    for fn in ['healthseek_fn', 'itn_fn', 'irs_fn', 'mda_fn', 'msat_fn', 'rcd_fn']:
        if fn in self.kwargs:
            if fn == 'healthseek_fn':
                include_healthseek = True
                self.add_healthseeking(cb, self.kwargs[fn])
            elif fn == 'itn_fn':
                include_itn = True
                self.add_itns(cb, self.kwargs[fn])
            elif fn == 'irs_fn':
                include_irs = True
                self.add_irs(cb, self.kwargs[fn])
            elif fn == 'mda_fn':
                include_mda = True
                self.add_mda(cb, self.kwargs[fn])
            elif fn == 'msat_fn':
                include_msat = True
                self.add_msat(cb, self.kwargs[fn])
            elif fn == 'rcd_fn':
                include_rcd = True
                self.add_rcd(cb, self.kwargs[fn])

        else:
            if self.verbose:
                print("Warning: No {} specified.".format(fn))

    return {"HS": include_healthseek,
            "ITN": include_itn,
            "IRS": include_irs,
            "MSAT": include_msat,
            "MDA": include_mda,
            "RCD": include_rcd}


#################################################################################################
# ONCE CB IS BUILT, FUNCTIONS FOR WHAT TO DO WITH IT

def vector_migration_sweeper(self, vector_migration_on):
    if vector_migration_on:
        self.cb.update_params({
            'Vector_Migration_Modifier_Equation': 'LINEAR',
            'Vector_Sampling_Type': 'SAMPLE_IND_VECTORS',  # individual vector model (required for vector migration)
            'Mosquito_Weight': 10,
            'Enable_Vector_Migration': 1,  # mosquito migration
            'Enable_Vector_Migration_Local': 1,
        # migration rate hard-coded in NodeVector::processEmigratingVectors() such that 50% total leave a 1km x 1km square per day (evenly distributed among the eight adjacent grid cells).
            'Vector_Migration_Base_Rate': 0.15,  # default is 0.5
            'x_Vector_Migration_Local': 1
        })
    else:
        self.cb.update_params({
            'Enable_Vector_Migration': 0,  # mosquito migration
            'Enable_Vector_Migration_Local': 0
            # migration rate hard-coded in NodeVector::processEmigratingVectors() such that 50% total leave a 1km x 1km square per day (evenly distributed among the eight adjacent grid cells).
        })
    return {"vec_migr": vector_migration_on}


def submit_experiment(self,
                      cb,
                      num_seeds=1,
                      intervention_sweep=False,
                      migration_sweep=False,
                      vector_migration_sweep=False,
                      simple_intervention_sweep=False,
                      custom_name=None):
    # Implement the actual (not dummy) baseline healthseeking
    self.implement_baseline_healthseeking(cb)

    modlists = []

    if num_seeds > 1:
        new_modlist = [ModFn(DTKConfigBuilder.set_param, 'Run_Number', seed) for seed in range(num_seeds)]
        modlists.append(new_modlist)

    if migration_sweep:
        new_modlist = [ModFn(DTKConfigBuilder.set_param, 'x_Local_Migration', x) for x in [0.5, 1, 5, 10]]
        modlists.append(new_modlist)

    if vector_migration_sweep:
        new_modlist = [ModFn(self.vector_migration_sweeper, vector_migration_on) for vector_migration_on in
                       [True, False]]
        modlists.append(new_modlist)

    if simple_intervention_sweep:
        new_modlist = [
            ModFn(self.implement_interventions, True, False, False, False, False),
            ModFn(self.implement_interventions, False, True, False, False, False),
            ModFn(self.implement_interventions, False, False, True, False, False),
            ModFn(self.implement_interventions, False, False, False, True, False),
            ModFn(self.implement_interventions, False, False, False, False, True),
            ModFn(self.implement_interventions, True, True, True, True, True)
        ]
        modlists.append(new_modlist)
    else:
        # new_modlist = [ModFn(self.implement_interventions, True, True, True, True, True)]
        new_modlist = [ModFn(self.implement_interventions, True, True, False, False, False)]
        modlists.append(new_modlist)

    builder = ModBuilder.from_combos(*modlists)

    run_name = self.exp_name
    if custom_name:
        run_name = custom_name

    # SetupParser.init()
    # SetupParser.set("HPC","priority","Normal")
    # exp_manager = ExperimentManagerFactory.init()
    # exp_manager.run_simulations(config_builder=self.cb, exp_name=run_name, exp_builder=builder)
    # return self.cb
    exp_manager = ExperimentManagerFactory.init()
    exp_manager.run_simulations(config_builder=cb, exp_name=run_name, exp_builder=builder)
    return cb


def return_cb_with_interventions(self,
                                 include_itn=False,
                                 include_irs=False,
                                 include_msat=False,
                                 include_mda=False,
                                 include_stepd=False):
    self.implement_baseline_healthseeking(self.cb)
    self.implement_interventions(self.cb, include_itn, include_irs, include_msat, include_mda, include_stepd)
    return self.cb

