import json
import os
import subprocess
import sys
from utils import listRecursive


def local_1(args):
    input_list = args["input"]

    scriptDir = "/computation/scripts"
    resDir = os.path.join(args["state"]["cacheDirectory"], 'results')
    logDir = os.path.join(args["state"]["cacheDirectory"], 'logs')

    finalResDir = args["state"]["outputDirectory"]

    data_dir = args["state"]["baseDirectory"]
    subjects_cov = os.path.join(args["state"]["baseDirectory"],
                                'covariates.csv')
    config_path = os.path.join(scriptDir, input_list["CONFIG_PATH"])

    regr_args = [
        "bash",
        os.path.join(scriptDir, "mass_uv_regr_csv.sh"), scriptDir, resDir,
        logDir, data_dir, config_path, subjects_cov
    ]
    subprocess.call(regr_args)

    concat_args = [
        "bash",
        os.path.join(scriptDir, "concat_mass_uv_regr_csv.sh"), scriptDir,
        finalResDir, logDir, data_dir, config_path
    ]
    subprocess.call(concat_args)

    # code to read ALL files and

    output_dict = {"config_path": config_path, "computation_phase": "local_1"}

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
