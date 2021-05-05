import matplotlib.pyplot as plt
from statistics import mean, stdev

def load_data(filename):
     data = []
     with open(filename, 'r') as fi:
         for line in fi.readlines():
             line = line.strip()
             if not line.startswith("read"):
                 continue
             line = [x for x in line.split(" ") if x]
             data.append(float(line[-6])/1000)
     return data

if __name__ == '__main__':
    data_m4 = load_data('m6.txt')
    data_x = [i for i in range(0, 300, 20)]

    plt.style.use('seaborn-darkgrid')
    plt.figure(figsize=(9.6, 7.2))
    plt.plot(data_x, data_m4, marker='.', color='black', linewidth=1.5, alpha=0.7)
    plt.title("memcached Server 95th Percentile Latency of Run 3", loc='center', fontsize=16, fontweight=1, color='black')
    plt.xlabel("time [s]", fontsize=16)
    plt.ylabel("Latency [ms]", fontsize=16)
    plt.xticks([0, 40, 80, 120, 160, 200, 240, 280], fontsize=14)
    plt.yticks([0.3, 0.35, 0.4, 0.45, 0.5], fontsize=14)
    plt.legend(fontsize='x-large')
    plt.savefig('m6.pdf')


