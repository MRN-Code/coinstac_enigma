import json
import os
import subprocess
import sys
from utils import listRecursive


def local_1(args):
    input_list = args["input"]

    scriptDir = "/computation/scripts/"
    resDir = args["state"]["outputDirectory"]
    logDir = args["state"]["outputDirectory"]

    data_dir = args["state"]["baseDirectory"]
    subjects_cov = os.path.join(args["state"]["baseDirectory"],
                                'covariates.csv')
    config_path = input_list["CONFIG_PATH"]

    pass_arg = [
        "bash",
        os.path.join(scriptDir, "mass_uv_regr_csv.sh"), scriptDir, resDir,
        logDir, data_dir, subjects_cov, config_path
    ]

    raise Exception(subprocess.check_output(pass_arg))

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
