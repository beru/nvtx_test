#!/usr/bin/python

import sys
import os
import sqlite3
from matplotlib import pyplot as plt

def main():
    if len(sys.argv) < 2:
        print('usage: sqlite_filename')
        sys.exit()
    db_filename = sys.argv[1]
    conn = sqlite3.connect(db_filename)
    c = conn.cursor()
    # for row in c.execute('SELECT start, end, text FROM NVTX_EVENTS WHERE text IS NOT NULL ORDER BY start'):
    #     print(row)
    labels = []
    durations = []
    for row in c.execute('SELECT text, SUM(end - start) FROM NVTX_EVENTS WHERE text IS NOT NULL GROUP BY text ORDER BY start'):
        labels.append(row[0])
        durations.append(row[1])
    conn.close()

    plt.bar(range(len(durations)), durations, label="NVTX")
    plt.xticks(range(len(durations)), labels, rotation=60, rotation_mode="anchor", horizontalalignment="right", verticalalignment="center")
    plt.yticks([1e8, 1e8 * 5, 1e9, 1e9 * 5])

    for i in range(len(durations)):
        plt.annotate("{:.1f}".format(durations[i]/1e9), xy=(i,durations[i]), ha='center', va='bottom')
    plt.tight_layout()
    plt.show()
#    plt.savefig(os.path.splitext(db_filename)[0] + ".svg")

if __name__ == "__main__":
    main()

