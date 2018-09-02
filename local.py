#import glob
import os
import pandas as pd
import sys
from utils import listRecursive
from patsy import dmatrix
import regression as reg
#import sys
import ujson as json
#import warnings
#from parsers import fsl_parser
from local_ancillary import local_stats_to_dict_fsl, ignore_nans
import numpy as np


def local_1(args):
    input_list = args["input"]
    covariates = input_list["covariates"]
    dependents = input_list["dependents"]
    roi = input_list["ROI"]
    models = input_list["models"]
    filters = input_list["filters"]
    
    curr_index = 0

    covariates_file = os.path.join(args["state"]["baseDirectory"], covariates)
    y_file = os.path.join(args["state"]["baseDirectory"],
                          'metr_' + dependents[curr_index] + '.csv')
    
    X_main = pd.read_csv(covariates_file)
    y_main = pd.read_csv(y_file)
    y = y_main[roi[curr_index]]
    
    curr_model = models[curr_index]
    curr_filter = filters[curr_index]
    
    Xy = pd.concat([X_main, y], axis=1)

    try:
        Xy.query(curr_filter, inplace=True)
    except ValueError:
        pass
    
    X = Xy.loc[:, Xy.columns != roi[curr_index]]
    y = Xy.loc[:, Xy.columns == roi[curr_index]]

    X = dmatrix(curr_model, data=X, return_type='dataframe')


#    # Setting environment for the script to work seamlessly
#    scriptDir = "/computation/enigma_scripts"
#    resDir = os.path.join(args["state"]["outputDirectory"], 'results')
#    logDir = os.path.join(args["state"]["outputDirectory"], 'logs')
#
#    data_dir = args["state"]["baseDirectory"]
#    subjects_cov = os.path.join(args["state"]["baseDirectory"],
#                                'covariates.csv')
#    config_path = os.path.join(scriptDir, input_list["CONFIG_PATH"])
#
#    # Running the first script
#    regr_args = [
#        "bash",
#        os.path.join(scriptDir, "mass_uv_regr_csv.sh"), scriptDir, resDir,
#        logDir, data_dir, config_path, subjects_cov
#    ]
#    subprocess.call(regr_args)
#
#    # Running the second script
#    concat_args = [
#        "bash",
#        os.path.join(scriptDir, "concat_mass_uv_regr_csv.sh"), scriptDir,
#        resDir, logDir, data_dir, config_path
#    ]
#    subprocess.call(concat_args)
#
#    # Gather the list of ALL csv files
#    agg_file_list = glob.glob(os.path.join(resDir, '*ALL*.csv'))

    # Sending contents of the ALL files as dictionary with the file name being
    # key and contents the value
    #TODO: Can also read the files as dataframes which makes it easy to work on
    # later
#    output_contents = dict()
#    for file in agg_file_list:
#        file_name = os.path.split(file)[-1]
#        file_name = os.path.splitext(file_name)[0]
#
#        with open(file, 'r') as f:
#            lines = f.readlines()
#
#        output_contents[file_name] = lines
#
#    output_dict = {
#        "output_contents": output_contents,
#        "computation_phase": "local_1"
#    }
#

    t = local_stats_to_dict_fsl(X, y)
    beta_vector, local_stats_list, meanY_vector, lenY_vector = t
    
    X_labels = list(X.columns)
    y_labels = list(y.columns)
    lamb = 0

    output_dict = {
        "beta_vector_local": beta_vector,
        "mean_y_local": meanY_vector,
        "count_local": lenY_vector,
        "X_labels": X_labels,
        "y_labels": y_labels,
        "local_stats_dict": local_stats_list,
        "computation_phase": 'local_1',
    }

    cache_dict = {
        "covariates": X.to_json(orient='split'),
        "dependents": y.to_json(orient='split'),
        "lambda": lamb
    }

    computation_output = {"output": output_dict, "cache": cache_dict}

    return json.dumps(computation_output)


def local_2(args):
    """Computes the SSE_local, SST_local and varX_matrix_local

    Args:
        args (dictionary): {"input": {
                                "avg_beta_vector": ,
                                "mean_y_global": ,
                                "computation_phase":
                                },
                            "cache": {
                                "covariates": ,
                                "dependents": ,
                                "lambda": ,
                                "dof_local": ,
                                }
                            }

    Returns:
        computation_output (json): {"output": {
                                        "SSE_local": ,
                                        "SST_local": ,
                                        "varX_matrix_local": ,
                                        "computation_phase":
                                        }
                                    }

    Comments:
        After receiving  the mean_y_global, calculate the SSE_local,
        SST_local and varX_matrix_local

    """
    cache_list = args["cache"]
    input_list = args["input"]

    X = pd.read_json(cache_list["covariates"], orient='split')
    y = pd.read_json(cache_list["dependents"], orient='split')
#    biased_X = sm.add_constant(X.values)
    biased_X = X.values

    avg_beta_vector = input_list["avg_beta_vector"]
    mean_y_global = input_list["mean_y_global"]

    SSE_local, SST_local, varX_matrix_local = [], [], []
    for index, column in enumerate(y.columns):
        curr_y = y[column]

        X_, y_ = ignore_nans(biased_X, curr_y)

        SSE_local.append(reg.sum_squared_error(X_, y_, avg_beta_vector[index]))
        SST_local.append(
            np.sum(np.square(np.subtract(y_, mean_y_global[index]))))

        varX_matrix_local.append(np.dot(X_.T, X_).tolist())

    output_dict = {
        "SSE_local": SSE_local,
        "SST_local": SST_local,
        "varX_matrix_local": varX_matrix_local,
        "computation_phase": 'local_2'
    }

    cache_dict = {}

    computation_output = {"output": output_dict, "cache": cache_dict}
    
    return json.dumps(computation_output)


if __name__ == '__main__':

    parsed_args = json.loads(sys.stdin.read())
    phase_key = list(listRecursive(parsed_args, 'computation_phase'))

    if not phase_key:
        computation_output = local_1(parsed_args)
        sys.stdout.write(computation_output)
    elif "remote_1" in phase_key:
        computation_output = local_2(parsed_args)
        sys.stdout.write(computation_output)
    else:
        raise ValueError("Error occurred at Local")