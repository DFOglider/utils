import logging
import os
import netCDF4 as nc
import re
import pandas as pd
import numpy as np
import pyglider.seaexplorer as seaexplorer
import pyglider.ncprocess as ncprocess
# function to add [longitude, latitude]_gps and linearly interpolate between gps hits
# to timeseries file
def addGPS(inname):
    src = nc.Dataset(inname, mode='a')
    variables = list(src.variables.keys())
    if 'DeadReckoning' in variables:
        # create LATITUDE_GPS and LONGITUDE_GPS
        ## this will be only coordinates where DeadReckoning == 0 and NavState == 116
        ## order of states :
        ### 119
        ### 116 - transmitting
        ### 110 - inflecting down -> 100 going down
        ### 118 - inflecting up -> 117 going up
        ### 115 - surfacing
        ### 119
        ### 116 - transmitting
        dr = src.variables.get('DeadReckoning')[:]
        ns = src.variables.get('NavState')[:]
        ok = (dr == 0) & ~dr.mask & (ns == 116) & ~ns.mask
    else: # use longitude and latitude values with navstate
        ns = src.variables.get('NavState')[:]
        ok = (ns == 116) & ~ns.mask
    lon = src.variables.get('longitude')[:]
    lat = src.variables.get('latitude')[:]
    longps = pd.Series(np.ma.masked_array(data=lon.data, mask=ok.mask, fill_value=np.nan).filled())
    longps.interpolate(method='linear', inplace=True)
    latgps = pd.Series(np.ma.masked_array(data=lat.data, mask=ok.mask, fill_value=np.nan).filled())
    latgps.interpolate(method='linear', inplace=True)
    # add to file
    ## get dimensions from existing variable
    dimensions = src.variables.get('NavState').dimensions
    ## create LONGITUDE_GPS
    nclongps = src.createVariable(varname = "LONGITUDE_GPS",
                                  datatype='f4',
                                  dimensions=dimensions)
    nclongps[:] = longps
    ### add attributes
    nclongps.coordinate_reference_frame='urn: ogc:crs: EPSG::4326'
    nclongps.long_name = "Longitude east by unspecified GPS system"
    nclongps.observation_type = "measured and interpolated"
    nclongps.reference= "WGS84"
    nclongps.standard_name = "longitude"
    nclongps.units= "degree_east"
    nclongps.unitsVocabulary= "http://vocab.nerc.ac.uk/collection/P06/current/DEGE/"
    nclongps.valid_max= 180.00
    nclongps.valid_min= -180.00
    nclongps.vocabulary= "https://vocab.nerc.ac.uk/collection/OG1/current/LON_GPS/"
        ## create LATITUDE_GPS
    nclatgps = src.createVariable(varname="LATITUDE_GPS",
                                  datatype='f4',
                                  dimensions=dimensions)
    nclatgps[:] = latgps
    ### add attributes
    nclatgps.coordinate_reference_frame='urn: ogc:crs: EPSG::4326'
    nclatgps.long_name = "Latitude north by unspecified GPS system"
    nclatgps.observation_type = "measured and interpolated"
    nclatgps.reference= "WGS84"
    nclatgps.standard_name = "latitude"
    nclatgps.units= "degree_north"
    nclatgps.unitsVocabulary= "http://vocab.nerc.ac.uk/collection/P06/current/DEGN/"
    nclatgps.valid_max= 90.00
    nclatgps.valid_min= -90.00
    nclatgps.vocabulary= "https://vocab.nerc.ac.uk/collection/OG1/current/LAT_GPS/"
    # close netcdf file
    src.close()

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
addGPS(inname=outname)
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
