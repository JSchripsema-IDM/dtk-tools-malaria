This is a simple example of a 3-node Southeast Asian setup consisting of 2 villages and 1 forest area, as described in Gerardin et al. Intl Health 2018.

Built by Jaline Gerardin (jgerardin@idmod.org). Other versions also used by abertozzivilla and mambrose.


Prereqs:
Must have dtk-tools, dtk-tools-malaria, malaria-toolbox packages installed.
(run "python setup.py" or "python setup.py develop" for all 3 packages)


Files:
run_forest_dtk.py - Picks up serialized simulation, runs short simulation with health-seeking, and calls analyzers on simulation results. Run as
"python ./run_forest_dtk.py"

configure_forest_system.py - vector param updates, other config param updates, set up seasonal migration, set input/exe/dll assets for HPC
analyze_spatial_villages.py - example analyzer for SpatialReportMalariaFiltered_* type output (per-node prevalence, incidence, population with time)
analyze_migration.py - example analyzer for ReportHumanMigrationTracking.csv type output, assuming local and intervention migration times
bin/ - executable and dlls
input/ - demographics, climate, migration files, and serialized file.


Description:
Provides example uses of:
- different vector species in different nodes (demographics file)
- user-defined Individual Properties (demographics file)
- migration as a campaign event (configure_forest_system)
- targeting an intervention to individuals with a specific Individual Property (add_forest_migration() in configure_forest_system)
- setting asset collection id's (configure_forest_system)
- picking up a serialized simulation (configure_forest_system)
- case management (add_health_seeking call in run_forest_dtk)
- requesting SpatialReportMalariaFiltered custom report (run_forest_dtk)
- requesting ReportEventCounter custom report to count treated cases (run_forest_dtk)
- requesting ReportHumanMigrationTracking (run_forest_dtk)
- sweeping over multiple random seeds (run_forest_dtk)
- writing an analyzer with arguments (both analyzers)
- writing an analyzer for SpatialReportMalariaFiltered custom reports and constructing basic plots of this data (analyze_spatial_villages)
- writing an analyzer for ReportHumanMigrationTracking custom report and constructing basic plots of this data (analyze_migration)


Note:
-The serialized file can be found in the input directory or grabbed via Asset Manager on COMPS.