import re
import numpy as np
import matplotlib.pyplot as plt

path_log = 'logs/'

benchmarks = ['blackscholes', 'canneal' ,'dedup', 'ferret', 'fft', 'freqmine']
n_threads = [1, 2, 4, 8]
reps = 3

p = re.compile(r'^real\s+([0-9]+)m([0-9]+\.[0-9]+)s$')
pferret = re.compile(r'^QUERY TIME: ([0-9]+\.[0-9]+) seconds$')
pfft = re.compile(r'^Total time without initialization :\s+([0-9]+)$')
pfreqmine = re.compile(r', the FPgrowth cost ([0-9]+\.[0-9]+) seconds$')

result = np.zeros((len(benchmarks), len(n_threads), reps))

for i in range(len(benchmarks)):
	for i_threads in range(len(n_threads)):
		for rep in range(reps):
			with open(path_log+benchmarks[i]+'_'+str(n_threads[i_threads])+'_'+str(rep)+'.txt', 'r') as f:
				for line in f:
					if i == 3:
						m = pferret.match(line)
						if m:
							t = float(m.group(1))
							result[i,i_threads,rep] = t
							break
					elif i == 4:
						m = pfft.match(line)
						if m:
							t = int(m.group(1)) / 1e6
							result[i,i_threads,rep] = t
							break
					elif i == 5:
						m = pfreqmine.search(line)
						if m:
							t = float(m.group(1))
							result[i,i_threads,rep] = t
							break
					else:
						m=p.match(line)
						if m:
							t = int(m.group(1)) * 60 + float(m.group(2))
							result[i,i_threads,rep] = t
							break

result_mean = np.mean(result, axis=-1)
result_base = result_mean[:,[0]*len(n_threads)]
result_speedup = result_base / result_mean
result_std = np.std(result, ddof=1 ,axis=-1)
result_err = result_std * result_base / result_mean**2

ylim = 6
plt.plot([0, ylim], [0, ylim], color='#b0b0b0', linewidth=1, linestyle='--')
for i in np.argsort(result_speedup[:,2])[::-1]:
	plt.errorbar(n_threads, result_speedup[i], yerr=result_err[i], label=benchmarks[i], marker='.', capsize=2)
plt.xticks(n_threads)
plt.yticks(range(ylim + 1))
plt.xlim(0, 9)
plt.ylim(0, ylim)
plt.gca().set_aspect("equal")
plt.xlabel('# Threads')
plt.ylabel('Speedup')
plt.title('PARSEC Parallel Behavior')
plt.grid(linestyle='--')
plt.legend()
plt.savefig('plot.pdf', bbox_inches='tight', pad_inches=0.1)
plt.show()
