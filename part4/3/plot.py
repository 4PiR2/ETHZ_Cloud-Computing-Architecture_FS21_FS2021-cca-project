import numpy as np
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec

log_prefix = 'log-2'
plot_dir = 'plot2/'

id2job = ['blackscholes', 'canneal', 'dedup', 'ferret', 'fft', 'freqmine']
job2id = {}
for id in range(len(id2job)):
	job2id[id2job[id]] = id
colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf']

run_time = np.zeros((7, 3))
slo_vio_rate = np.zeros(3)
qps_diff_rate = np.zeros(3)


def to_step(y, s, e=None):
	n = len(y)
	if e is not None:
		X = np.zeros(2 * n)
		Y = np.zeros(2 * n)
		for i in range(n):
			X[2 * i] = s[i]
			X[2 * i + 1] = e[i]
			Y[2 * i] = Y[2 * i + 1] = y[i]
	else:
		X = np.zeros(2 * n - 1)
		Y = np.zeros(2 * n - 1)
		for i in range(n):
			if i == 0:
				X[0] = s[0]
			else:
				X[2 * i - 1] = X[2 * i] = s[i]
			if i == n - 1:
				Y[2 * i] = y[i]
			else:
				Y[2 * i] = Y[2 * i + 1] = y[i]
	return X, Y


for run_id in range(3):
	logfile_dir = log_prefix + ['a', 'b', 'c'][run_id] + '/'

	mcperf_numbers = []
	mcperf_ts_start = 0
	mcperf_ts_end = 0
	with open(logfile_dir + 'mcperf.txt', 'r') as f:
		for line in f:
			if line.startswith('read'):
				mcperf_numbers.append([float(i) for i in line.split()[1:]])
			elif line.startswith('Timestamp start:'):
				mcperf_ts_start = int(line.split()[-1]) / 1e3
			elif line.startswith('Timestamp end:'):
				mcperf_ts_end = int(line.split()[-1]) / 1e3
	mcperf_numbers = np.array(mcperf_numbers)
	mcperf_n_interval = len(mcperf_numbers)
	mcperf_t_interval = (mcperf_ts_end - mcperf_ts_start) / mcperf_n_interval
	mcperf_s = np.array([mcperf_ts_start + i * mcperf_t_interval for i in range(mcperf_n_interval)])
	mcperf_e = mcperf_s + mcperf_t_interval

	operations = []
	with open(logfile_dir + 'operation.txt', 'r') as f:
		for line in f:
			fields = line.split()
			while len(fields) < 5:
				fields.append('')
			operations.append(fields)
	operations = np.array(operations)
	operation_start = float(operations[0, 0])
	operation_end = float(operations[-1, 0])
	status = np.zeros(6)
	run_intervals = [[], [], [], [], [], []]
	for entry in operations:
		ts, name, op, _, _ = entry
		id = job2id[name]
		if op in ['start', 'resume']:
			status[id] = float(ts)
		elif op in ['remove', 'pause'] and status[id] != 0:
			run_intervals[id].append([status[id], float(ts)])
			status[id] = 0
	for i in range(6):
		for interval in run_intervals[i]:
			run_time[i, run_id] += interval[1] - interval[0]
	run_time[-1, run_id] = operation_end - operation_start

	mask_mcperf = np.logical_and(mcperf_e >= operation_start, mcperf_s <= operation_end)
	mcperf_numbers = mcperf_numbers[mask_mcperf]
	mcperf_s = mcperf_s[mask_mcperf]
	mcperf_e = mcperf_e[mask_mcperf]
	mcperf_p95 = mcperf_numbers[:, -6]
	mcperf_qps = mcperf_numbers[:, -2]
	mcperf_qps_t = mcperf_numbers[:, -1]

	cores_numbers = []
	with open(logfile_dir + 'mc.txt', 'r') as f:
		for line in f:
			fields = line.split()
			fields[0] = float(fields[0])
			fields[1] = len(fields[1].split(','))
			cores_numbers.append(fields)
	cores_numbers = np.array(cores_numbers)

	slo_vio_rate[run_id] = np.sum(mcperf_p95 > 2000) / len(mcperf_p95)
	qps_diff_rate[run_id] = np.max(np.abs(mcperf_qps - mcperf_qps_t) / mcperf_qps_t)

	mcperf_x = (mcperf_s + mcperf_e) / 2
	cores_x, cores_y = to_step(cores_numbers[:, 1], cores_numbers[:, 0])

	# plt.scatter(mcperf_qps, mcperf_p95)
	# plt.show()

	fig = plt.figure(figsize=(18, 6))
	gs = GridSpec(4, 1)
	gs.update(hspace=0)
	ax1 = fig.add_subplot(gs[0:-1, 0])

	line1, = ax1.plot(mcperf_x - operation_start, mcperf_p95 / 1e3, color='darkred', marker='.', label='P95 Latency',
	                  alpha=0.7)
	ax1.axhline(2, color='black', linestyle='--')
	ax1.tick_params(axis='y')
	ax1.set_ylabel('P95 Latency [ms]')
	ax1.set_yticks(np.arange(0, 2.51, 0.5))
	ax1.set_ylim(0, 2.5)
	ax1.text(3, 2.05, 'SLO')
	ax1.set_title(str(run_id + 1) + 'A', loc='center', color='black')

	ax1.set_xlim(0, operation_end - operation_start)
	ax1.set_xticks(np.arange(0, operation_end - operation_start + 1, 100))
	ax1.get_xaxis().set_visible(False)
	ax2 = ax1.twinx()
	ax2.set_ylabel('QPS [K]')
	line2, = ax2.plot(mcperf_x - operation_start, mcperf_qps / 1e3, color='darkblue', marker='^', label='QPS',
	                  alpha=0.7)
	ax2.tick_params(axis='y')
	ax2.set_yticks(np.arange(0, 125.1, 25))
	ax2.set_ylim(0, 125)
	ax2.legend(handles=[line1, line2])

	ax3 = fig.add_subplot(gs[-1, 0], sharex=ax1)
	for i in range(6):
		for interval in run_intervals[i]:
			ax3.barh(i, width=interval[1] - interval[0], left=interval[0] - operation_start, color=colors[i])
	ax3.set_yticks(range(6))
	ax3.set_yticklabels(id2job)
	ax3.set_xlabel('Time [s]')

	plt.tight_layout()
	plt.savefig(plot_dir + str(run_id + 1) + 'A' + '.pdf')
	plt.savefig(plot_dir + str(run_id + 1) + 'A' + '.png')

	fig = plt.figure(figsize=(18, 6))
	gs = GridSpec(4, 1)
	gs.update(hspace=0)
	ax1 = fig.add_subplot(gs[0:-1, 0])

	line1, = ax1.plot(cores_x - operation_start, cores_y, color='darkred', marker='.', label='# CPU Cores', alpha=0.7)
	ax1.tick_params(axis='y')
	ax1.set_ylabel('# CPU Cores')
	ax1.set_yticks(np.arange(0, 2.1, 1))
	ax1.set_ylim(0, 2.5)
	ax1.set_title(str(run_id + 1) + 'B', loc='center', color='black')

	ax1.set_xlim(0, operation_end - operation_start)
	ax1.set_xticks(np.arange(0, operation_end - operation_start + 1, 100))
	ax1.get_xaxis().set_visible(False)
	ax2 = ax1.twinx()
	ax2.set_ylabel('QPS [K]')
	line2, = ax2.plot(mcperf_x - operation_start, mcperf_qps / 1e3, color='darkblue', marker='^', label='QPS',
	                  alpha=0.7)
	ax2.tick_params(axis='y')
	ax2.set_yticks(np.arange(0, 125.1, 25))
	ax2.set_ylim(0, 125)
	ax2.legend(handles=[line1, line2])

	ax3 = fig.add_subplot(gs[-1, 0], sharex=ax1)
	for i in range(6):
		for interval in run_intervals[i]:
			ax3.barh(i, width=interval[1] - interval[0], left=interval[0] - operation_start, color=colors[i])
	ax3.set_yticks(range(6))
	ax3.set_yticklabels(id2job)
	ax3.set_xlabel('Time [s]')

	plt.tight_layout()
	plt.savefig(plot_dir + str(run_id + 1) + 'B' + '.pdf')
	plt.savefig(plot_dir + str(run_id + 1) + 'B' + '.png')

run_time_mean = np.mean(run_time, axis=-1)
run_time_std = np.std(run_time, axis=-1, ddof=1)
with open(plot_dir + 'data.txt', 'w') as f:
	f.write(str(run_time_mean) + '\n')
	f.write(str(run_time_std) + '\n')
	f.write(str(slo_vio_rate) + '\n')
	f.write(str([np.mean(slo_vio_rate), np.std(slo_vio_rate, ddof=1)]) + '\n')
