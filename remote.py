import json
import sys
from utils import listRecursive


def remote_1(args):
    input_list = args["input"]

    config_path = [input_list[site]["config_path"] for site in input_list]
    output_dict = {"config_path": config_path}

    computation_output = {"output": output_dict, "success": True}

    return json.dumps(computation_output)


if __name__ == '__main__':

    parsed_args = json.loads(sys.stdin.read())
    phase_key = list(listRecursive(parsed_args, 'computation_phase'))

    if 'local_1' in phase_key:
        computation_output = remote_1(parsed_args)
        sys.stdout.write(computation_output)
    else:
        raise ValueError("Error occurred at Remote")
