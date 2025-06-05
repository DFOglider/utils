import logging
import os
import netCDF4 as nc
import re
import pyglider.seaexplorer as seaexplorer
import pyglider.ncprocess as ncprocess

logging.basicConfig(filename = 'process_delayed.log', level='INFO')

# define yaml file
deploymentyaml = 'deployment.yaml'
# define and create (if needed) directories
rawdir = './raw/' # where the raw data lives
rawncdir = './rawnc/' # for raw netcdf files
rawncmergedir = './delayed_rawnc/' # for merged raw netcdf files
l0tsdir    = './L0-timeseries/'
l0prfdir = './L0-profiles/'
l0grddir = './L0-grid/'
fnamesuffix = '_delayed'
outputdirs = [rawncdir, rawncmergedir, l0tsdir, l0prfdir, l0grddir]
# check if output directories exist, if not, create them
for dir in outputdirs:
    exists = os.path.exists(dir)
    if not exists:
        os.makedirs(dir)
        print('Created' + dir)
        

# Turn binary raw files into *.nc netcdf files.
seaexplorer.raw_to_rawnc(indir=rawdir, 
                         outdir=rawncdir, 
                         deploymentyaml=deploymentyaml,
                         #dropna_subset=['GPCTD_TEMPERATURE', 'FLBBCD_CHL_COUNT'], 
                         incremental=False # always re-parse
                         )
# Merge individual netcdf files into single netcdf file *.nc
seaexplorer.merge_rawnc(indir=rawncdir, 
                        outdir=rawncmergedir,
                        deploymentyaml=deploymentyaml, 
                        kind='raw')
# Make level-1 timeseries netcdf file from the raw files
outname = seaexplorer.raw_to_timeseries(indir=rawncmergedir,
                                        outdir=l0tsdir, 
                                        deploymentyaml=deploymentyaml, 
                                        kind='raw', 
                                        profile_filt_time=20, 
                                        profile_min_time=100, 
                                        fnamesuffix=fnamesuffix,
					deadreckon=True)
# make profile netcdf files for ioos gdac
ncprocess.extract_timeseries_profiles(inname=outname, 
                                      outdir=l0prfdir, 
                                      deploymentyaml=deploymentyaml,
                                      force=True)
# make grid of dataset....
outname2 = ncprocess.make_gridfiles(inname=outname, 
                                    outdir=l0grddir, 
                                    deploymentyaml=deploymentyaml,
                                    fnamesuffix=fnamesuffix)
