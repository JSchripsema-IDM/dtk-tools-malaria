This is a simplified example version of the spatial setup that was used for the ISGlobal Mozambique engagement of Spring 2018, built
primarily by Josh Suresh (jsuresh@idmod.org), Caitlin Bever, and Jaline Gerardin.

Prereqs:
Must have dtk-tools, dtk-tools-malaria, malaria-toolbox packages installed.
(run "python setup.py" or "python setup.py develop" for all 3 packages)

Description:
Runs the catchment "Magude-Sede-Facazissa" with 1 km^2 gridded pixels from 2 serialized file (for 2 cores),
starting at year 2010 and running for 10 years, with node-specific intervention timings and coverages.
This codebase is organized into


Note:
-The serialized files are located on COMPS at "//internal.idm.ctr/IDM/home/jsuresh/input/Magude_Core_Geography_Example/"

How to run:
Execute "python run_magude_dtk.py".

