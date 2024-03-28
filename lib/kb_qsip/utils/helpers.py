

import rpy2
import rpy2.robjects as robjects
from rpy2.robjects.packages import importr, data

from installed_clients.WorkspaceClient import Workspace
from typing import Any

qsip2 = importr('qSIP2')
qsip2_data = data(qsip2)

# source data
def get_source_df(params, ws_client):
    
    if 'debug' in params and params['debug']:
        source_df = qsip2_data.fetch('example_source_df')['example_source_df']

        # AJ... make df (either csv in scratch, or pandas df) from KBaseSets.SampleSet
        ref = get_object_by_ref(params['source_data'], ws_client)
        # print(ref)
        # converted = convert_samples(ref)
        # print(converted)

    else:
        # get logic to import via kbase api
        pass

    return source_df

def make_source_object(source_df, params):

    # validation checks are all run inside qSIP2 R package
    source_data = qsip2.qsip_source_data(source_df,
                                         isotope = params['M_isotope'], 
                                         source_mat_id = params['M_source_mat_id'],
                                         isotopolog = params['M_isotopolog'])
    
    return source_data


# sample data
def get_sample_df(params):
    
    if 'debug' in params and params['debug']:
        sample_df = qsip2_data.fetch('example_sample_df')['example_sample_df']

        # AJ... make df (either csv in scratch, or pandas df) from KBaseSets.SampleSet
    else:
        # get logic to import via kbase api
        pass

    return sample_df

def make_sample_object(sample_df, params):

    if params['calculate_gradient_pos_rel_amt']:
        
        # If relative amounts are not already calculated, then do this now
        sample_df = qsip2.add_gradient_pos_rel_amt(sample_df,
                                                   source_mat_id = params['S_source_mat_id'], 
                                                   amt = params['S_gradient_pos_rel_amt'])
        
        # set the params to the newly generated column
        params['S_gradient_pos_rel_amt'] = 'gradient_pos_rel_amt'

    # validation checks are all run inside qSIP2 R package
    sample_data = qsip2.qsip_sample_data(sample_df,
                                         sample_id = params['S_sample_id'], 
                                         source_mat_id = params['S_source_mat_id'],
                                         gradient_position = params['S_gradient_position'],
                                         gradient_pos_density = params['S_gradient_pos_density'],
                                         gradient_pos_amt = params['S_gradient_pos_amt'],
                                         gradient_pos_rel_amt = params['S_gradient_pos_rel_amt'])
    
    return sample_data




# feature data
def get_feature_df(params):
    
    if 'debug' in params and params['debug']:
        feature_df = qsip2_data.fetch('example_feature_df')['example_feature_df']


        # AJ... make df (either csv in scratch, or pandas df) from KBaseMatrices.AmpliconMatrix 

    else:
        # get logic to import via kbase api
        pass

    return feature_df

def make_feature_object(feature_df, params):

    # validation checks are all run inside qSIP2 R package
    feature_data = qsip2.qsip_feature_data(feature_df,
                                         feature_id = params['F_feature_ids'], 
                                         type = params['F_type'])
    
    return feature_data

# qsip object
def make_qsip_object(source_data, sample_data, feature_data):
    
    # validation checks are all run inside qSIP2 R package
    q = qsip2.qsip_data(source_data, sample_data, feature_data)

    return(q)







'''

# from combinatrix app
def get_info(ws_output: dict[str, Any]) -> dict[str, Any]:
    """Get the "infostruct" dictionary from a workspace object.

    :param ws_output: object from the workspace
    :type ws_output: dict[str, Any]
    :raises KeyError: if there is no "infostruct" key
    :return: contents of infostruct
    :rtype: dict[str, Any]
    """
    if not ws_output.get(INFO):
        err_msg = f"Cannot find an '{INFO}' key"
        raise KeyError(err_msg)
    return ws_output[INFO]


def get_upa(ws_output: dict[str, Any]) -> str:
    """Retrieve the UPA from a workspace infostruct.

    :param ws_output: workspace object, including the "infostruct" key/value
    :type ws_output: dict[str, Any]
    :return: KBase UPA
    :rtype: str
    """
    infostruct = get_info(ws_output)
    return f"{infostruct['wsid']}/{infostruct['objid']}/{infostruct['version']}"

def get_object_by_ref(ref, ws_client):
    # based off https://github.com/kbaseapps/kb_combinatrix/blob/0c178d4c32c8428f036c4fd236046fe9f2316e42/lib/combinatrix/fetcher.py#L70

    results = ws_client.get_objects2(
            {
                "objects": [{"ref": ref}],
                "ignoreErrors": 1,
                "infostruct": 1,
                "skip_external_system_updates": 1,
            }
        )["data"]

    output = {}
    for item in results:
        # check for any samplesets that need to be populated
        #if "SampleSet" in get_data_type(item):
        item["data"]["sample_data"] = fetch_samples(item["data"]["samples"])
            
        # store in a dict indexed by UPA
        output[get_upa(item)] = item  # {INFO: item[INFO], DATA: item[DATA]}

    return output

def fetch_samples(
        self: "DataFetcher", sample_list: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        """Retrieve sample data from the sample service.

        :param self: class instance
        :type self: DataFetcher
        :param sample_list: list of dicts containing sample IDs and version
        :type sample_list: list[dict[str, Any]]
        :raises RuntimeError: if there are any issues with fetching from the Sample Service
        :return: list containing data from the Sample Service
        :rtype: list[dict[str, Any]]
        """
        headers = {"Authorization": self.token, "Content-Type": "application/json"}
        payload = {
            "method": "SampleService.get_samples",
            "id": str(uuid.uuid4()),
            "params": [
                {
                    "samples": [
                        {"id": sample["id"], "version": sample["version"]}
                        for sample in sample_list
                    ],
                }
            ],
            "version": "1.1",
        }

        resp = requests.post(
            url=self.sample_service_url, headers=headers, data=json.dumps(payload)
        )
        resp_json = resp.json()
        if resp_json.get("error"):
            err_msg = f"Error from SampleService - {resp_json['error']}"
            raise RuntimeError(err_msg)
        return resp_json["result"][0]

# def convert_samples(object_data: dict[str, Any]) -> dict[str, Any]:
#     """Parse sample data and flatten it out for combinatrixing.

#     :param sample_list: the `sample_data` value
#     :type sample_list: list[dict[str, Any]]
#     :return: dict containing the fieldnames and a list of samples data dicts
#     :rtype: dict[str, Any]
#     """
#     sample_data = object_data.get("data", {}).get("sample_data")
#     if not sample_data:
#         err_msg = f"{get_upa(object_data)}: no 'data.sample_data' field found"
#         raise ValueError(err_msg)

#     keys = {
#         "all": set(),
#         "user": set(),
#         "controlled": set(),
#     }
#     parsed_samples = []
#     for sample in sample_data:
#         sample_data = deepcopy(sample)
#         del sample_data["node_tree"]

#         # move the interesting data from under 'node_tree' up
#         sample_name = sample["name"]
#         sample_node_trees = [
#             nt for nt in sample["node_tree"] if sample_name == nt["id"]
#         ]
#         if len(sample_node_trees) != 1:
#             err_msg = f"{get_upa(object_data)}: incorrect number of sample node trees for sample {sample['id']}, {sample['name']}"
#             raise ValueError(err_msg)

#         snt = sample_node_trees[0]
#         sample_data["type"] = snt["type"]

#         # the data is in `snt` under the keys
#         # "meta_controlled" and "meta_user"
#         for key_type in ["user", "controlled"]:
#             m_key = f"meta_{key_type}"
#             if m_key in snt and snt.get(m_key, []):
#                 keys[key_type].update(snt.get(m_key).keys())
#                 for key in snt.get(m_key, []):
#                     node_value = snt[m_key][key]
#                     value = None
#                     # check if it's in value/units form
#                     if set(node_value.keys()) == {"value", "units"}:
#                         value = f"{node_value['value']} {node_value['units']}"
#                     elif set(node_value.keys()) == {"value"}:
#                         value = node_value["value"]
#                     else:
#                         print(
#                             f"unrecognised configuration: keys: {', '.join(node_value.keys())}"
#                         )
#                         value = json.dumps(node_value, indent=0)
#                     sample_data[key] = value

#         parsed_samples.append(sample_data)
#         keys["all"].update(sample_data.keys())

#     return {
#         KEYS: {
#             "controlled": keys["controlled"],
#             "user": keys["user"],
#         },
#         FN: keys["all"],
#         DL: parsed_samples,
#     }



'''