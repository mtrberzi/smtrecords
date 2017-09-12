#!/usr/bin/env python3

import sys
import os
import tempfile
import json
import argparse

from collections import OrderedDict

# constants
LABEL_FONTSIZE    = 10
TITLE_FONTSIZE    = 14
SUBTITLE_FONTSIZE = 10

DESCRIPTION = '''
Make a cactus plot from given datasets and print it in PNG format on stdout.

notes:
  no check is made to see if the datasets have the same problems
  the datasets are not required to be of the same size

dataset format:
  [
      {
          "problem": "/path/to/problem",
          "result":  "sat"|"unsat"|"unknown"|"timeout"|"parsing error",
          "solver":  "solver name",
          "elapsed": 1.0 // time it took, as a float
      },
      ...
  ]
'''

# helpers
def plottable(row):
    return (
        row['result'] == 'sat' or
        row['result'] == 'unsat'
    )

def get_solver_name(dataset):
    return dataset[0]['solver']

def data2png(raw_data, title):

    # configure plot library to use SVG
    import numpy as np
    import matplotlib
    matplotlib.use('svg')
    import matplotlib.pyplot as pyplot
    import matplotlib.ticker

    # set axis labels and graph title
    pyplot.title(title + '\n', fontsize=TITLE_FONTSIZE)
    pyplot.xlabel('number of solved instances', fontsize=SUBTITLE_FONTSIZE)
    pyplot.ylabel('time (s)', fontsize=LABEL_FONTSIZE, labelpad=12)

    # sort the data sets by solver name
    raw_data = sorted(raw_data, key=lambda x: get_solver_name(x))

    # groom the data:
    #   - remove the incomplete points
    #   - sort the remaining points
    groomed_data = []
    for points in raw_data:
        kept_points   = filter(plottable, points)
        sorted_points = sorted(kept_points, key=lambda x: x['elapsed'])
        groomed_data.append(sorted_points)

    # determine axis limits
    min_x = 0
    max_x = max(len(points) for points in groomed_data)
    min_y = 0
    max_y = max(max(point['elapsed'] for point in points) for points in groomed_data)

    # set axis limits
    pyplot.axis([min_x, max_x, min_y, max_y])
    # use colours
    colourmap = pyplot.cm.get_cmap(name="plasma")
    colours = [colourmap(i) for i in np.linspace(0, 0.9, len(groomed_data))]
    
    # add the data points
    for points in groomed_data:
        x = range(len(points))
        y = [point['elapsed'] for point in points]
        pyplot.plot(x, y, color=colours[0], linestyle='solid', marker='.', label=get_solver_name(points))
        colours = colours[1:] # pop last used colour

    # put the legend somewhere sensible
    ax = pyplot.gca()
    box = ax.get_position()
#    ax.set_yscale("log", nonposy='clip')
    ax.set_ylim(ymin=0.001, ymax=max_y*1.1)

#    ax.set_position([box.x0, box.y0, box.width * 0.8, box.height])
    lgd = pyplot.legend(loc='center left', bbox_to_anchor=(0, -0.2));

    # make a temporary file to store the graph
    # FIXME:
    #       this is here because I don't know how to make pyplot
    #       print the graph to something other than a file
    # NOTE:
    #      doing an instant close() of the file because pyplot will open it
    #      on its own, and will close it on its own, after which we will
    #      manually open it on our own
    fd, path = tempfile.mkstemp(suffix='.png')
    os.close(fd)

    # save the graph
    pyplot.savefig(path, bbox_extra_artists=(lgd,), bbox_inches='tight')

    # read the graph back
    with open(path, 'rb') as graph_file:
        png = graph_file.read()

    return png

def main():

    # create arg parser
    parser = argparse.ArgumentParser(
        description     = DESCRIPTION,
        formatter_class = argparse.RawTextHelpFormatter
    )
    parser.add_argument(
        'name',
        type = str,
        help = 'name of the experiment (used in the title)'
    )
    parser.add_argument(
        'timeout',
        type = float,
        help = 'timeout with which the results were gathered (used in the title)'
    )
    parser.add_argument(
        'datasets',
        metavar = 'dataset',
        type    = str,
        nargs   = '+',
        help    = 'JSON file with benchmark results in the described format'
    )

    # parse args
    args = parser.parse_args()

    # load data
    data = {}
    for dataset_path in args.datasets:

        # read file
        with open(dataset_path, 'r') as file:
            points = json.load(file)

        # add points
        for point in points:
            solver = point['solver']

            # create dataset for the solver
            if solver not in data:
                data[solver] = []

            # add the point to the dataset if it's plottable
            if plottable(point):
                data[solver].append(point)

    # check data size
    if len(data) < 1:
        print('ERROR: no data', file=sys.stderr)
        exit(1)

    # drop empty data sets
    empty_set_names = []
    for solver, points in data.items():
        if len(points) < 1:
            print('WARNING: no plottable points for solver {}'.format(solver), file=sys.stderr)
            empty_set_names.append(solver)

    for name in empty_set_names:
        data.pop(name)

    # get largest data set size
    size = max(map(len, data.values()))

    # make title
    title = '{}: {} problems, {}-s timeout'.format(args.name, size, args.timeout)

    # print PNG image
    sys.stdout.buffer.write(data2png(data.values(), title))

