# -*- coding: utf-8 -*-
import sys
sys.path.append('utilities')
import os
import data_utils
import general_utils
import numpy as np

################# OPTIONS ######################

options = general_utils.read_input_parameters()

"""
# Define the target name, detrending method and parameters of it:
target = '228735255b'#'CL032-10'#'my_data'

photometry = {}
phot_noise_model = ['white','white']
phot_detrend = [None,None]#'mfilter'
window = [41,41]

# Define if you want to perform automatic outlier removal (sigma-clipping):
phot_get_outliers = [True,False]

# Define which transits you want to ommit (counted from first transit):
n_ommit = [[],[]]

# Define if you want to perform the resampling technique and in 
# which phase range you want to perform such resampling. Additionally, 
# define how many samples you want to resample:
resampling = [True,False]
phase_max = [0.025,0.025]
N_resampling = [20,20]

# Limb-darkening law to be used:
ld_law = ['quadratic','quadratic']

# Define the mode to be used:
mode = 'full' 

# Define noise properties:
rv_jitter = False

# Define emcee parameters:
nwalkers = 500
njumps = 500
nburnin = 500

# Define time conversions:
transit_time_def = ['tdb->utc','utc->utc']
rv_time_def = 'utc->utc'
"""
################################################

# ---------- DATA PRE-PROCESSING ------------- #

# First, get the transit and RV data:
t_tr,f,f_err,transit_instruments,t_rv,rv,rv_err,rv_instruments = general_utils.read_data(options)

# Sort transit data if there is any:
# Initialize the parameters:
parameters = general_utils.read_priors(options['TARGET'],options['MODE'])

# Pre-process the transit data if available:
if options['MODE'] != 'rvs':
    t_tr,phases,f, f_err,transit_instruments = data_utils.pre_process(t_tr,f,f_err,options,transit_instruments,parameters)
    idx = np.argsort(t_tr)
    t_tr = t_tr[idx]
    f = f[idx]
    f_err = f_err[idx]
    phases = phases[idx]
    transit_instruments = transit_instruments[idx]
    idx_resampling = {}
    for instrument in options['photometry'].keys():
        idx = np.where(transit_instruments==instrument)[0]
        if options['photometry'][instrument]['RESAMPLING']:
            # Define indexes between which data will be resampled:
            idx_resampling[instrument] = np.where((phases[idx]>-options['photometry'][instrument]['PHASE_MAX_RESAMPLING'])&\
                                         (phases[idx]<options['photometry'][instrument]['PHASE_MAX_RESAMPLING']))[0]
        else:
            idx_resampling[instrument] = []
# Create results folder if not already created:
if not os.path.exists('results'):
    os.mkdir('results')

mode = options['MODE']
target = options['TARGET']
fname = target+'_'+mode+'_'
for instrument in options['photometry'].keys():
    fname = fname + instrument +'_'+options['photometry'][instrument]['PHOT_NOISE_MODEL']+\
                  '_'+options['photometry'][instrument]['LD_LAW']+'_'
out_dir = 'results/'+fname[:-1]+'/'

# If chains not ran, run the MCMC and save results:
if not os.path.exists(out_dir):
    print '\t Starting MCMC...'
    data_utils.exonailer_mcmc_fit(t_tr, f, f_err, transit_instruments, t_rv, rv, rv_err, rv_instruments,\
                                     parameters, idx_resampling, options)

    general_utils.save_results(target,options,parameters)

else:
    parameters = general_utils.read_results(target,options,transit_instruments,rv_instruments)

# Get plot of the transit-fit, rv-fit or both (TODO: this is missing the RV fit alone!):
#if options['MODE'] == 'transit':
#    data_utils.plot_transit(t_tr,f,parameters,ld_law,transit_instruments, resampling = resampling, \
#                                      phase_max = phase_max, N_resampling=N_resampling)
if options['MODE'] != 'transit_noise':
    data_utils.plot_transit_and_rv(t_tr, f, f_err, transit_instruments, t_rv, rv, rv_err, rv_instruments,\
                               parameters, idx_resampling, options)
                                    #t_tr,f,f_err,t_rv,rv,rv_err,parameters,transit_instruments, rv_instruments,\
                                    #  options)#ld_law,rv_jitter, \
                                      #transit_instruments, rv_instruments,\
                                      #resampling = resampling, phase_max = phase_max, \
                                      #N_resampling=N_resampling)
