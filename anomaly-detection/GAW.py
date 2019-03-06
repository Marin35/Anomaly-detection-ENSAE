import scipy
from math import ceil
from utils import p_val_upper
import pandas as pd
import numpy as np
import scipy.stats

def weight_to_dict(G):
    '''
        Utilities to store the weight of all edges from a node in a dict.
        Also return the list of all the weights in the network.
        
        G (nxnetwork) : The network for which to store the stats
    '''
    W_nodes = {} # Store the list of weight for each nodes
    W_full = [] # Store all weight
    for s_in, s_out, w in G.edges(data = "weight"):
        W_full.append(w)
        for i in [s_in, s_out]:
            if i in W_nodes:
                W_nodes[i].append(w)
            else:
                W_nodes[i] = [w]
    return W_nodes, W_full


def GAW_G(G):
    W_nodes, W_full = weight_to_dict(G)
    res = {}
    for i, W in W_nodes.items():
        res[i] = scipy.stats.mstats.gmean(W)
    return res
        


def group_by_deg(deg_stat):
    '''
        Group the weight distribution of all nodes by its degree.
        Return a dictionary with the degree as keys and that stores
            the list of nodes and their edge weight in a list
    '''
    deg_grouped = {}
    for i, W in deg_stat.items():
        d = len(W)
        if d in deg_grouped:
            deg_grouped[d][0].append(i)
            deg_grouped[d][1].append(W)
        else:
            deg_grouped[d] = [[i], [W]]
    return deg_grouped
    

def GAW_with_null(G, levels, N_draw = 10000, p_val_threshold = 0.05):
    # Group the nodes by degree
    W_nodes, W_full = weight_to_dict(G)
    deg_grouped = group_by_deg(W_nodes) # For each degree, the nodes and their edges weights
    
    # Compute the GAW with the null for each degree
    feats = pd.DataFrame(index = G.nodes())
    for d , (nodes_d, W_d) in deg_grouped.items():
        print("Computing GAW for degree {} for {} nodes...".format(d, len(nodes_d)))
        W_d = np.array(W_d)
        W_d.sort(axis=0)
        W_null = np.random.choice(W_full, size = (N_draw, d))
        GAW_null = GAW_levels(W_null, levels)
        GAW_d = GAW_levels(W_d, levels)
        
        # Compute p_va for each level
        for i, (V, D) in enumerate(zip(GAW_d, GAW_null)):
            p_val = p_val_upper(V, D)
            V[p_val > p_val_threshold] = 0
            feats.loc[nodes_d, i] = V
            
    feats_name = ["GAW_{}".format(level) for level in levels]
    feats.columns = feats_name
    return feats


def GAW_levels(X, levels):
    '''
        Compute the GAW statistic for all value in X and all levels defined.
        
        X      : the value for the GAW stats
        levels : different level for which to compute the GAW stats 
    '''
    n, d = X.shape
    GAW = []
    for level in levels:
        d_level = ceil(d*level)
        GAW_level = scipy.stats.mstats.gmean(X[:, -d_level:], axis = -1)
        GAW.append(GAW_level)
    return GAW    