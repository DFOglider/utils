import os
import pathlib
import shutil
import re
import numpy as np
# define some paths
yamlpath='../../../deploymentYaml'
datapath='.'
# get list of glider data directories
## anything not hidden
alldatadirs = [f for f in os.listdir(datapath) if not f.startswith('.')]
## get directories
datadirs = [f for f in alldatadirs if os.path.isdir(os.path.join(datapath, f))]
## get glider directories
glddirs = [f for f in datadirs if re.search('^GLD\\w+', f)]
# get list of yaml files
## anything not hidden
allyamlfiles = [f for f in os.listdir(yamlpath) if not f.startswith('.')]
## get yaml files
yamlfiles = [f for f in allyamlfiles if re.search('^GLI\\w+\\.yaml', f)]
## remove 'GLI' b/c of inconsistency
yamllook = [re.sub('GLI(\\w+)\\.yaml', '\\1', x) for x in yamlfiles]
# iterate through each glddir and copy over yamlfile
for dir in glddirs:
    # find match
    # remove 'GLD' b/c of inconsistency
    dirlook = re.sub('GLD(\\w+)', '\\1', dir)
    # find which yamllook matches dirlook
    #   i'm not going to assume that there is one.
    yamlmatch = [x for x in yamllook if x == dirlook]
    if yamlmatch.__len__() == 0:
        print(f"Yaml for glider data directory {dir} does not exist,"
              f" continuing to next directory.")
    else:
        print(f"Copying yaml file to {dir}.")
        srcPath = yamlpath + '/' + 'GLI' + dirlook + '.yaml'
        src = pathlib.Path(srcPath)
        dstPath = datapath + '/' + dir + '/' + 'deployment.yaml'
        dst = pathlib.Path(dstPath)
        shutil.copy2(src=src,
                     dst=dst)