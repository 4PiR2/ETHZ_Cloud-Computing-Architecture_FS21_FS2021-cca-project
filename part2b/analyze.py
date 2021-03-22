import re
import numpy as np
import matplotlib.pyplot as plt

path_log = 'logs/'

benchmarks = ['blackscholes', 'canneal' ,'dedup', 'ferret', 'fft', 'freqmine']
n_threads = [1, 2, 4, 8]
reps = 3

p = re.compile(r'real\s+([0-9]*)m([0-9]*\.[0-9]*)s')

result = np.zeros((len(benchmarks), len(n_threads), reps))

for i in range(len(benchmarks)):
	for i_threads in range(len(n_threads)):
		for rep in range(reps):
			with open(path_log+benchmarks[i]+'_'+str(n_threads[i_threads])+'_'+str(rep)+'.txt', 'r') as f:
				for line in f:
					m=p.match(line)
					if m:
						t = int(m.group(1)) * 60 + float(m.group(2))
						result[i, i_threads, rep] = t
						break

result_mean = np.mean(result, axis=-1)
result_base = result_mean[:,[0]*len(n_threads)]
result_speedup = result_base / result_mean
result_std = np.std(result, ddof=1 ,axis=-1)
result_std /= result_base

for i in range(len(benchmarks)):
	plt.plot(n_threads, result_speedup[i], label=benchmarks[i])
plt.xticks(n_threads)
plt.yticks(range(6))
plt.xlim(0, 9)
plt.ylim(0, 5)
plt.gca().set_aspect("equal")
plt.xlabel('# Threads')
plt.ylabel('Speedup')
plt.title('PARSEC Parallel Behavior')
plt.grid()
plt.legend()
plt.savefig('plot.png', dpi=300)
plt.show()
