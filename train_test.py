import os
from . import shot_detect as sd
from . import config
from . import utils

def get_n_for_ext(ext, resources_path=config.RESOURCES_PATH):
    source_video_frame_directory = os.path.join(resources_path, ext)
    n = len([name for name in os.listdir(source_video_frame_directory)
             if name[0] != "."])
    return n

def make_segment_inds_for_ext(ext, num_segments=config.DEFAULT_NUM_SEGMENTS,
                              resources_path=config.RESOURCES_PATH):
    n = get_n_for_ext(ext)
    inds = split_into_segment_inds(ext, num_segments)
    return inds

def make_fold_inds(exts_considered, num_groups=config.DEFAULT_NUM_SEGMENTS,
                   resources_path=config.RESOURCES_PATH):
    segment_inds = dict()
    for ext in exts_considered:
        segment_inds[ext] = make_segment_inds_for_ext(ext, num_groups,
                                                      resources_path)
    return segment_inds

# This uses folds consisting of segments
def run_k_folds(exts_considered, make_thresh_func,
                num_groups=config.DEFAULT_NUM_SEGMENTS,
                resources_path=config.RESOURCES_PATH):
    segment_dict = make_fold_inds(exts_considered, num_groups, resources_path)
    best_thresholds = []

def test():
    for ext in exts_considered:
        for i in range(num_groups):
            lmt_func = make_thresh_func(thresh_val)
            results_dict[i] = sd.run_detector(config.RESOURCES_PATH,
                                           local_maxima_thresh_func = lmt_func,
                                           ignore_these=ignore_these,
                                           exts=all_exts)

            
def run_detector_multi_thresh(exts_to_run, make_thresh_func, all_exts,
                              num_groups=config.DEFAULT_NUM_SEGMENTS):
    #thresh_vals = list(np.arange(.25,2.25,.125))
    seg_dict = make_fold_inds(exts_to_run, num_groups)
    thresh_vals = list(np.arange(.5,2.5,.5))
    max_mean_ap, best_thresh = None, None
    ignore_these = [e for e in all_exts if e not in exts_to_run]
    #print(exts_to_run, all_exts, ignore_these)
    print("in multi thresh with {0} \n {1}".format(exts_to_run, all_exts))
    for thresh_val in thresh_vals:
        # TODO: Complete
        lmt_func = make_thresh_func(thresh_val)
        results = sd.run_detector(config.RESOURCES_PATH,
                               local_maxima_thresh_func = lmt_func,
                               ignore_these=ignore_these, exts=all_exts)
        # Compute mean AUC
        ground = {'ground':utils.batch_get_shots(config.GROUND_DIR)}
        info = plot_accuracy(ground, results, True)
        mean_ap = np.mean([info[title]['average_precision'] for title
                           in info.keys()])
        max_mean_ap, best_thresh = (mean_ap, thresh_val)\
                                   if (max_mean_ap is None \
                                       or mean_ap > max_mean_ap)\
                                   else (max_mean_ap, best_thresh)
        
    return (max_mean_ap, best_thresh)



def split_into_groups(lst, num_groups):
    length = len(lst)
    group_sizes = np.array([length/num_groups for i in range(num_groups)]) +\
                  np.array([1 for i in range(length % num_groups)] +\
                           [0 for i in range(num_groups-(length % num_groups))])
    sums = [sum(group_sizes[:i]) for i in range(len(group_sizes))]
    return [lst[k:k + i] for k,i in zip(sums, group_sizes)]

def split_into_segment_inds(n, num_groups):
    length = n
    group_sizes = np.array([length/num_groups for i in range(num_groups)]) +\
                  np.array([1 for i in range(length % num_groups)] +\
                           [0 for i in range(num_groups-(length % num_groups))])
    sums = [sum(group_sizes[:i]) for i in range(len(group_sizes))]
    return [(k, k + i) for k,i in zip(sums, group_sizes)]
    
