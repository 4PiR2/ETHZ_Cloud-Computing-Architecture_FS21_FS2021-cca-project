import os
import subprocess
import time

path_src = 'part2b/'
path_dst = 'configs/'
path_log = 'logs/'

benchmarks = ['blackscholes', 'canneal' ,'dedup', 'ferret', 'fft', 'freqmine']
jobs = ['blackscholes', 'canneal' ,'dedup', 'ferret', 'splash2x-fft', 'freqmine']

for i in range(len(benchmarks)):
	for n_threads in [1, 2, 4, 8]:
		with open(path_src+'parsec-'+benchmarks[i]+'.yaml', 'r') as fin:
			with open(path_dst+'parsec-'+benchmarks[i]+'_'+str(n_threads)+'.yaml', 'w') as fout:
				for line in fin:
					fout.write(line.replace('N_THREADS', str(n_threads)))

def issue(cmd):
	print(cmd)
	p = subprocess.Popen(cmd.split(), stdout=subprocess.PIPE, universal_newlines=True)
	out = ''.join(p.stdout.readlines())
	print(out)
	return out

for i in range(len(benchmarks)):
	for n_threads in [1, 2, 4, 8]:
		for rep in range(3):
			print('\n### '+benchmarks[i]+' '+str(n_threads)+' '+str(rep)+' ###\n')
			issue('kubectl create -f '+path_dst+'parsec-'+benchmarks[i]+'_'+str(n_threads)+'.yaml')
			while True:
				out = issue('kubectl get jobs')
				if '1/1' in out:
					break
				time.sleep(10)
			os.system("kubectl logs $(kubectl get pods --selector=job-name="+"parsec-"+jobs[i]+" --output=jsonpath='{.items[*].metadata.name}') > "
			      +path_log+benchmarks[i]+'_'+str(n_threads)+'_'+str(rep)+'.txt')
			with open(path_log+benchmarks[i]+'_'+str(n_threads)+'_'+str(rep)+'.txt', 'r') as f:
				print(''.join(f.readlines()))
			issue('kubectl delete jobs --all')
			time.sleep(1)
			issue('kubectl delete pods --all')
			time.sleep(1)
