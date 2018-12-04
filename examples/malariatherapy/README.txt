This example was written by Jon Russell as part of the work to improve the intrahost model of malaria by simulating and analyzing malariatherapy like infections using a scalable set of transition probabilities in a stochastic matrix. 

This run file uses the .from_files command for using a config file that details the necessary parameters for running this Malaria 2.0 logic.
cb = DTKConfigBuilder.from_files(config_path)

In addition it calls for the creation of the Malaria Patient Report output and relies on the DurationsAnalyzer that will plot the infection durations from each simulation.

The immunity forcing block allows for the potential to scale the Transition Matrix values using pretty simple logic and relies on the ModFn tool to set up the scale_factor for each sim.

12/3/2018
Institute for Disease Modeling, Bellevue, WA
