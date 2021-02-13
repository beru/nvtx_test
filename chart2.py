#!/usr/bin/python

import sys
import os
import sqlite3
from matplotlib import pyplot as plt
import numpy as np

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
    i = 0
    for j in range(num_of_dbs):
        durations.append([])
    for row in c.execute(sql):
        #print(row)
        labels.append(row[0])
        lst = []
        for j in range(num_of_dbs):
            durations[j].append(row[1+j])
        i += 1
    conn.close()
    x = np.arange(len(labels))
    width = 1.5 / (num_of_dbs * len(labels))
    fig, ax = plt.subplots()

    def autolabel(rects):
        """Attach a text label above each bar in *rects*, displaying its height."""
        for rect in rects:
            height = rect.get_height()
            ax.annotate('{:.1f}'.format(height/1e9),
                        xy=(rect.get_x() + rect.get_width() / 2, height),
                        xytext=(0, 3),  # 3 points vertical offset
                        textcoords="offset points",
                        ha='center', va='bottom')


    for i in range(num_of_dbs):
        autolabel(ax.bar(-(num_of_dbs*width)/2 + width/2 + x + width*i, durations[i], width * 0.95, label=os.path.splitext(db_filenames[i])[0]))
    plt.xticks(x, labels, rotation=60, rotation_mode="anchor", horizontalalignment="right", verticalalignment="center")
    ax.legend(bbox_to_anchor=(1.1, 1.05))
    # plt.yticks([1e8, 1e8 * 5, 1e9, 1e9 * 5])
    plt.yticks([])
    plt.ylabel('time(sec)')

    x1,x2,y1,y2 = plt.axis()
    plt.axis((x1,x2,y1,y2*1.05))

    plt.tight_layout()
    plt.show()
    # plt.savefig(os.path.splitext(db_filenames[0])[0] + ".svg")

if __name__ == "__main__":
    main()

