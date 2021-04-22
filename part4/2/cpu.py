import time

def process_line(line1, line2):
    line1 = line1.strip().split(' ')[1:]
    line1 = [int(x) for x in line1]
    total_time1 = sum(line1)
    line2 = line2.strip().split(' ')[1:]
    line2 = [int(x) for x in line2]
    total_time2 = sum(line2)
    # print(total_time1, total_time2)
    # print(line2[3], line1[3])
    utilization = 1 - ((line2[3] - line1[3]) / (total_time2 - total_time1))
    return utilization * 100

def get_cpu_utilization(cpu_list):
    filename = '/proc/stat'
    # filename = 'test'
    result = []
    with open(filename, 'r') as fi:
        lines1 = fi.readlines()
    time.sleep(0.5)
    with open(filename, 'r') as fi:
        lines2 = fi.readlines()
    for i in cpu_list:
        assert i <= 3 and i >= 0
        result.append(process_line(lines1[i+1], lines2[i+1]))
    return result, time.time()
    

if __name__ == '__main__':
    with open('data', 'w') as fo:
        while True:
            data = get_cpu_utilization([0, 1])
            fo.write(str(data[0][0]))
            fo.write(" ")
            fo.write(str(data[0][1]))
            fo.write(" ")
            fo.write(str(data[1]))
            fo.write("\n")