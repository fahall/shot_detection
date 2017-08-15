## shot_detect
Multithreaded color-histogram based shot-detection. Takes as input a directory of movies and outputs a csv file for each movie with shot-boundary candidates. Each candidate is scored based on the algorithm's confidence that it is a shot boundary.  

#### External Dependencies
OpenCV

ffmpeg (tested on v3.3.3)

#### Python Dependencies
Python 3.6 (earlier versions not tested)

See requirements.txt

#### Input
`input_directory`: path to directory containing 1 or more video files

`output_directory`: path to directory in which to store output csvs (defaults to input directory if no arg passed)

#### Output
csv file where each row represents a potential boundary.
* The first column is the frame number (1 indexed) 
* The second column is the normalized strength
* The third column is the absolute strength


#### Sample Calls from the command line:
python3 shot_detect.py path/to/video-directory path/to/desired/output
python3 shot_detect.py path/to/video-directory 
