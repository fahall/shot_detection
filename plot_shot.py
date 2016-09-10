import matplotlib.pyplot as plt
from matplotlib import gridspec
from . import html_funcs as web
from . import config



def plot_shots(high_color_peaks, smooth_color_hists, ground_data, title='Movie',\
               detector='Detector'):
    fig = plt.figure(figsize=(20,5))
    ax = fig.add_subplot(111)
    make_subplot(ax, high_color_peaks, smooth_color_hists, ground_data, title,\
                 detector)
    plt.plot(smooth_color_hists)
    plt.plot(high_color_peaks, [smooth_color_hists[i] for i in\
                                high_color_peaks], "ro")
    for g in ground_data:
        plt.axvline(g,linewidth=1, color='y')
    
def make_subplot(subplot, data, smooth, ground, title, detector):
    subplot.set_yscale('log')
    subplot.plot(smooth)
    subplot.plot(data, [smooth[int(i)] for i in data], "ro")
    for g in ground:
        subplot.set_title(' - '.join([detector, title]))
        subplot.axvline(g,linewidth=1, color='y')


def shots_to_binary_vec(shot_list, length = 0):
    mx = max(shot_list)
    mx = max(mx, length)
    output = np.array([1 if x in shot_list else 0 for x in range(mx)])
    return output

def plot_all_shots(data, ground, title):

    col = 0
    row = 0
    num_col = 1
    num_row = len(data)
    gs = gridspec.GridSpec(num_row, num_col)
    fig = plt.figure(figsize=(num_col * 10, num_row * 3))
    fig.set_size_inches(20, 50)
    for ext in sorted(data):
        row += 1
        idx = (row-1) * num_col + col
        ax = fig.add_subplot(gs[idx - 1])
        make_subplot(ax, data[ext]['shots'], data[ext]['smooth'],
                     utils.undo_ground_offset(ground[ext]), '', str(ext))
    
    save_location = os.path.join('/Users/alexhall/Desktop',
                                 ''.join([title, '.png']))
    print(save_location)
    fig.savefig(save_location)
    

def analyze_shot_boundaries(ground_shots, probs, peaks):
    probs = np.array(probs)
    prob_filter = shots_to_binary_vec(peaks, len(probs))
    probs = probs * prob_filter
    truth = shots_to_binary_vec(undo_ground_offset(ground_shots), len(probs))
    print(len(ground_shots), len(probs), len(truth))
    precision, recall, thresholds = precision_recall_curve(truth, probs)
    average_precision = average_precision_score(truth, probs)

    return precision, recall, thresholds, average_precision


def plot_accuracy(ground, predictions, show_plot=True):
    results = {}
    
    color_list = [
        "#a6cee3",
        "#1f78b4",
        "#b2df8a",
        "#33a02c",
        "#ffff00",
        "#fb9a99",
        "#fb9a99",
        "#fdbf6f",
        #"#ff7f00",
    ]
    
    
    
    
    mean_ap = 0
    for title in predictions.keys():
        d = {}
        p, r, t, ap = analyze_shot_boundaries(ground['ground'][title],
                                              predictions[title]['data'],
                                              predictions[title]['shots'])
        
        d['precision'] = p
        d['recall'] = r
        d['threshold'] = t
        d['average_precision'] = ap
        
        results[title] = d
        
        mean_ap += ap 
        
    mean_ap = mean_ap / len(predictions.keys())
        
        
    # Plot Precision-Recall curve
    plt.clf()
    c_idx = 0

    for title in results:
        r = results[title]['recall']
        p = results[title]['precision']
        plt.plot(r, p, label=title + '(area = {0:0.2f})'
                 .format(results[title]['average_precision']),
                 color = color_list[c_idx])
        c_idx += 1
        if c_idx >= len(color_list):
            c_idx = 0

        
        
    plt.xlabel('Recall')
    plt.ylabel('Precision')
    plt.ylim([0.0, 1.05])
    plt.xlim([0.0, 1.0])
    plt.title('Precision-Recall: Mean AUC={0:0.2f}'.format(mean_ap))
    plt.legend(bbox_to_anchor=(1.8, 1))
        
    
    
    
    if show_plot:
        plt.show()
    
    return results


def union(a, b):
    """ return the union of two lists """
    return list(set(a) | set(b))

def get_filtered_shot_ranges(a, b, dist):
    values = union(a, b)
    values = sorted(values)
    max_val = max(values)
    valids = []
    for v in values:
        s = []
        for i in range(max(0, v - dist), min(max_val, v + dist + 1)):
            s.append(i)
        valids.append(s) 
    
            
    return valids
    



def create_shot_visualization(results, ground, im_root, out_path,
                              filename = 'shot_visualization.html'):
    
    titles = [m for m in sorted(results.keys())]
    

    for t in titles: #titles:
        html_string = ''
        g_data = ground
        mov_table = get_movie_table(results[t], t, g_data, im_root)
        html_string = ' \n'.join([html_string, mov_table]) 
        index = os.path.join(out_path,
                             filename.replace('.html', '_' + t + '.html'))
        with open(index, 'w') as html:
            html.write(html_string)
        
    return html_string

def get_movie_table(data, title, ground_data, im_root, num_cols = 10):
    offset = utils.get_ground_truth_offset(title, ground_data)
    header = web.html_header(title)
    
    shots = [d + offset for d in data['shots']]
    
    valids = get_filtered_shot_ranges(ground_data[title], shots, 1)
    
    t_rows = []
    shot_row = []
    last_frame = max(ground_data[title])
    for row in valids:
        shot_row = []
        for frame in row:

#             if(frame - valids[f - 1] > 1 and len(shot_row) > 0):
#                 t_rows.append(shot_row)
#                 shot_row = []

            f_num = int(frame)


            check, color = get_truth_style(f_num, ground_data[title], im_root)
            im_str = get_frame_img(f_num, im_root, title)
            det_check, det_col = get_truth_style(f_num, shots, im_root,
                                                 true_im = 'purple_circle.png')

            if color != '':
                im_str = web.html_wrap(im_str, '<span> ',
                                       ' style = \"background-color: ' + color +
                                       '\"')
            im_str = im_str + '<br/>' + check + str(f_num) + det_check
            
            index = frame - offset
            diff_str = '<br/>\n Diff ' + str(data['data'][index])
#             hist = data['hists'][index]
#             hist = ['%1.0f' % x for x in hist]
#             hist_str = '<br/>\n Hist ' + str(hist)
            full_str = '\n'.join([im_str, diff_str])
            shot_row.append(full_str)
        t_rows.append(shot_row)
        
        

    table_string = web.html_table(t_rows)
    head_and_table = ' \n'.join([header, table_string])
    return head_and_table
    
def get_frame_img(f_num, im_root, title):
    f_txt = str(f_num).zfill(6)
    im_file = ''.join([f_txt, '.jpg'])
    f_path = os.path.join(im_root, title, im_file)
    im_str = web.html_img(f_path)
    return im_str
    

def get_truth_style(f_num, data, im_root, ico_width=16, red_x = False,
                    true_im = 'green_check.png', false_im = 'red_x.png'):
    exists = f_num in data
    
    check_file = os.path.join(im_root, true_im)
    check_im = web.html_img(check_file, width=ico_width)
    
    x_file = os.path.join(im_root, false_im)
    x_im = web.html_img(x_file, width=ico_width)
    
    false_string = x_im if red_x else ''
    
    st = check_im if exists else false_string
    green = '#b2df8a'
    red = '#800000'
    color = green if exists else ''

    return st, color
    
