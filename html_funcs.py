def table_row(data, header = False):
    begin = " \n<tr>"
    end = "</tr>"
    mid = ' \n'.join([table_cell(d, header = header) for d in data])
    output = '\n'.join([begin, mid, end])
    
    return output


def html_header(text, level=1):
    l = str(level)
    beg, end = html_pair(''.join(['<h', l, '>']))
    string = ' '.join([beg, text, end])
    return string

def html_pair(tag_string, modifiers = ''):
    opening = tag_string
    closing = tag_string.replace('<', '</')
    opening = html_modify_tag(opening, modifiers)
    return opening, closing

def html_wrap(string, tag_string, modifiers = ''):
    o, c = html_pair(tag_string, modifiers)
    s = ' '.join([o, string, c])
    return s

def html_hyperlink(text, url):
    mod = ' '.join([' href =', url])
    s = html_wrap(text, '<a >', mod)
    return s

def html_modify_tag(raw, modifier):
    raw = raw.replace('>', ' '.join([modifier, '>']))
    return raw

def html_table(data, headers=[]):
    '''Expects data to be a 2d list of strings, where each row 
       in the list represents a row in the table'''
    
    beg, end = html_pair('<table>')
    head = ''
    if len(headers) > 0:
        head = table_row(headers, header=True)
    
    mid = ' \n'.join([table_row(d) for d in data])
    
    full_string = ' \n'.join([beg, head, mid, end])
    return full_string

def table_cell(d, header=False):
    begin = "<td>" if not header else "<th>"
    end = begin.replace('<', '</')
    return ' '.join([begin, str(d), end])

def html_img(file_path, width=256):
    beg = '<img'
    end = '>'
    
    source = ''.join(['src="', file_path, '"'])
    style = ''.join(['style="width:', str(width), 'px;"'])
    
    im_string = ' '.join([beg, source, style, end])
    return im_string
