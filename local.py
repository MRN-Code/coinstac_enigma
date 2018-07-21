import glob
import json
import os
import subprocess
import sys
from utils import listRecursive


def local_1(args):
    input_list = args["input"]

    # Setting environment for the script to work seamlessly
    scriptDir = "/computation/enigma_scripts"
    resDir = os.path.join(args["state"]["outputDirectory"], 'results')
    logDir = os.path.join(args["state"]["outputDirectory"], 'logs')

    data_dir = args["state"]["baseDirectory"]
    subjects_cov = os.path.join(args["state"]["baseDirectory"],
                                'covariates.csv')
    config_path = os.path.join(scriptDir, input_list["CONFIG_PATH"])

    # Running the first script
    regr_args = [
        "bash",
        os.path.join(scriptDir, "mass_uv_regr_csv.sh"), scriptDir, resDir,
        logDir, data_dir, config_path, subjects_cov
    ]
    subprocess.call(regr_args)

    # Running the second script
    concat_args = [
        "bash",
        os.path.join(scriptDir, "concat_mass_uv_regr_csv.sh"), scriptDir,
        resDir, logDir, data_dir, config_path
    ]
    subprocess.call(concat_args)

    # Gather the list of ALL csv files
    agg_file_list = glob.glob(os.path.join(resDir, '*ALL*.csv'))

    # Sending contents of the ALL files as dictionary with the file name being
    # key and contents the value
    #TODO: Can also read the files as dataframes which makes it easy to work on 
    # later
    output_contents = dict()
    for file in agg_file_list:
        file_name = os.path.split(file)[-1]
        file_name = os.path.splitext(file_name)[0]

        with open(file, 'r') as f:
            lines = f.readlines()

        output_contents[file_name] = lines

    output_dict = {
        "output_contents": output_contents,
        "computation_phase": "local_1"
    }

    computation_output = {"output": output_dict}

    return json.dumps(computation_output)


if __name__ == '__main__':

    parsed_args = json.loads(sys.stdin.read())
    phase_key = list(listRecursive(parsed_args, 'computation_phase'))

    if not phase_key:
        computation_output = local_1(parsed_args)
        sys.stdout.write(computation_output)
    else:
        raise ValueError("Error occurred at Local")
