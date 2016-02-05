#!/usr/bin/env dls-python
# coding=utf-8

assert __name__ == '__main__'  # Don't let anyone import us.
from pkg_resources import require;  require('numpy', 'dill')

from os import path
from functools import partial, reduce

import cv2

import sys;  sys.path.append('..')
from dls_imagematch import (
    consensus_match, match, apply_tr, get_size, grain_extract)




# Note non-reference images SHOULD NOT have features near their edges.
# TODO: Could blur the reference image ahead-of-time.
# TODO: Deduplication of scale preprocessing?
# TODO: Alert/discard when out-of-bounds array indexing is averted.
# TODO: Input images with different sizes.


# Test options...
PROFILING = False
DISPLAY_PROGRESS = True
DISPLAY_RESULTS = False
OUTPUT_DIRECTORY = None
TRANSLATIONS_OUTPUT_FILE = None
CONSENSUS = False  # If True, cannot display progress.
N_PROCESSES = 8  # How many CPU cores to use (sort of).
TEST_SET = 'B'  # Test set B is more interesting than A.
CROP_AMOUNTS = [0.12]*4

INPUT_DIR_ROOT = "../test-images/old/"


# Real image dimensions, in microns... of the reference?
# (These dimensions are for test set A.)
image_physical_width, image_physical_height = map(float, (2498, 2004))


if TEST_SET == 'A':
    input_dir = INPUT_DIR_ROOT + 'translate-test-A'
    indices = [
        (1, [1, 2, 3, 4]),
        (2, [1, 2]),
        (3, [1, 2, 3, 4, 5]),
        (4, [1, 2, 3, 4, 5]),
        (5, [1, 2, 3]),
        (6, [1, 2, 3, 5]),
        (7, [1, 2, 3, 4]),  # Last one is a crazy GIMP edit...
    ]
elif TEST_SET == 'B':
    input_dir = INPUT_DIR_ROOT + 'translate-test-B'
    indices = [(i, [1, 2]) for i in range(1, 8)]


def make_gray(img):
    if len(img.shape) in (3, 4):
        return cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    else:
        return img


def table_line(strings, underline=False, separator='\t\t'):
    line = reduce(lambda x, y: x+separator+y, strings)+'\n'
    if underline:
        line += table_line(['='*len(string) for string in strings])
    return line


if TRANSLATIONS_OUTPUT_FILE is not None:
    with open(TRANSLATIONS_OUTPUT_FILE, 'w') as f:
        # Write some column headings.
        f.write(table_line(
            ('X', 'Y', 'x/px', 'y/px', 'x/um', 'y/um'), underline=True))


if PROFILING:
    import cProfile, pstats, StringIO
    pr = cProfile.Profile()
    pr.enable()


find_tr_fn = partial(consensus_match, N_PROCESSES) if CONSENSUS else match


for sample in indices:
    samp_num = sample[0]
    ref_num = sample[1][0]
    for trans_num in sample[1][1:]:
        ref_file = path.join(
            input_dir, str(samp_num)+'_'+str(ref_num)+'.png')
        trans_file = path.join(
            input_dir, str(samp_num)+'_'+str(trans_num)+'.png')
        print(ref_file, trans_file)
        ref, trans = map(cv2.imread, (ref_file, trans_file))
        ref, trans = map(make_gray, (ref, trans))

        print(str(samp_num)+'_'+str(trans_num)+'.png\n---')

        net_transform = find_tr_fn(
            ref, trans,
            debug=DISPLAY_PROGRESS, crop_amounts=CROP_AMOUNTS)

        image_width, image_height = get_size(ref)
        t = net_transform((image_width, image_height))

        delta_x = -t[0, 2]*image_physical_width/image_width
        delta_y = +t[1, 2]*image_physical_height/image_height

        print('---\ndelta_x is', delta_x, 'µm; delta_y is', delta_y, 'µm\n---')
        print(t)
        print('===')

        if TRANSLATIONS_OUTPUT_FILE is not None:
            with open(TRANSLATIONS_OUTPUT_FILE, 'a') as f:
                f.write(table_line((str(samp_num), str(trans_num),
                                    str(-t[0, 2]), str(t[1, 2]),
                                    str(delta_x), str(delta_y))))

        if DISPLAY_RESULTS:
            cv2.imshow(
                'sample'+str(samp_num)+' comparison'+str(trans_num),
                cv2.absdiff(ref, apply_tr(net_transform, trans)))
            cv2.waitKey(0)

        if OUTPUT_DIRECTORY is not None:
            cv2.imwrite(
                path.join(
                    OUTPUT_DIRECTORY,
                    str(samp_num)+'_'+str(ref_num)+'_'+str(trans_num)+'.jpg'),
                grain_extract(ref, apply_tr(net_transform, trans)))


if PROFILING:
    pr.disable()
    s = StringIO.StringIO()
    ps = pstats.Stats(pr, stream=s).sort_stats('cumulative')
    ps.print_stats()
    print(s.getvalue())