import os
import shutil
import pathlib
import pyglider.utils as pyutils
# get list of glider directories
path = '.'
nonHiddenDir = [f for f in os.listdir(path) if not f.startswith('.')]
gldDir = [f for f in nonHiddenDir if os.path.isdir(os.path.join(path, f))]
gldPath = [path + "/" + k for k in gldDir]
# iterate through each directory
# read in deployment yaml
# copy over appropriate processing script
# modify the logic below as things progress
for x in gldPath:
    yml = x + "/" + "deployment.yaml"
    if os.path.isfile(yml):
        print(f"Yaml file exists for {x}, copying over processing scripts")
        deployment = pyutils._get_deployment(yml)
        model = deployment['metadata']['glider_model']
        if model == "SeaExplorer":
            # add logic to check if 'dst' exists
            # have a parameter in header to decide if it
            #   gets replaced everytime the script is executed
            src = pathlib.Path("./process_SeaExplorer_delayed.py")
            dst = pathlib.Path(x + "/" + "process_delayed.py")
            shutil.copy2(src = src,
                         dst = dst)
            src = pathlib.Path("./postProcess_SeaExplorer_delayed.py")
            dst = pathlib.Path(x + "/" + "postProcess_delayed.py")
            shutil.copy2(src=src,
                         dst=dst)
        else:
            print(f"Yaml files does not exists for {x}")
