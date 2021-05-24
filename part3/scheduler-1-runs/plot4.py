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
    data_m4 = load_data('m4.txt')
    data_x = [i for i in range(0, 280, 20)]

    plt.style.use('seaborn-darkgrid')
    plt.figure(figsize=(9.6, 7.2))
    plt.plot(data_x, data_m4, marker='.', color='black', linewidth=1.5, alpha=0.7)
    plt.title("Memcached Server 95th Percentile Latency of Run 1", loc='center', fontsize=16, fontweight=1, color='black')
    plt.xlabel("Time [s]", fontsize=16)
    plt.ylabel("Latency [ms]", fontsize=16)
    plt.xticks([0, 40, 80, 120, 160, 200, 240, 280], fontsize=14)
    plt.yticks([0, 0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4, 0.45, 0.5], fontsize=14)
    plt.xlim(0)
    plt.ylim(0)
    # plt.legend(fontsize='x-large')

    plt.axvline(x=0, linewidth=2, color='orange')
    plt.text(2, 0.2, 'dedup\nferret\nfreqmine\ncanneal\nfft', color='orange', fontsize='x-large')
    plt.axvline(x=55, linewidth=2, color='orange')
    plt.text(57, 0.2, 'blackholes', color='orange', fontsize='x-large')

    plt.savefig('m4.pdf')


