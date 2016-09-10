import unittest
from . import config
from . import utils

class TestSuite(unittest.TestCase):

    def setUp(self):
        self.test_path = config.TEST_PATH
        self.main_path = config.RESOURCES_PATH
        
    def tearDown(self):
        pass
        
    def test_undo_offset(self):
        out_vals = [0, 1, 2, 3]
        in_vals = [10, 11, 12, 13]
        self.assertEqual(utils.undo_ground_offset(in_vals), out_vals)
    
    def test_shot_detect(self):
        exts = ['tiny_frames', 'similar_frames']
        #exts = ['similar_frames']
        #exts = ['tiny_frames']
        for ext in exts:
            ground = self.get_ground(ext)
            self.run_shot_detect(ext, ground)
            
    def get_ground(self, ext):
        output = {'hists':None,
                  'diffs':None,
                  'shots':None,
                 }
        
        if ext == 'tiny_frames':
            white_hist = [0, 0, 4, 0, 0, 4, 0, 0, 4]
            black_hist = [4, 0, 0, 4, 0, 0, 4, 0, 0]
            check_hist = [2, 0, 2, 2, 0, 2, 2, 0, 2]

            hist = [white_hist, white_hist,
                    black_hist, black_hist, black_hist,
                    white_hist, white_hist,
                    check_hist, check_hist, check_hist,
                    white_hist, white_hist]
            output['hists'] = hist
            output['diffs'] =  [0, 4, 0, 0, 4, 0, 2, 0, 0, 2, 0]
            output['shots'] = {'a':[0, 1, 4, 6, 9]}
            
        return output
    
    def test_hist_diffs(self):
        
        test_hists = np.array([[100, 50, 25, 25],
                               [50, 50, 50, 50],
                               [75, 75, 25, 25],
                               [200, 0, 0, 0]])
        expected_result = [100, 50, 25, 125]
        diffs = get_hist_diffs(test_hists).tolist()
        self.assertEqual(diffs, expected_result)
        
    
    def run_shot_detect(self, ext, ground):
        resources_path = self.test_path
        offset = utils.get_ground_truth_offset(ext, resources_path = self.test_path)
        source_video_frame_directory = os.path.join(resources_path, ext)
        n = len([name for name in os.listdir(source_video_frame_directory)
                 if name[0] != "."])
        fn_prefix, fn_suffix = source_video_frame_directory, "%06d.jpg"
        fn = os.path.join(fn_prefix, fn_suffix)
        color_hists = color_histograms(fn,n, n_bins = 3, first_frame=offset)  
        hists = color_hists.tolist()
        
        
        do_ground_compare = ground['hists'] != None
        
        if do_ground_compare:
            num_frames = len(ground['hists'])
            self.assertEqual(len(hists), num_frames)        
            self.assertListEqual(hists, ground['hists'])
        
        
        color_hist_diffs = np.array([distance.chebyshev(color_hists[i-1],
                                                        color_hists[i])
                                     for i in range(len(color_hists))
                                     if i != 0])
        
        if do_ground_compare:
            self.assertListEqual(color_hist_diffs.tolist(), ground['diffs'])
        
        
        smooth_color_hists = smooth_hanning(color_hist_diffs, 2)
        
        color_peaks = utils.local_maxima(color_hist_diffs)
        
        
        color_inds = [i for i in range(len(color_peaks)) if color_peaks[i]]
        high_color_peaks = utils.filter_local_maxima(smooth_color_hists,
                                               color_inds, 0.5)
        
        results = {'a':{'shots':high_color_peaks.tolist(),
                        'smooth':smooth_color_hists.tolist()}}

        if do_ground_compare:
            verts = ground['shots']
        else:
            verts = {'a':[0]}
        plot_all_shots(results, verts,'hist_test')
    
    

def run_unit_tests():
    suite = unittest.TestLoader().loadTestsFromTestCase(TestSuite)
    unittest.TextTestRunner(verbosity=3).run(suite)
    


