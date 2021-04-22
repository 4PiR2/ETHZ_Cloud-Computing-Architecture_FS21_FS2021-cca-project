import matplotlib.pyplot as plt
from statistics import mean, stdev

def load_data(filename):
    data_x = {}
    data_y = {}
    for i in range(5000, 125000, 5000):
        data_x[i] = []
        data_y[i] = []
    with open(filename, 'r') as fi:
        for line in fi.readlines():
            line = line.strip()
            if not line.startswith("read"):
                continue
            line = [x for x in line.split(" ") if x]
            data_x[int(line[-3])].append(float(line[-4]))
            data_y[int(line[-3])].append(float(line[-8]))
    x = []
    x_std = []
    y = []
    y_std = []
    
    # # merge data
    # if filename == 'l2':
    #     for i in [55000]:
    #         data_x[50000].extend(data_x[i])
    #         data_y[50000].extend(data_y[i])
    #         del data_x[i]
    #         del data_y[i]
    # if filename == 'l1d':
    #     for i in [55000]:
    #         data_x[50000].extend(data_x[i])
    #         data_y[50000].extend(data_y[i])
    #         del data_x[i]
    #         del data_y[i]
    # if filename == 'membw':
    #     for i in [55000]:
    #         data_x[50000].extend(data_x[i])
    #         data_y[50000].extend(data_y[i])
    #         del data_x[i]
    #         del data_y[i]
    # if filename == 'llc':
    #     for i in [55000, 50000, 45000, 40000]:
    #         data_x[35000].extend(data_x[i])
    #         data_y[35000].extend(data_y[i])
    #         del data_x[i]
    #         del data_y[i]
    # if filename == 'l1i':
    #     for i in [55000, 50000, 45000, 40000, 35000, 30000]:
    #         data_x[25000].extend(data_x[i])
    #         data_y[25000].extend(data_y[i])
    #         del data_x[i]
    #         del data_y[i]
    # if filename == 'cpu':
    #     for i in [55000, 50000, 45000, 40000, 35000, 30000]:
    #         data_x[25000].extend(data_x[i])
    #         data_y[25000].extend(data_y[i])
    #         del data_x[i]
    #         del data_y[i]


    for i in sorted(data_x.keys()):
        x.append(mean(data_x[i]) / 1000)
        x_std.append(stdev(data_x[i]) / 1000)
        y.append(mean(data_y[i]) / 1000)
        y_std.append(stdev(data_y[i]) / 1000)
    return (x, x_std, y, y_std)

if __name__ == '__main__':
    t1c1 = load_data('t1c1')
    t1c2 = load_data('t1c2')
    t2c1 = load_data('t2c1')
    t2c2 = load_data('t2c2')

    plt.style.use('seaborn-darkgrid')
    plt.figure(figsize=(9.6, 7.2))
    plt.errorbar(t1c1[0], t1c1[2], xerr=t1c1[1], yerr=t1c1[3], marker='.', color='black', linewidth=1.5, alpha=0.7, label='T=1 C=1')
    plt.errorbar(t1c2[0], t1c2[2], xerr=t1c2[1], yerr=t1c2[3], marker='^', color='darkblue', linewidth=1.5, alpha=0.7, label='T=1 C=2')
    plt.errorbar(t2c1[0], t2c1[2], xerr=t2c1[1], yerr=t2c1[3], marker='s', color='darkred', linewidth=1.5, alpha=0.7, label='T=2 C=1')
    plt.errorbar(t2c2[0], t2c2[2], xerr=t2c2[1], yerr=t2c2[3], marker='8', color='darkgreen', linewidth=1.5, alpha=0.7, label='T=2 C=2')
    # plt.errorbar(data_l2[0], data_l2[2], xerr=data_l2[1], yerr=data_l2[3], marker='<', color='darkorange', linewidth=1.5, alpha=0.7, label='l2')
    # plt.errorbar(data_llc[0], data_llc[2], xerr=data_llc[1], yerr=data_llc[3], marker='>', color='grey', linewidth=1.5, alpha=0.7, label='llc')
    # plt.errorbar(data_membw[0], data_membw[2], xerr=data_membw[1], yerr=data_membw[3], marker='p', color='magenta', linewidth=1.5, alpha=0.7, label='membw')
    plt.title("memcached Server 95th Percentile Latency Averaged over 3 Runs", loc='center', fontsize=16, fontweight=1, color='black')
    plt.xlabel("QPS [k]", fontsize=16)
    plt.ylabel("Latency [ms]", fontsize=16)
    # plt.xticks([0, 10, 20, 30, 40, 50, 60], fontsize=14)
    # plt.yticks([0, 2, 4, 6, 8, 10], fontsize=14)
    plt.legend(fontsize='x-large')
    plt.savefig('p95.pdf')
