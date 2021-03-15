import matplotlib.pyplot as plt
from statistics import mean

def load_data(filename):
    data = {}
    for i in range(5000, 60000, 5000):
        data[i] = []
    with open(filename, 'r') as fi:
        for line in fi.readlines():
            line = line.strip()
            if not line.startswith("read"):
                continue
            line = [x for x in line.split(" ") if x]
            data[int(line[-1])].append(float(line[-6]))
    result = []
    for i in range(5000, 60000, 5000):
        result.append(mean(data[i]) / 1000)
    return result

if __name__ == '__main__':
    data_no = load_data('no')
    data_cpu = load_data('cpu')
    data_l1d = load_data('l1d')
    data_l1i = load_data('l1i')
    data_l2 = load_data('l2')
    data_llc = load_data('llc')
    data_membw = load_data('membw')
    data_x = [i for i in range(5, 60, 5)]

    plt.style.use('seaborn-darkgrid')
    plt.figure(figsize=(9.6, 7.2))
    line_no, = plt.plot(data_x, data_no, marker='.', color='black', linewidth=1.5, alpha=0.7, label='no interference')
    line_cpu, = plt.plot(data_x, data_cpu, marker='^', color='darkblue', linewidth=1.5, alpha=0.7, label='cpu')
    line_l1d, = plt.plot(data_x, data_l1d, marker='s', color='darkred', linewidth=1.5, alpha=0.7, label='l1d')
    line_l1i, = plt.plot(data_x, data_l1i, marker='8', color='darkgreen', linewidth=1.5, alpha=0.7, label='l1i')
    line_l2, = plt.plot(data_x, data_l2, marker='<', color='darkorange', linewidth=1.5, alpha=0.7, label='l2')
    line_llc, = plt.plot(data_x, data_llc, marker='>', color='navy', linewidth=1.5, alpha=0.7, label='llc')
    line_membw, = plt.plot(data_x, data_membw, marker='p', color='magenta', linewidth=1.5, alpha=0.7, label='membw')
    # plt.axvline(x=700, linewidth=2, color='orange')
    # plt.text(750, 3.7, 'L3 Cache', color='orange', fontsize='x-large')
    plt.legend(handles=[line_no, line_cpu, line_l1d, line_l1i, line_l2, line_llc, line_membw], fontsize='x-large')
    plt.title("95th Percentile Latency", loc='center', fontsize=16, fontweight=1, color='black')
    plt.xlabel("QPS [k]", fontsize=16)
    plt.ylabel("Latency [ms]", fontsize=16)
    plt.xticks(fontsize=14)
    plt.yticks(fontsize=14)
    plt.savefig('p95.png')
