import matplotlib.pyplot as plt
from statistics import mean, stdev

import numpy as np


def load_data(filename_l, filename_u):
    u_data = []
    with open(filename_u, 'r') as fi:
        for line in fi.readlines():
            line = [float(x) for x in line.strip().split(' ')]
            u_data.append(line)

    data_x = {}
    data_y = {}
    data_z = {}
    for i in range(5000, 105000, 5000):
        data_x[i] = []
        data_y[i] = []
        data_z[i] = []
    with open(filename_l, 'r') as fi:
        for line in fi.readlines():
            line = line.strip()
            if not line.startswith("read"):
                continue
            line = [x for x in line.split(" ") if x]
            data_x[int(line[-3])].append(float(line[-4]))
            data_y[int(line[-3])].append(float(line[-8]))
            for u1, u2, ts in u_data:
                if int(line[-2]) <= ts * 1000 <=  int(line[-1]):
                    data_z[int(line[-3])].append(u1 + u2)
    x = []
    y = []
    z = []
    for i in sorted(data_x.keys()):
        x.append(mean(data_x[i]) / 1000)
        y.append(mean(data_y[i]) / 1000)
        z.append(mean(data_z[i]))
    return x, y, z
    
if __name__ == '__main__':
    x, y, z = load_data('c2_latency', 'c2_utilization')

    plt.style.use('seaborn-darkgrid')
    plt.figure(figsize=(9.6, 7.2))

    fig, ax1 = plt.subplots()
    ax1.set_xlabel("QPS [K]")
    ax1.set_ylabel("Latency [ms]")
    line1, = ax1.plot(x, y, color='darkred', marker='.', label='P95 Latency', alpha=0.7)
    ax1.axhline(2, color='black', linestyle='--')
    ax1.tick_params(axis='y')
    ax1.text(3, 1.93, 'SLO')
    ax1.set_yticks(np.arange(0, 2.1, 0.2))
    ax1.set_xlim(0, 110)
    ax1.set_ylim(0, 2.1)

    ax2 = ax1.twinx() 
    ax2.set_ylabel('CPU Utilization [%]')
    line2, = ax2.plot(x, z, color='darkblue', marker='^', label='CPU Utilization', alpha=0.7)
    ax2.tick_params(axis='y')
    ax2.set_yticks([i for i in range(0, 210, 20)])
    ax2.set_ylim(0, 210)

    plt.title("2-Core Memcached Server Performance", loc='center', color='black')
    plt.legend(handles=[line1, line2], bbox_to_anchor=(0, 0, 1, 0.95))
    fig.tight_layout()
    plt.savefig('c2.pdf')
