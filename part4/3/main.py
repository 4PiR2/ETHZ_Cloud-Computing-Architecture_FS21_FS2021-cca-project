import os
import re
import sys
import time
import docker
import psutil
import numpy as np

logfile_dir = sys.argv[1] + '/'
logfile_operation = open(logfile_dir + 'operation.txt', 'w')
logfile_cpu = open(logfile_dir + 'cpu.txt', 'w')
logfile_mc = open(logfile_dir + 'mc.txt', 'w')

job_names = ['blackscholes', 'canneal', 'dedup', 'ferret', 'splash2x-fft', 'freqmine']

client = docker.from_env()


def log_cpu():
	p = psutil.cpu_percent(percpu=True)
	logfile_cpu.write(str(time.time()) + '\t' + '\t'.join([str(x) for x in p]) + '\n')
	logfile_cpu.flush()
	return p


def pull_images():
	for job_name in job_names:
		print('pulling', job_name)
		client.images.pull('anakli/parsec:' + job_name + '-native-reduced')


def remove_all():
	for container in client.containers.list(all=True):
		if container.name.startswith('parsec-'):
			container.remove(force=True)


class Job:
	def __init__(self, i):
		self.name = job_names[i]
		self.container = None

	def log_operation(self, *args):
		line = str(time.time()) + '\t' + self.name.split('-')[-1] + '\t' + '\t'.join([str(arg) for arg in args])
		print(line)
		logfile_operation.write(line + '\n')
		logfile_operation.flush()

	# docker run --cpuset-cpus="0" -d --rm --name parsec anakli/parsec:blackscholes-native-reduced ./bin/parsecmgmt -a run -p blackscholes -i native -n 2
	# container = client.containers.run(
	# 	'anakli/parsec:blackscholes-native-reduced',
	# 	'./bin/parsecmgmt -a run -p blackscholes -i native -n 2',
	# 	cpuset_cpus='0', detach=True, remove=True, name='parsec')
	def start(self, cpus, t):
		if 'fft' in self.name:
			t = 2 ** int(np.log2(t))
		cpus_str = ','.join([str(cpu) for cpu in cpus])
		self.container = client.containers.run(
			'anakli/parsec:' + self.name + '-native-reduced',
			'./bin/parsecmgmt -a run -p ' + self.name.replace('-', '.') + ' -i native -n ' + str(t),
			# mem_limit='6m', memswap_limit='6m',
			cpuset_cpus=cpus_str, detach=True, name='parsec-' + self.name)
		self.log_operation('start', cpus_str, t)

	def status(self):
		# restarting, running, paused, exited
		try:
			self.container.reload()
		except docker.errors.NotFound:
			return None
		return self.container.status

	def update(self, cpu_set):
		cpus_str = ','.join([str(cpu) for cpu in cpu_set])
		try:
			self.container.update(cpuset_cpus=cpus_str)
			self.log_operation('update', cpus_str)
		except:
			pass

	def pause(self):
		if self.status() == 'running':
			try:
				self.container.pause()
				self.log_operation('pause')
			except:
				pass

	def resume(self):
		if self.status() == 'paused':
			self.container.unpause()
			self.log_operation('resume')

	def remove(self):
		self.container.remove(force=True)
		self.log_operation('remove')

	def log(self):
		try:
			self.container.reload()
		except docker.errors.NotFound:
			return None
		l = self.container.logs().decode()
		with open(logfile_dir + self.name.split('-')[-1] + '.txt', 'w') as ff:
			ff.write(l)
		p = re.compile(r'real\s+([0-9]+)m([0-9]+\.[0-9]+)s')
		m = p.search(l)
		if m:
			t = int(m.group(1)) * 60 + float(m.group(2))
			return t
		return None


class Queue:
	def __init__(self, cpu_set, job_list, with_mc=False, t=None):
		self.cpu_set = cpu_set
		self.jobs = [Job(i) for i in job_list]
		self.with_mc = with_mc
		self.t = t
		self.index = 0
		self.need_init = self.index < len(self.jobs)

	def tick(self):
		if self.index >= len(self.jobs):
			return True
		t = self.t
		if t is None:
			t = len(self.cpu_set)
		if self.need_init:
			self.jobs[self.index].start(self.cpu_set, t)
			self.need_init = False
		if self.jobs[self.index].status() == 'exited':
			tt = self.jobs[self.index].log()
			self.jobs[self.index].remove()
			if tt is None:
				self.jobs[self.index].log_operation('fail')
				self.index = len(self.jobs)
			self.index += 1
			if self.index < len(self.jobs):
				self.jobs[self.index].start(self.cpu_set, t)
			else:
				return True
		return False

	def pause(self):
		if self.need_init:
			self.tick()
		if self.index < len(self.jobs):
			self.jobs[self.index].pause()

	def resume(self):
		if self.need_init:
			self.tick()
		if self.index < len(self.jobs):
			self.jobs[self.index].resume()

	def update(self, cpu_set, with_mc=False):
		self.cpu_set = cpu_set
		self.with_mc = with_mc
		if not self.need_init and self.index < len(self.jobs):
			self.jobs[self.index].update(cpu_set)

	def add_job(self, job_list):
		self.need_init = self.index == len(self.jobs)
		self.jobs.extend([Job(i) for i in job_list])
		if self.need_init:
			self.tick()


class Mc:
	def __init__(self, cpu_set):
		pid_path = '/var/run/memcached/memcached.pid'
		# pid_path = 'test.pid'
		with open(pid_path, 'r') as f:
			self.pid = f.readline().strip()
		self.cpu_set = cpu_set
		self.mode = 2
		self.update(self.cpu_set)

	def mode2(self):
		if self.mode != 2:
			self.mode = 2
			self.update(self.cpu_set)

	def mode1(self):
		if self.mode != 1:
			self.mode = 1
			self.update(self.cpu_set)

	def update(self, cpu_set):
		self.cpu_set = cpu_set
		cpus_str = str(self.cpu_set[0])
		if self.mode == 2:
			cpus_str += ',' + str(self.cpu_set[1])
		os.system('taskset -acp ' + cpus_str + ' ' + self.pid + ' >/dev/null')
		logfile_mc.write(str(time.time()) + '\t' + cpus_str + '\n')
		logfile_mc.flush()


if '-p' in sys.argv:
	pull_images()
	input('press any key to continue')

remove_all()

if '-r' in sys.argv:
	input('removed, press any key to continue')

"""
q0 = Queue([2], [], True)
q1 = Queue([0], [5, 1])
q2 = Queue([1], [3])
dynamic = [0, 4, 2]
mc = Mc([3, 2])

f0 = False
f1 = False
f2 = False
while True:
	time.sleep(1)
	p = log_cpu()
	cpu_rate = np.sum(np.array(p)[mc.cpu_set[:mc.mode]])
	if q0.with_mc:
		if f0 or cpu_rate > 90:
			mc.mode2()
			q0.pause()
		elif cpu_rate < 90:
			mc.mode1()
			q0.resume()
	f0 = q0.tick()
	f1 = q1.tick()
	f2 = q2.tick()
	if dynamic and f1:
		q1.add_job([dynamic.pop(0)])
		f1 = q1.tick()
	if dynamic and f2:
		q2.add_job([dynamic.pop(0)])
		f2 = q2.tick()
	if dynamic and f0:
		q0.add_job([dynamic.pop(0)])
		f0 = q0.tick()
	if f1 and f2 and not f0 and q0.cpu_set != [0, 1]:
		q0.update([0, 1])
		q0.resume()
	if f1 and not f0 and q0.cpu_set != [0]:
		q0.update([0])
		q0.resume()
	if f2 and not f0 and q0.cpu_set != [1]:
		q0.update([1])
		q0.resume()
	if f2 and not f1 and q1.cpu_set != [0, 1]:
		q1.update([0, 1])
	if f1 and not f2 and q2.cpu_set != [0, 1]:
		q2.update([0, 1])
	if f0 and f1 and f2:
		break
"""

"""
q0 = Queue([2], [], True)
q1 = Queue([0, 1], [5, 1])
q2 = Queue([0, 1], [3])
dynamic = [0, 4, 2]
mc = Mc([3, 2])

f0 = False
f1 = False
f2 = False
while True:
	time.sleep(1)
	p = log_cpu()
	cpu_rate = np.sum(np.array(p)[mc.cpu_set[:mc.mode]])
	if q0.with_mc:
		if f0 or cpu_rate > 90:
			mc.mode2()
			q0.pause()
		elif cpu_rate < 90:
			mc.mode1()
			q0.resume()
	f0 = q0.tick()
	f1 = q1.tick()
	f2 = q2.tick()
	if dynamic and f1:
		q1.add_job([dynamic.pop(0)])
		f1 = q1.tick()
	if dynamic and f2:
		q2.add_job([dynamic.pop(0)])
		f2 = q2.tick()
	if dynamic and f0:
		q0.add_job([dynamic.pop(0)])
		f0 = q0.tick()
	if f1 and not f0 and q0.cpu_set != [0, 1]:
		q0.update([0, 1])
		q0.resume()
	if f2 and not f0 and q0.cpu_set != [0, 1]:
		q0.update([0, 1])
		q0.resume()
	if f0 and f1 and f2:
		break
"""

"""
q0 = Queue([2], [], True)
q1 = Queue([0, 1], [3, 5, 1])
dynamic = [0, 4, 2]
mc = Mc([3, 2])

f0 = False
f1 = False
while True:
	time.sleep(1)
	p = log_cpu()
	cpu_rate = np.sum(np.array(p)[mc.cpu_set[:mc.mode]])
	if q0.with_mc:
		if f0 or cpu_rate > 90:
			mc.mode2()
			q0.pause()
		elif cpu_rate < 90:
			mc.mode1()
			q0.resume()
	f0 = q0.tick()
	f1 = q1.tick()
	if dynamic and f1:
		q1.add_job([dynamic.pop(0)])
		f1 = q1.tick()
	if dynamic and f0:
		q0.add_job([dynamic.pop(0)])
		f0 = q0.tick()
	if f1 and not f0 and q0.cpu_set != [0, 1]:
		q0.update([0, 1])
		q0.resume()
	if f0 and f1:
		break
"""

"""
q1 = Queue([0, 1], range(6))

f1 = False
while True:
	time.sleep(1)
	p = log_cpu()
	f1 = q1.tick()
	if f1:
		break
"""

q0 = Queue([0, 1], range(6), t=3)
mc = Mc([3, 2])

f0 = False
while True:
	time.sleep(1)
	p = log_cpu()
	cpu_rate = np.sum(np.array(p)[mc.cpu_set[:mc.mode]])
	if cpu_rate > 90:
		mc.mode2()
		if q0.cpu_set != [0, 1]:
			q0.update([0, 1])
	elif cpu_rate < 90:
		mc.mode1()
		if q0.cpu_set != [0, 1, 2]:
			q0.update([0, 1, 2])
	f0 = q0.tick()
	if f0:
		break
