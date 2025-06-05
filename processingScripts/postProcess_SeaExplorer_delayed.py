import logging
import os
import subprocess
import netCDF4 as nc
import re
import pyglider.utils as pyutils
# function to create new 'post' file
#   which will exclude some variables defined by 'toexclude'
#   and rename some variables
#   note that renaming 'salinity' to 'PSAL' is hard coded
def createPostProcessFile(fileIn, fileOut, toExclude, originalReplaceName, replaceName):
    for i in range(len(fileIn)): 
        print(f"Reading in file {fileIn[i]} and creating new file {fileOut[i]}.")
        with nc.Dataset(fileIn[i]) as src, nc.Dataset(fileOut[i], "w") as dst:
            # copy global attributes all at once via dictionary
            dst.setncatts(src.__dict__)
            # copy dimensions
            for name, dimension in src.dimensions.items():
                dst.createDimension(
                    name, (len(dimension) if not dimension.isunlimited() else None))
                # copy all file data except for the excluded
            for name, variable in src.variables.items(): 
                if name not in toExclude:
                    print(f"Adding {name} to {fileOut[i]}.")
                    x = dst.createVariable(name, variable.datatype, variable.dimensions)
                    # copy variable attributes all at once via dictionary
                    dst[name].setncatts(src[name].__dict__)
                    dst[name][:] = src[name][:]
            # change variable name
            for i in range(len(originalReplaceName)):
                origname = originalReplaceName[i]
                newname = replaceName[i]
                print(f"Changing variable name from {origname} to {newname}.")
                dst.renameVariable(oldname = origname, newname = newname)
            if not('PSAL' in list(src.variables)):
                print(f"Changing variable name from salinity to PSAL") 
                dst.renameVariable(oldname = 'salinity', newname = 'PSAL')
            if 'oxygen_concentration' in list(src.variables):
                print(f"Changing variable name from oxygen_concentration to DOXY")
                dst.renameVariable(oldname = 'oxygen_concentration', newname = 'DOXY')

logging.basicConfig(filename = 'postProcess_delayed.log', level='INFO')
# define derived variables that will be removed from nc files
toExclude = ['potential_density',
             'potential_temperature',
             'distance_over_ground',
             'density']
# define yaml file
deploymentyaml = 'deployment.yaml'
# define and create (if needed) directories
l0tsdir    = './L0-timeseries/'
l0tsdirpost = './L0-timeseries-post/'
l0prfdir = './L0-profiles/'
l0prfdirpost = './L0-profiles-post/'
l0grddir = './L0-grid/'
l0grddirpost = './L0-grid-post/'
fnamesuffix = '_delayed'
outputdirs = [l0tsdir, l0tsdirpost, 
              l0prfdir, l0prfdirpost, 
              l0grddir, l0grddirpost]
# check if output directories exist, if not, create them
for dir in outputdirs:
    exists = os.path.exists(dir)
    if not exists:
        os.makedirs(dir)
        print('Created' + dir)

# rename some variables with OG1 variable names
# remove some derived variables that we aren't interested in
# read in deploymentyaml
deployment = pyutils._get_deployment(deploymentyaml)
# find which variables have 'replaceName'
ncvar = deployment['netcdf_variables']
varnames = list(ncvar.keys())
# omit unnecessary vars
for i in ['time', 'timebase', 'keep_variables', 'interpolate']:
    if i in varnames:
        varnames.remove(i)
originalReplaceName = [x for x in varnames if 'replaceName' in ncvar[x].keys()]
replaceName = [ncvar[x]['replaceName'] for x in originalReplaceName]
# define which directories to iterate through to create
#   new post processed files
#   iterate through each type of file
lookdirs = [[l0tsdir, l0tsdirpost], # timeseries
            [l0prfdir, l0prfdirpost], # profiles
            [l0grddir, l0grddirpost]] # grid
for dirs in lookdirs:
    # files
    file = os.listdir(path=dirs[0])
    file =  [f for f in file if os.path.isfile(dirs[0]+'/'+f)]
    # construct new filename
    fileBasename = [os.path.basename(f) for f in file]
    fileBasenameSpli = [os.path.splitext(f) for f in fileBasename]
    filePost = [f[0] + '_post' + f[1] for f in fileBasenameSpli]
    # construct paths for original files and post files
    fileIn = [dirs[0] + f for f in file]
    fileOut = [dirs[1] + f for f in filePost]
    createPostProcessFile(fileIn=fileIn,
                          fileOut=fileOut,
                          toExclude=toExclude,
                          originalReplaceName=originalReplaceName,
                          replaceName=replaceName)

