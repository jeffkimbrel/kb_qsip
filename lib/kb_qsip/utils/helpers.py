

import rpy2
import rpy2.robjects as robjects
from rpy2.robjects.packages import importr, data

qsip2 = importr('qSIP2')
qsip2_data = data(qsip2)

# source data
def get_source_df(params):
    
    if params['debug']:
        source_df = qsip2_data.fetch('example_source_df')['example_source_df']
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
    
    if params['debug']:
        sample_df = qsip2_data.fetch('example_sample_df')['example_sample_df']
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
    
    if params['debug']:
        feature_df = qsip2_data.fetch('example_feature_df')['example_feature_df']
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
