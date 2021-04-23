import subprocess
import threading
import time
import json

def print_stdout(stdout):
    stdout = stdout.split('\n')
    for line in stdout:
        print(">>> " + line.strip())

def run_shell_cmd(cmd):
    print('*** ' + cmd)
    process = subprocess.Popen(cmd.split(' '), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    print_stdout(stdout.decode().strip())
    print()

def is_job_complete(job):
    cmd = 'kubectl get jobs -o json'
    process = subprocess.Popen(cmd.split(' '), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    json_obj = json.loads(stdout.decode().strip())
    # print(json_obj)
    for item in json_obj['items']:
        name = str(item['metadata']['name'])
        if name != job:
            continue
        # print(name)
        if 'active' in item['status'].keys():
            return False
        assert item['status']['succeeded']
        return True
    assert False

def scheduler_2_core():
    run_shell_cmd('kubectl create -f parsec-dedup.yaml')
    time.sleep(1)
    while not is_job_complete('parsec-dedup'):
        time.sleep(1)

    run_shell_cmd('kubectl create -f parsec-blackscholes.yaml')
    run_shell_cmd('kubectl get jobs')

def scheduler_4_core():
    run_shell_cmd('kubectl create -f parsec-fft.yaml')
    run_shell_cmd('kubectl create -f parsec-freqmine.yaml')
    run_shell_cmd('kubectl get jobs')

def scheduler_8_core():
    run_shell_cmd('kubectl create -f parsec-ferret.yaml')
    run_shell_cmd('kubectl create -f parsec-canneal.yaml')
    run_shell_cmd('kubectl get jobs')

# def scheduler_2_core():
#     run_shell_cmd('kubectl create -f parsec-dedup.yaml')
#     run_shell_cmd('kubectl create -f parsec-fft.yaml')
#     run_shell_cmd('kubectl get jobs')

# def scheduler_4_core():
#     run_shell_cmd('kubectl create -f parsec-canneal.yaml')
#     run_shell_cmd('kubectl create -f parsec-freqmine.yaml')
#     run_shell_cmd('kubectl get jobs')

# def scheduler_8_core():
#     run_shell_cmd('kubectl create -f parsec-ferret.yaml')
#     run_shell_cmd('kubectl create -f parsec-blackscholes.yaml')
#     run_shell_cmd('kubectl get jobs')

if __name__ == '__main__':
    # start memcached
    # run_shell_cmd('kubectl create -f memcache-t1-cpuset.yaml')
    # run_shell_cmd('kubectl expose pod some-memcached --name some-memcached-11211 --type LoadBalancer --port 11211 --protocol TCP')
    # run_shell_cmd('sleep 60')
    # run_shell_cmd('kubectl get service some-memcached-11211')

    # run_shell_cmd('kubectl get pods -o wide')
    # time.sleep(60)

    thread_2_core = threading.Thread(target=scheduler_2_core)
    thread_2_core.start()
    thread_4_core = threading.Thread(target=scheduler_4_core)
    thread_4_core.start()
    thread_8_core = threading.Thread(target=scheduler_8_core)
    thread_8_core.start()

    thread_2_core.join()
    thread_4_core.join()
    thread_8_core.join()