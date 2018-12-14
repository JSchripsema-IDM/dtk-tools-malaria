
from dtk.vector.species import set_larval_habitat, set_species_param, set_params_by_species
from dtk.interventions.input_EIR import add_InputEIR
from dtk.interventions.mosquito_release import add_mosquito_release
from dtk.interventions.itn import add_ITN
from dtk.interventions.itn_age_season import add_ITN_age_season
from dtk.interventions.irs import add_node_IRS, add_IRS
from dtk.interventions.outbreakindividual import recurring_outbreak
from dtk.interventions.migrate_to import add_migration_event
from dtk.interventions.health_seeking import add_health_seeking
from dtk.utils.reports.CustomReport import BaseReport, BaseVectorStatsReport

import json
import numpy as np

# Call update_params on the CB
class update_params:
    def __init__(self, params):
        self.params = params

    def __call__(self, cb):
        return cb.update_params(self.params)

class config_setup_fn:
    def __init__(self, duration=21915):
        self.duration = duration

    def __call__(self, cb):
        return cb.update_params({'Simulation_Duration': self.duration,
                            'Infection_Updates_Per_Timestep': 8})

# reporters
class summary_report_fn:
    def __init__(self, start=1, interval=365, nreports=2000, age_bins=[1000], parasitemia_bins=[0, 50, 500, 5000, 5000000], infection_bins=[0, 5, 20, 50, 80, 100], description='Annual_Report', nodes=None, ipfilter=None):
        self.start = start
        self.interval = interval
        self.nreports = nreports
        self.age_bins = age_bins or [1000]
        self.parasitemia_bins = parasitemia_bins
        self.infection_bins = infection_bins
        self.description = description
        self.nodes = nodes or {"class": "NodeSetAll"}
        self.ip_filter = ipfilter

    def __call__(self, cb):
        from malaria.reports.MalariaReport import add_summary_report
        return add_summary_report(cb, start=self.start, interval=self.interval, nreports=self.nreports,
                                  description=self.description, age_bins=self.age_bins,
                                  parasitemia_bins=self.parasitemia_bins, infection_bins=self.infection_bins,
                                  nodes=self.nodes, ipfilter=self.ip_filter)


class vector_stats_report_fn:
    def __init__(self, start=1):
        self.start = start

    def __call__(self, cb):
        return cb.add_reports(BaseVectorStatsReport(type="ReportVectorStats"))


class survey_report_fn:
    def __init__(self, days, interval=10000, nreports=1, survey_days=None, reporting_interval=None):
        self.days = days
        self.interval = interval
        self.nreports = nreports
        self.survey_days = survey_days or self.days
        self.reporting_interval = reporting_interval or self.interval

    def __call__(self, cb):
        from malaria.reports.MalariaReport import add_survey_report
        return add_survey_report(cb, survey_days=self.survey_days, reporting_interval=self.reporting_interval,
                                 nreports=self.nreports)
class patient_report_fn:
    def __init__(self, interval=10000, nreports=1, survey_days=None, reporting_interval=None):
        self.interval = interval
        self.nreports = nreports
        self.survey_days = survey_days
        self.reporting_interval = reporting_interval or self.interval

    def __call__(self, cb):
        from malaria.reports.MalariaReport import add_patient_report
        return add_patient_report(cb)


class add_challenge_trial_fn:
    def __init__(self, start_day=0):

        self.start_day = start_day

    def __call__(self, cb):
        from malaria.interventions.malaria_challenge import add_challenge_trial
        return add_challenge_trial(cb, start_day=self.start_day)


class filtered_report_fn:
    def __init__(self, start, end=100000, nodes=[], description=''):
        self.start = start
        self.end = end
        self.nodes = nodes
        self.description = description

    def __call__(self, cb):
        from malaria.reports.MalariaReport import add_filtered_report
        return add_filtered_report(cb, start=self.start, end=self.end, nodes=self.nodes, description=self.description)

class filtered_spatial_report_fn:
    def __init__(self, start, end, channels, nodes=[], description=''):
        self.start = start
        self.end = end
        self.channels = channels
        self.nodes = nodes
        self.description = description

    def __call__(self, cb):
        from malaria.reports.MalariaReport import add_filtered_spatial_report
        return add_filtered_spatial_report(cb, start=self.start, end=self.end, channels=self.channels,
                                           nodes=self.nodes, description=self.description)

class event_counter_report_fn:
    def __init__(self, channels, start, duration, nodes, description=''):
        self.start = start
        self.duration = duration
        self.channels = channels
        self.nodes = nodes
        self.description = description

    def __call__(self, cb):
        from malaria.reports.MalariaReport import add_event_counter_report
        return add_event_counter_report(cb, self.channels, start=self.start, duration=self.duration,
                                        nodes=self.nodes, description=self.description)


# vector
class larval_habitat_fn:
    def __init__(self, species, habitats):
        self.species = species
        self.habitats = habitats

    def __call__(self, cb):
        return set_larval_habitat(cb, {self.species: self.habitats})

class species_param_fn:
    def __init__(self, species, param, value):
        self.species = species
        self.param = param
        self.value = value

    def __call__(self, cb):
        return set_species_param(cb, self.species, self.param, self.value)

class set_params_by_species_fn:
    def __init__(self, species):
        self.species = species

    def __call__(self, cb):
        return set_params_by_species(cb.params, self.species, 'MALARIA_SIM')

# immune overlays
class add_immunity_fn:
    def __init__(self, tags):
        self.tags = tags

    def __call__(self, cb):
        from malaria.immunity import add_immune_overlays
        return add_immune_overlays(cb, tags=self.tags)

# input EIR
class site_input_eir_fn:
    def __init__(self, site, birth_cohort=True, set_site_geography=False):
        self.site = site
        self.birth_cohort = birth_cohort
        self.set_site_geography = set_site_geography

    def __call__(self, cb):
        from malaria.site.input_EIR_by_site import configure_site_EIR
        return configure_site_EIR(cb, site=self.site, birth_cohort=self.birth_cohort, set_site_geography=False)

class input_eir_fn:
    def __init__(self, monthlyEIRs, start_day=0, nodes=None):
        self.monthlyEIRs = monthlyEIRs
        self.start_day = start_day
        self.nodes = nodes or {"class": "NodeSetAll"}

    def __call__(self, cb):
        return add_InputEIR(cb, monthlyEIRs=self.monthlyEIRs, start_day=self.start_day, nodes=self.nodes)

# importation pressure
class add_outbreak_fn:
    def __init__(self, start_day=0, outbreak_fraction=0.01, repetitions=-1, tsteps_btwn=365, nodes=None):
        self.start_day = start_day
        self.outbreak_fraction = outbreak_fraction
        self.repetitions = repetitions
        self.tsteps_btwn = tsteps_btwn
        self.nodes = nodes or {"class": "NodeSetAll"}

    def __call__(self, cb):
        return recurring_outbreak(cb, outbreak_fraction=self.outbreak_fraction, repetitions=self.repetitions,
                                  tsteps_btwn=self.tsteps_btwn, start_day=self.start_day, nodes=self.nodes)

# migration
class add_migration_fn:
    def __init__(self, nodeto, start_day=0, coverage=1, repetitions=1, tsteps_btwn=365,
                     duration_at_node_distr_type='FIXED_DURATION',
                     duration_of_stay=100, duration_of_stay_2=0,
                     duration_before_leaving_distr_type='FIXED_DURATION',
                     duration_before_leaving=0, duration_before_leaving_2=0,
                     target='Everyone', nodesfrom=None):
        self.nodeto = nodeto
        self.start_day = start_day
        self.coverage = coverage
        self.repetitions = repetitions
        self.tsteps_btwn = tsteps_btwn,
        self.duration_at_node_distr_type = duration_at_node_distr_type
        self.duration_of_stay = duration_of_stay
        self.duration_of_stay_2 = duration_of_stay_2
        self.duration_before_leaving_distr_type = duration_before_leaving_distr_type
        self.duration_before_leaving = duration_before_leaving
        self.duration_before_leaving_2 = duration_before_leaving_2
        self.target = target
        self.nodesfrom = nodesfrom or {"class": "NodeSetAll"}

    def __call__(self, cb):
        return add_migration_event(cb, self.nodeto, start_day=self.start_day, coverage=self.coverage,
                                           repetitions=self.repetitions,
                                           tsteps_btwn=self.tsteps_btwn,
                                           duration_at_node_distr_type=self.duration_at_node_distr_type,
                                           duration_of_stay=self.duration_of_stay,
                                           duration_of_stay_2=self.duration_of_stay_2,
                                           duration_before_leaving_distr_type=self.duration_before_leaving_distr_type,
                                           duration_before_leaving=self.duration_before_leaving,
                                           duration_before_leaving_2=self.duration_before_leaving_2,
                                           target=self.target, nodesfrom=self.nodesfrom)


# mosquito release
class add_mosquito_release_fn:
    def __init__(self, start_day, vector_species, number_vectors, repetitions=-1, tsteps_btwn=365, nodes=None) :
        self.start_day = start_day
        self.vector_species = vector_species
        self.number_vectors = number_vectors
        self.repetitions = repetitions
        self.tsteps_btwn = tsteps_btwn
        self.nodes = nodes or {"class": "NodeSetAll"}

    def __call__(self, cb):
        return add_mosquito_release(cb, self.start_day, self.vector_species, self.number_vectors,
                                    repetitions=self.repetitions, tsteps_btwn=self.tsteps_btwn, nodes=self.nodes)



# health-seeking
class add_treatment_fn:
    def __init__(self, start=0, drug=None, targets=None, nodes=None, drug_ineligibility_duration=0,
                 node_property_restrictions=[]):
        self.start = start
        self.drug = drug or ['Artemether', 'Lumefantrine']
        self.targets = targets or [{'trigger': 'NewClinicalCase', 'coverage': 0.8, 'seek': 0.6, 'rate': 0.2}]
        self.nodes = nodes or {"class": "NodeSetAll"}
        self.node_property_restrictions=node_property_restrictions
        self.durg_ineligibility_duration=drug_ineligibility_duration

    def __call__(self, cb):
        return self.fn(cb)

    def fn(self, cb):
        add_health_seeking(cb, start_day=self.start, drug=self.drug, targets=self.targets, nodes=self.nodes,
                           drug_ineligibility_duration=self.durg_ineligibility_duration,
                           node_property_restrictions=self.node_property_restrictions)
        cb.update_params({'PKPD_Model': 'CONCENTRATION_VERSUS_TIME'})


# health-seeking from nodeid-coverage specified in json
def add_HS_by_node_id_fn(reffname, start=0) :        
    def fn(cb) :
        with open(reffname) as fin :
            cov = json.loads(fin.read())
        for hscov in cov['hscov'] :
            targets = [ { 'trigger': 'NewClinicalCase', 'coverage': 1, 'agemin':15, 'agemax':200, 'seek': hscov['coverage'], 'rate': 0.3 },
                        { 'trigger': 'NewClinicalCase', 'coverage': 1, 'agemin':0, 'agemax':15, 'seek':  min([1, hscov['coverage']*1.5]), 'rate': 0.3 },
                        { 'trigger': 'NewSevereCase',   'coverage': 1, 'seek': 0.8, 'rate': 0.5 } ]
            add_health_seeking(cb, start_day = start, targets=targets, nodes={'Node_List' : hscov['nodes'], "class": "NodeSetNodeList"})
    return fn

# seasonal health-seeking from nodeid-coverage specified in json
class add_HS_by_node_id_fn:
    def __init__(self, reffname, start=0):
        self.reffname = reffname
        self.start = start

    def __call__(self, cb):
        return self.fn(cb)

    def fn(self, cb):
        with open(self.reffname) as fin :
            cov = json.loads(fin.read())
        for hscov in cov['hscov'] :
            targets = [{'trigger': 'NewClinicalCase', 'coverage': 1, 'agemin':15, 'agemax':200, 'seek': hscov['coverage'], 'rate': 0.3},
                       {'trigger': 'NewClinicalCase', 'coverage': 1, 'agemin':0, 'agemax':15, 'seek':  min([1, hscov['coverage']*1.5]), 'rate': 0.3},
                       {'trigger': 'NewSevereCase',   'coverage': 1, 'seek': 0.8, 'rate': 0.5}]
            add_health_seeking(cb, start_day=self.start, targets=targets, nodes={'Node_List': hscov['nodes'], "class": "NodeSetNodeList"})


class add_seasonal_HS_by_node_id_fn:
    def __init__(self, reffname, days_in_month, scale_by_month, start=0):
        self.reffname = reffname
        self.days_in_month = days_in_month
        self.scale_by_month = scale_by_month
        self.start = start

    def __call__(self, cb):
        return self.fn(cb)

    def fn(self, cb):
        with open(self.reffname) as fin :
            cov = json.loads(fin.read())
        for hscov in cov['hscov']:
            ad_cov = hscov['coverage']
            kid_cov = min([1, hscov['coverage']*1.5])
            sev_cov = 0.8

            for start_month in range(len(self.scale_by_month)) :
                start_day = self.start+np.cumsum(self.days_in_month)[start_month]
                duration = self.days_in_month[start_month+1]

                scale = self.scale_by_month[start_month]
                targets = [
                    {'trigger': 'NewClinicalCase', 'coverage': 1, 'agemin': 15, 'agemax': 200,
                     'seek': min([1, ad_cov*scale]), 'rate': 0.3},
                    {'trigger': 'NewClinicalCase', 'coverage': 1, 'agemin': 0, 'agemax': 15,
                     'seek': min([1, kid_cov*scale]), 'rate': 0.3},
                    {'trigger': 'NewSevereCase', 'coverage': 1,
                     'seek': min([1, max([sev_cov*scale, kid_cov*scale])]), 'rate': 0.5}]

                add_health_seeking(cb, start_day=start_day, targets=targets,
                                   duration=duration, repetitions=-1,
                                   drug_ineligibility_duration=14,
                                   nodes={'Node_List': hscov['nodes'], "class": "NodeSetNodeList"})

class add_seasonal_HS_by_NP_fn:
    def __init__(self, fname, channel, start_day, days_in_month, scale_by_month, duration_years):
        self.fname = fname
        self.channel = channel
        self.date = start_day
        self.days_in_month = days_in_month
        self.scale_by_month = scale_by_month
        self.duration_years = duration_years
        self.prop_name = 'HScategory' if self.channel == 'hscov' else 'CHWcategory'

    def __call__(self, cb):
        return self.fn(cb)

    def fn(self, cb):
        self.set_hs_group(cb)
        self.seasonal_health_seeking(cb)

    def set_hs_group(self, cb):

        from dtk.interventions.property_change import change_node_property

        with open(self.fname) as fin:
            interv = json.loads(fin.read())

        covlist = interv[self.channel]
        for i, item in enumerate(covlist):
            code = 'group%d' % i
            change_node_property(cb, self.prop_name, code, start_day=self.date, nodeIDs=item['nodes'])

    def seasonal_health_seeking(self, cb):

        with open(self.fname) as fin:
            cov = json.loads(fin.read())
        for i, hscov in enumerate(cov[self.channel]):

            code = 'group%d' % i
            ad_cov = hscov['coverage']
            kid_cov = min([1, hscov['coverage'] * 1.5])
            sev_cov = 0.8

            for start_month in range(len(self.scale_by_month)):
                start_day = int(self.date + np.cumsum(self.days_in_month)[start_month])
                duration = self.days_in_month[start_month + 1]
                scale = self.scale_by_month[start_month]
                targets = [
                    {'trigger': 'NewClinicalCase', 'coverage': 1, 'agemin': 15, 'agemax': 200,
                     'seek': min([1, ad_cov * scale]), 'rate': 0.3},
                    {'trigger': 'NewClinicalCase', 'coverage': 1, 'agemin': 0, 'agemax': 15,
                     'seek': min([1, kid_cov * scale]), 'rate': 0.3},
                    {'trigger': 'NewSevereCase', 'coverage': 1,
                     'seek': min([1, max([sev_cov * scale, kid_cov * scale])]), 'rate': 0.5}]

                add_health_seeking(cb, start_day=start_day, targets=targets,
                                   duration=duration, repetitions=self.duration_years + 1,
                                   drug_ineligibility_duration=14,
                                   node_property_restrictions=[{self.prop_name: code}])


# ITNs
class add_itn_fn:
    def __init__(self, start=0, coverage=1, waning=None, nodeIDs=None):
        self.start = start
        self.coverage = coverage
        self.waning = waning or {}
        self.nodeIDs = nodeIDs or []

    def __call__(self, cb):
        return self.fn(cb)

    def fn(self, cb):
        coverage_by_age = {'min': 0, 'max': 200, 'coverage': self.coverage}
        add_ITN(cb, start=self.start, coverage_by_ages=[coverage_by_age], waning=self.waning, nodeIDs=self.nodeIDs)

class add_itn_age_season_fn:
    def __init__(self, start=0, coverage=1, age_dep=[], seasonal_dep={}, discard={}):
        self.start = start
        self.coverage = coverage
        self.age_dep = age_dep
        self.seasonal_dep = seasonal_dep
        self.discard = discard

    def __call__(self, cb):
        return self.fn(cb)

    def fn(self, cb):
        add_ITN_age_season(cb, start=self.start,
                           age_dep=self.age_dep,
                           coverage_all=self.coverage,
                           as_birth=False,
                           seasonal_dep=self.seasonal_dep,
                           discard=self.discard)


# ITNs from nodeid-coverage specified in json
class add_itn_by_node_id_fn:
    def __init__(self, reffname, itn_dates, itn_fracs, channel='itn2012cov', waning=None):
        self.reffname = reffname
        self.itn_dates = itn_dates
        self.itn_fracs = itn_fracs
        self.channel = channel
        self.waning = waning or {}

    def __call__(self, cb):
        return self.fn(cb)

    def fn(self, cb) :
        birth_durations = [self.itn_dates[x] - self.itn_dates[x + 1] for x in range(len(self.itn_dates) - 1)]
        # itn_distr = zip(self.itn_dates[:-1], self.itn_fracs)
        with open(self.reffname) as fin :
            cov = json.loads(fin.read())
        for itncov in cov[self.channel] :
            if itncov['coverage'] > 0 :
                for i, (itn_date, itn_frac) in enumerate(zip(self.itn_dates, self.itn_fracs)):
                    c = itncov['coverage'] * itn_frac
                    if i < len(self.itn_fracs) - 1:
                        c /= np.prod([1 - x * itncov['coverage'] for x in self.itn_fracs[i + 1:]])
                    add_ITN(cb, itn_date,
                            coverage_by_ages=[{'min': 0, 'max': 5, 'coverage': min([1, c*1.3])},
                                              {'birth': 1, 'coverage': min([1,c*1.3]), 'duration': max([-1, birth_durations[i]])},
                                              {'min': 5, 'max': 20, 'coverage': c / 2},
                                              {'min': 20, 'max': 100, 'coverage': min([1, c*1.3])}],
                            waning=self.waning, nodeIDs=itncov['nodes'])


# IRS
class add_irs_fn:
    def __init__(self, start=0, coverage=1, waning=None, nodeIDs=None):
        self.start = start
        self.coverage = coverage
        self.waning = waning or {}
        self.nodeIDs = nodeIDs or []

    def __call__(self, cb):
        return self.fn(cb)

    def fn(self, cb):
        coverage_by_age = {'min': 0, 'max': 200, 'coverage': self.coverage}
        add_IRS(cb, start=self.start, coverage_by_ages=[coverage_by_age], waning=self.waning, nodeIDs=self.nodeIDs)

# IRS from nodeid-coverage specified in json
class add_node_level_irs_by_node_id_fn:
    def __init__(self, reffname, irs_dates, irs_fracs, channel='irs2012cov',
                                     initial_killing=0.5, box_duration=90):
        self.reffname = reffname
        self.irs_dates = irs_dates
        self.irs_fracs = irs_fracs
        self.channel = channel
        self.initial_killing = initial_killing
        self.box_duration = box_duration

    def __call__(self, cb):
        return self.fn(cb)

    def fn(self, cb):
        nodelist = {x: [] for x in self.irs_dates}

        irs_distr = zip(self.irs_dates, self.irs_fracs)
        with open(self.reffname) as fin:
            cov = json.loads(fin.read())
        for irscov in cov[self.channel]:
            if irscov['coverage'] > 0:
                for i, (irs_date, irs_frac) in enumerate(irs_distr):
                    c = irscov['coverage'] * irs_frac
                    if i < len(self.irs_fracs) - 1:
                        c /= np.prod([1 - x * irscov['coverage'] for x in self.irs_fracs[i + 1:]])
                    nodeIDs = [x for x in irscov['nodes'] if np.random.random() <= c]
                    nodelist[irs_date] += nodeIDs

        for i, (irs_date, irs_frac) in enumerate(irs_distr):
            if len(nodelist[irs_date]) > 0 :
                add_node_IRS(cb, irs_date, initial_killing=self.initial_killing,
                             box_duration=self.box_duration, nodeIDs=nodelist[irs_date])


# drug campaign
class add_drug_campaign_fn:
    def __init__(self, campaign_type, drug_code, start_days, coverage=1.0, repetitions=3,
                         interval=60, diagnostic_threshold=40, diagnostic_type='TRUE_PARASITE_DENSITY',
                         snowballs=0, delay=0, nodes=None, target_group='Everyone',
                 node_property_restrictions=[], drug_ineligibility_duration=0):
        self.campaign_type = campaign_type
        self.drug_code = drug_code
        self.start_days = start_days
        self.coverage = coverage
        self.repetitions = repetitions
        self.interval = interval
        self.diagnostic_threshold = diagnostic_threshold
        self.diagnostic_type = diagnostic_type
        self.snowballs = snowballs
        self.delay = delay
        self.nodes = nodes or []
        self.target_group = target_group
        self.NP_restrictions = node_property_restrictions
        self.drug_ineligibility_duration = drug_ineligibility_duration

    def __call__(self, cb):
        from malaria.interventions.malaria_drug_campaigns import add_drug_campaign
        return add_drug_campaign(cb, self.campaign_type, self.drug_code, start_days=self.start_days,
                                 coverage=self.coverage, repetitions=self.repetitions, interval=self.interval,
                                 diagnostic_threshold=self.diagnostic_threshold,
                                 diagnostic_type=self.diagnostic_type,
                                 drug_ineligibility_duration=self.drug_ineligibility_duration,
                                 snowballs=self.snowballs, treatment_delay=self.delay, nodes=self.nodes,
                                 target_group=self.target_group, node_property_restrictions=self.NP_restrictions)

