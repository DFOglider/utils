import os
import re
import shutil
import pathlib
# get list of glider directories
path = '.'
nonHiddenDir = [f for f in os.listdir(path) if not f.startswith('.')]
gldDir = [f for f in nonHiddenDir if os.path.isdir(os.path.join(path, f))]
gldPath = [path + "/" + k for k in gldDir]
for x in gldPath:
    print(f"{x}")
    # create 'raw' directory
    rawdir = x + '/' + 'raw'
    ## check if it exists, if not create it
    exists = os.path.exists(rawdir)
    if not exists:
        print(f"Creating raw directory")
        os.makedirs(rawdir)
    # get mission number
    missionNumber = re.sub('./GLD\\d+SEA\\d+M(\\d+)', '\\1', x)
    # copy data from nav into rawdir
    navpath = x + '/' + 'nav/logs'
    ## check that it exists
    navexists = os.path.exists(navpath)
    ## define navpattern
    navpattern = '.*\\.'+ missionNumber + '\\..*gli\\.sub.*'
    if navexists:
        allnavfiles = [f for f in os.listdir(navpath) if not f.startswith('.')]
        navfiles = [f for f in allnavfiles if re.search(navpattern, f)]
        print(f"Copying nav files to raw for {x}")
        if navfiles.__len__() == 0:
            print(f"No nav files found")
        else :
            for f in navfiles:
                src = pathlib.Path(navpath + '/' + f)
                dst = pathlib.Path(rawdir + '/' + f)
                if os.path.isfile(dst):
                    continue
                else :
                    shutil.copy2(src=src,
                                 dst=dst)
            navomit = [f for f in navfiles if re.search('.*\\.1\\.gz', f)]
            if navomit.__len__() != 0:
                for f in navomit:
                    dstomit = pathlib.Path(rawdir + '/' + f)
                    if os.path.exists(dstomit):
                        print(f"Removing file {f}")
                        os.remove(dstomit)
    else:
        print(f"Expected path to nav files, {navpath} does not exist.")
    # copy data from pld into rawdir
    pldpath = x + '/' + 'pld/logs'
    ## check that it exists
    pldexists = os.path.exists(pldpath)
    ## define pldpattern
    pldpattern = '.*\\.'+ missionNumber + '\\..*pld1\\.raw.*'
    if pldexists:
        allpldfiles = [f for f in os.listdir(pldpath) if not f.startswith('.')]
        pldfiles = [f for f in allpldfiles if re.search(pldpattern, f)]
        print(f"Copying pld files to raw for {x}")
        if pldfiles.__len__() == 0:
            print(f"No pld files found")
        else:
            for f in pldfiles:
                src = pathlib.Path(pldpath + '/' + f)
                dst = pathlib.Path(rawdir + '/' + f)
                if os.path.isfile(dst):
                    continue
                else:
                    shutil.copy2(src=src,
                                 dst=dst)
            pldomit = [f for f in pldfiles if re.search('.*\\.1\\.gz', f)]
            if pldomit.__len__() != 0:
                for f in pldomit:
                    dstomit = pathlib.Path(rawdir + '/' + f)
                    if os.path.exists(dstomit):
                        print(f"Removing file {f}")
                        os.remove(dstomit)
    else:
        print(f"Expected path to pld files, {pldpath} does not exist.")