import sys

def make_std_dev_thresh_func(multiplier):
    def std_dev_thresh_func(x, a):
        std_dev = np.std(x)
        return multiplier*std_dev
    return std_dev_thresh_func


OUTPUT_TXT_FNAME = 'shots.txt'
OUTPUT_CSV_FNAME = 'shots.csv'
SOURCE_FRAME_DIR = 'temp_frames'

FRAME_FNAME_FORMAT = '%06d.jpg'
FILE_TYPES = ['.mp4', '.m4v', '.mkv']
IGNORES = ['movie_title_to_ignore']

THRESH_MULTIPLIER = 0.5

WAIT_TIME = 0.5
DEFAULT_NUM_SEGMENTS = 10
FRAME_CHUNK_SIZE = 10000

CLEANUP = False #Delete images when finished
DECOMPOSE = False #Convert movie file into images


######## TRAIN & TEST ONLY ########
RESOURCES_PATH = "/Users/alexhall/Documents/filmGrammar/deepak_ground_truth/frames/"
GROUND_DIR = '/Users/alexhall/Documents/filmGrammar/deepak_ground_truth/classification_shot/ground_truth_0_index'
TEST_PATH = '/Users/alexhall/Documents/filmGrammar/deepak_ground_truth/test_dataset'
LOCAL_MAXIMA_THRESH = 0.1
VAL = 0.5
THRESH_FUNC = lambda x, a : VAL
