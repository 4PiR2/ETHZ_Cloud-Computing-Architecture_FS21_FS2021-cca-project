import os
import subprocess
import time

path_interf = '../../interference/'
path_bench = './'
path_log = 'logs/'

interference = ['cpu', 'l1d', 'l1i', 'l2', 'llc', 'membw']
benchmarks = ['blackscholes', 'canneal' ,'dedup', 'ferret', 'fft', 'freqmine']
jobs = ['blackscholes', 'canneal' ,'dedup', 'ferret', 'splash2x-fft', 'freqmine']

def issue(cmd):
	print(cmd)
	p = subprocess.Popen(cmd.split(), stdout=subprocess.PIPE, universal_newlines=True)
	out = ''.join(p.stdout.readlines())
	print(out)
	return out

for i in range(len(benchmarks)):
	for j in range(len(interference)):
		for rep in range(3):
			print('\n### '+benchmarks[i]+' '+interference[j]+' '+str(rep)+' ###\n')
			issue('kubectl create -f '+path_interf+'ibench-'+interference[j]+'.yaml')
			time.sleep(10)
			issue('kubectl create -f '+path_bench+'parsec-'+benchmarks[i]+'.yaml')
			while True:
				out = issue('kubectl get jobs')
				if '1/1' in out:
					break
				time.sleep(10)
			os.system("kubectl logs $(kubectl get pods --selector=job-name="+"parsec-"+jobs[i]+" --output=jsonpath='{.items[*].metadata.name}') > "
			      +path_log+benchmarks[i]+'_'+interference[j]+'_'+str(rep)+'.txt')
			with open(path_log+benchmarks[i]+'_'+interference[j]+'_'+str(rep)+'.txt', 'r') as f:
				print(''.join(f.readlines()))
			issue('kubectl delete jobs --all')
			time.sleep(1)
			issue('kubectl delete pods --all')
			time.sleep(5)