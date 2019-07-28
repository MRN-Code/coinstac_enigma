import os
import sys
import warnings

import numpy as np
import pandas as pd
import ujson as json
from patsy import dmatrix

import regression as reg
from local_ancillary import ignore_nans, local_stats_to_dict_fsl
from utils import listRecursive

warnings.simplefilter("ignore")


def local_1(args):
    input_list = args["input"]

    covariates = input_list["covariates"]
    dependents = input_list["dependents"]
    roi = input_list["ROI"]
    models = input_list["models"]
    filters = input_list["filters"]

    covariates_file = os.path.join(args["state"]["baseDirectory"], covariates)
    X_main = pd.read_csv(covariates_file)

    for curr_model, curr_filter in zip(models, filters):
        for curr_roi in roi:
            for curr_dependent in dependents:
                y_file = os.path.join(args["state"]["baseDirectory"],
                                      'metr_' + curr_dependent + '.csv')

                y_main = pd.read_csv(y_file)
                y = y_main[curr_roi]

                Xy = pd.concat([X_main, y], axis=1)

                try:
                    Xy.query(curr_filter, inplace=True)
                except ValueError:
                    pass

                X = Xy.loc[:, Xy.columns != curr_roi]
                y = Xy.loc[:, Xy.columns == curr_roi]

                X = dmatrix(curr_model, data=X, return_type='dataframe')

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
