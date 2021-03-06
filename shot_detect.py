import os
import shutil
import sys
import time
from threading import Thread

import numpy as np

# from . import config, unit_tests, utils
from lib import config, unit_tests, utils

# # Globals


def make_std_dev_thresh_func(multiplier):
    def std_dev_thresh_func(color_hist_diffs, a):
        std_dev = np.std(color_hist_diffs)
        return multiplier * std_dev
    return std_dev_thresh_func


def make_max_thresh_func(multiplier):
    def max_thresh_func(color_hist_diffs, a):
        return multiplier * max(color_hist_diffs)
    return max_thresh_func


STD_DEV_THRESH_FUNC = make_std_dev_thresh_func(config.THRESH_MULTIPLIER)
MAX_THRESH_FUNC = make_max_thresh_func(config.LOCAL_MAXIMA_THRESH)


# # Functions
# takes in a file name, and number of images in the file,
# and number of bins for the histogram

def shots_for_ext(ext, color_space=1, local_maxima_thresh=0.05, hist_bins=16,
                  thresh=61, resources_path=config.RESOURCES_PATH,
                  local_maxima_thresh_func=None, start=0, end=None):
    source_video_frame_directory = os.path.join(resources_path, ext)

    if not end:
        n = len([name for name in os.listdir(source_video_frame_directory)
                 if name[0] != "."])
    else:
        n = end
    fn_prefix, fn_suffix = source_video_frame_directory, "%06d.jpg"
    fn = os.path.join(fn_prefix, fn_suffix)
    first_frame = utils.get_first_frame(ext)
    color_hists = utils.color_histograms(fn, n, n_bins=hist_bins,
                                         first_frame=first_frame)

    color_hist_diffs = utils.get_hist_diffs(color_hists)
    smooth_color_hists = color_hist_diffs

    lmt = local_maxima_thresh * max(color_hist_diffs)
    color_peaks = utils.local_maxima(smooth_color_hists)
    color_inds = [i for i in range(len(color_peaks)) if color_peaks[i]]
    high_color_peaks = utils.filter_local_maxima(smooth_color_hists, color_inds, lmt,
                                                 thresh_func=local_maxima_thresh_func)

    # high_color_peaks = [i for i in range(len(color_hist_diffs))
    #                    if color_hist_diffs[i] > lmt]

    results = {}
    results['shots'] = high_color_peaks
    results['smooth'] = smooth_color_hists
    results['hists'] = color_hists
    results['data'] = color_hist_diffs
    results['thresh'] = lmt
    return results


def run_detector(resources_path, thresh=61, local_maxima_thresh=0.05,
                 local_maxima_thresh_func=None, n_bins=4, color_space=1,
                 ignore_these=config.IGNORES, limit_to=[], exts=None,
                 segments_to_run=None, segment_number=None):

    output = {}
    if not exts:
        exts = [f for f in os.listdir(resources_path) if "." not in f]
    exts = [e for e in exts if e not in ignore_these]
    if len(limit_to) > 0:
        exts = [e for e in exts if e in limit_to]

    for ext in exts:
        if segments_to_run:

            warn = "segment indices specified but no entry for ext {0} exists"
            warn = warn.format(ext)
            assert ext in segments_to_run, warn

            warn_num = "segment indices specified but segment number not given"
            assert segment_number != None, warn_num

            first, last = segments_to_run[ext][segment_number]
            results = shots_for_ext(ext, color_space, local_maxima_thresh,
                                    n_bins, thresh, first, last,
                                    local_maxima_thresh_func=local_maxima_thresh_func)
            output[segment_number][ext] = results
        else:
            results = shots_for_ext(ext, color_space, local_maxima_thresh,
                                    n_bins, thresh, local_maxima_thresh_func=local_maxima_thresh_func)
            output[ext] = results

    return output


# # Detection Work Space

def process_shots(source_video_frame_directory, start_marker, end_marker,
                  color_space=1, hist_bins=16,
                  thresh=61):

    fn_prefix, fn_suffix = source_video_frame_directory, config.FRAME_FNAME_FORMAT
    fn = os.path.join(fn_prefix, fn_suffix)
    first_frame = start_marker
    n = end_marker - start_marker
    color_hists = utils.color_histograms(fn, n, n_bins=hist_bins,
                                         first_frame=first_frame)

    color_hist_diffs = utils.get_hist_diffs(color_hists)

    results = {}
    results['hists'] = color_hists
    results['data'] = color_hist_diffs
    return results


def post_process_results(results, local_maxima_thresh_func):
    color_hist_diffs = results['data']

    color_peaks = utils.local_maxima(color_hist_diffs)
    color_inds = [i for i in range(len(color_peaks)) if color_peaks[i]]
    lmt = None
    high_color_peaks = utils.filter_local_maxima(color_hist_diffs, color_inds, lmt,
                                                 thresh_func=local_maxima_thresh_func)
    # NOTE: off by one?
    results['shots'] = high_color_peaks

    return results


def stream_shots_for_ext(source_video_frame_directory, total_frames,
                         color_space=1, hist_bins=16, thresh=61,
                         local_maxima_thresh_func=MAX_THRESH_FUNC):

    def get_frames(): return [int(os.path.splitext(f)[0]) for f in
                              os.listdir(source_video_frame_directory)]

    start_marker = 1
    end_marker = min(config.FRAME_CHUNK_SIZE + start_marker, total_frames)
    end = total_frames

    done = False

    prev_result, next_result = None, None

    while not done:
        if get_frames() and end_marker <= max(get_frames()):
            if end_marker == end:
                done = True

            next_result = process_shots(source_video_frame_directory,
                                        start_marker, end_marker)
            prev_result = next_result if not prev_result else \
                utils.stitch_results(prev_result, next_result)
            if config.CLEANUP:
                utils.delete_images(source_video_frame_directory,
                                    start_marker, end_marker)
            start_marker = end_marker
            end_marker = min(end, end_marker + config.FRAME_CHUNK_SIZE)
        time.sleep(config.WAIT_TIME)

    filtered_results = post_process_results(prev_result,
                                            local_maxima_thresh_func)

    return filtered_results


def run_movie_pipeline(source_package, output_dir=None):
    # housekeeping

    if output_dir == None:
        output_dir = source_package

    temp_frame_dir = utils.get_temp_dir(source_package)

    if not os.path.exists(temp_frame_dir):
        os.makedirs(temp_frame_dir)

    movie_file = utils.get_movie_file(source_package)
    movie_file_path = os.path.join(source_package, movie_file)

    num_total_frames = utils.find_num_frames(movie_file_path)
    stars = '*' * 80

    task = 'Decompose'
    if config.DECOMPOSE:

        ffmpeg_thread = Thread(target=utils.ffmpeg_call,
                               args=(movie_file_path, ))

        # Thread will terminate abruptly if main thread is stopped
        ffmpeg_thread.daemon = True
        ffmpeg_thread.start()

    results = stream_shots_for_ext(temp_frame_dir, num_total_frames)

    utils.write_output_text_file(results, output_dir)
    utils.write_output_csv_file(results, output_dir)

    task = 'Cleanup'
    if config.CLEANUP:
        shutil.rmtree(temp_frame_dir)

    return


'''
# EXAMPLE TEST CODE

MOVIE_SOURCE = '~/path/to/video/directory/'

run_movie_pipeline(MOVIE_SOURCE)
'''
if __name__ == '__main__':
    args = sys.argv
    movie_source = '.'

    if len(args) > 0:
        movie_source = args[1]

        if 'no_cleanup' in args:
            config.CLEANUP = False
        if 'no_decomp' in args:
            config.DECOMPOSE = False

    run_movie_pipeline(movie_source)
