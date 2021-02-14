#!/usr/bin/python

import sys
import os
import sqlite3
import matplotlib as mpl
from matplotlib import pyplot as plt
from cycler import cycler

import numpy as np
from pprint import pprint

def main():
    if len(sys.argv) < 2:
        print('usage: sqlite_file ...')
        sys.exit()
    db_filenames = sys.argv[1:]
    num_of_dbs = len(db_filenames)
    conn = sqlite3.connect(":memory:")
    c = conn.cursor()

    for i in range(num_of_dbs):
        sql = "ATTACH DATABASE '{}' as db{}".format(db_filenames[i], i)
        c.execute(sql)

    sql = 'SELECT text'
    for i in range(num_of_dbs):
        sql += ', SUM(db{}) as db{}'.format(i, i)
    sql += ' FROM (\n'
    for i in range(num_of_dbs):
        if i > 0:
            sql += '    UNION\n'
        sql += '    SELECT text'
        for j in range(num_of_dbs):
            if i == j:
                sql += ', SUM(end - start)'
            else:
                sql += ', 0'
            sql += ' as db{}'.format(j)
        sql += ' FROM db{}.NVTX_EVENTS WHERE text IS NOT NULL GROUP BY text\n'.format(i)
    sql += ') GROUP BY text'
    # print(sql)

    labels = []
    durations = []
    for row in c.execute(sql):
        #print(row)
        labels.append(row[0])
        durations.append(row[1:])
    conn.close()
    x = np.arange(len(labels))
    height = (len(labels) - 1) / (num_of_dbs * len(labels))

    n = num_of_dbs
    plt.rcParams['axes.prop_cycle']  = cycler(color=[plt.get_cmap('hot')(1. * i/n) for i in range(n)])
    fig, ax = plt.subplots()

    def autolabel(rects):
        """Attach a text label above each bar in *rects*, displaying its height."""
        for rect in rects:
            width = rect.get_width()
            if width == 0:
                continue
            ax.annotate('{:.1f}'.format(width/1e9),
                        xy=(width, rect.get_y() + rect.get_height() / 2),
                        xytext=(3, 0),
                        textcoords="offset points",
                        ha='left', va='center',
                        fontsize=12 - len(rects))

    durations = list(map(list, zip(*durations)))
    # pprint(durations)

    basenames_without_ext = []
    rects = []
    ind = np.arange(len(labels))
    for i in range(num_of_dbs):
        basename_without_ext = os.path.splitext(os.path.basename(db_filenames[i]))[0]
        basenames_without_ext.append(basename_without_ext)
        y = ind+(-(num_of_dbs-1)/2.0+i)*height
        r = ax.barh(y, durations[i], height -0.02, label=basename_without_ext)
        rects.append(r)
        autolabel(r)
    plt.yticks(x, labels)
    ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left', borderaxespad=0)
    # plt.yticks([1e8, 1e8 * 5, 1e9, 1e9 * 5])
    plt.xticks([])
    plt.xlabel('Time(sec)')

    x1,x2,y1,y2 = plt.axis()
    plt.axis((x1,x2*1.1,y1,y2))
    plt.gca().invert_yaxis()

    plt.tight_layout()
    plt.show()
    # plt.savefig(" and ".join(basenames_without_ext) + ".svg")

if __name__ == "__main__":
    main()

