import matplotlib.pyplot as plt
from statistics import mean, stdev

def load_data(filename):
    data_x = {}
    data_y = {}
    for i in range(5000, 60000, 5000):
        data_x[i] = []
        data_y[i] = []
    with open(filename, 'r') as fi:
        for line in fi.readlines():
            line = line.strip()
            if not line.startswith("read"):
                continue
            line = [x for x in line.split(" ") if x]
            data_x[int(line[-1])].append(float(line[-2]))
            data_y[int(line[-1])].append(float(line[-6]))
    x = []
    x_std = []
    y = []
    y_std = []
    
    # merge data
    if filename == 'l2':
        for i in [55000]:
            data_x[50000].extend(data_x[i])
            data_y[50000].extend(data_y[i])
            del data_x[i]
            del data_y[i]
    if filename == 'l1d':
        for i in [55000]:
            data_x[50000].extend(data_x[i])
            data_y[50000].extend(data_y[i])
            del data_x[i]
            del data_y[i]
    if filename == 'membw':
        for i in [55000]:
            data_x[50000].extend(data_x[i])
            data_y[50000].extend(data_y[i])
            del data_x[i]
            del data_y[i]
    if filename == 'llc':
        for i in [55000, 50000, 45000, 40000]:
            data_x[35000].extend(data_x[i])
            data_y[35000].extend(data_y[i])
            del data_x[i]
            del data_y[i]
    if filename == 'l1i':
        for i in [55000, 50000, 45000, 40000, 35000, 30000]:
            data_x[25000].extend(data_x[i])
            data_y[25000].extend(data_y[i])
            del data_x[i]
            del data_y[i]
    if filename == 'cpu':
        for i in [55000, 50000, 45000, 40000, 35000, 30000]:
            data_x[25000].extend(data_x[i])
            data_y[25000].extend(data_y[i])
            del data_x[i]
            del data_y[i]


    for i in sorted(data_x.keys()):
        x.append(mean(data_x[i]) / 1000)
        x_std.append(stdev(data_x[i]) / 1000)
        y.append(mean(data_y[i]) / 1000)
        y_std.append(stdev(data_y[i]) / 1000)
    return (x, x_std, y, y_std)

if __name__ == '__main__':
    data_no = load_data('no')
    data_cpu = load_data('cpu')
    data_l1d = load_data('l1d')
    data_l1i = load_data('l1i')
    data_l2 = load_data('l2')
    data_llc = load_data('llc')
    data_membw = load_data('membw')

    plt.style.use('seaborn-darkgrid')
    plt.figure(figsize=(9.6, 7.2))
    plt.errorbar(data_no[0], data_no[2], xerr=data_no[1], yerr=data_no[3], marker='.', color='black', linewidth=1.5, alpha=0.7, label='no interference')
    plt.errorbar(data_cpu[0], data_cpu[2], xerr=data_cpu[1], yerr=data_cpu[3], marker='^', color='darkblue', linewidth=1.5, alpha=0.7, label='cpu')
    plt.errorbar(data_l1d[0], data_l1d[2], xerr=data_l1d[1], yerr=data_l1d[3], marker='s', color='darkred', linewidth=1.5, alpha=0.7, label='l1d')
    plt.errorbar(data_l1i[0], data_l1i[2], xerr=data_l1i[1], yerr=data_l1i[3], marker='8', color='darkgreen', linewidth=1.5, alpha=0.7, label='l1i')
    plt.errorbar(data_l2[0], data_l2[2], xerr=data_l2[1], yerr=data_l2[3], marker='<', color='darkorange', linewidth=1.5, alpha=0.7, label='l2')
    plt.errorbar(data_llc[0], data_llc[2], xerr=data_llc[1], yerr=data_llc[3], marker='>', color='grey', linewidth=1.5, alpha=0.7, label='llc')
    plt.errorbar(data_membw[0], data_membw[2], xerr=data_membw[1], yerr=data_membw[3], marker='p', color='magenta', linewidth=1.5, alpha=0.7, label='membw')
    plt.title("95th Percentile Latency", loc='center', fontsize=16, fontweight=1, color='black')
    plt.xlabel("QPS [k]", fontsize=16)
    plt.ylabel("Latency [ms]", fontsize=16)
    plt.xticks([0, 10, 20, 30, 40, 50, 60], fontsize=14)
    plt.yticks([0, 2, 4, 6, 8, 10], fontsize=14)
    plt.legend(fontsize='x-large')
    plt.savefig('p95.pdf')
