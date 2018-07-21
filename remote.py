import json
import os
import sys
from utils import listRecursive


def remote_1(args):
    input_list = args["input"]
    site_ids = list(input_list.keys())

    # Getting all the file names
    file_names = list(input_list[site_ids[0]]["output_contents"].keys())
    
    # Getting the header from each file
    file_headers = [
        input_list[site_ids[0]]["output_contents"][key][0]
        for key in file_names
    ]

    # Associating file names with their headers as a dictionary
    file_headers = dict(zip(file_names, file_headers))

    # Creating files and concatenating contents from different local sites and
    # putting then in the file
    for file in file_names:
        with open(
                os.path.join(args["state"]["outputDirectory"], file + '.csv'),
                'w+') as f:
            f.writelines(['"site",', file_headers[file]])
            for site in site_ids:
                for line in input_list[site]["output_contents"][file][1:]:
                    f.writelines(['"' + site + '",', line])

#    for file in file_names:
#        a = list()
#        for site in site_ids:
#            df = pd.DataFrame(input_list[site]["output_contents"][file])
#            df = df[0].apply(lambda x: pd.Series(x.split(',')))
#            df.columns = df.iloc[0]
#            df.columns = df.columns.str.replace('"', '').str.replace('\n','')
#            df.drop(df.index[0], inplace=True)
#            a.append(df)
#
#        df = pd.concat(a, ignore_index=True)
#
#        file_name = os.path.join(args["state"]["outputDirectory"],
#                                 file + '.csv')
#        df.to_csv(file_name, index=False)

    computation_output = {
        "output": "Results files sent to remote",
        "success": True
    }

    return json.dumps(computation_output)

if __name__ == '__main__':

    parsed_args = json.loads(sys.stdin.read())
    phase_key = list(listRecursive(parsed_args, 'computation_phase'))

    if 'local_1' in phase_key:
        computation_output = remote_1(parsed_args)
        sys.stdout.write(computation_output)
    else:
        raise ValueError("Error occurred at Remote")
