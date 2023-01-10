from csv import reader
import math
import numpy as np

#csv読み込み
def csv_file(file):
    with open(file, 'r') as csv_file:
        csv_reader = reader(csv_file)
        data_header = next(csv_reader) #一行目を出力
        data = list(csv_reader)
    return data
  
#計測時間処理
def time(data):
    elapsed_time = 0
    time_list = []
    elapsed_time_list = []
    
    for i in range(len(data)-1):
        time_list.append(float(data[i+1][0]) - float(data[i][0]))
        elapsed_time += time_list[i]
        elapsed_time_list.append(elapsed_time)
        #print(elapsed_time[i])
    return time_list, elapsed_time_list

#z軸データ処理
def accl_z(data):
    z_list = []
    abs_z_list = []
    for i in range(len(data)-1):
        z_list.append(float(data[i+1][3]) - float(data[0][3]))
        abs_z_list.append(math.fabs(z_list[i]))
        #print(z[i])
        #print(absolutely_z[i])
    return z_list, abs_z_list

#速度計算
def speed(data, abs_z, time):
    speed_list = []
    for i in range(len(data)-2):
        speed_list.append(((abs_z[i] + abs_z[i+1]) * time[i]) / 2)
        #print(speed[i])
    return speed_list

#移動距離計算
def distance(data, speed, time):
    distance_sum = 0
    distance_list = []
    distance_sum_list = []
    for i in range(len(data)-3):
        distance_list.append(((speed[i] + speed[i+1]) * time[i]) / 2)
        distance_sum += distance_list[i]
        distance_sum_list.append(distance_sum)
    return distance_sum_list

#分散処理による停止識別
def variance(data):
    var_list = []
    for i in range(len(data)-1):
        var_process = []
        var_process.append(float(data[i][3]))
        var_process.append(float(data[i+1][3]))
        var_list.append(np.var(var_process))
    return var_list

#歩行と停止の区別
def WalkStop(data, speed, time, var_num):
    cor_distance_sum = 0
    cor_distance_list = []
    cor_distance_sum_list = []
    for i in range(len(data)-3):
        if i in var_num:
            cor_distance_list.append(0)
        else:
            cor_distance_list.append((((speed[i] + speed[i+1]) * time[i]) / 2)*5*1.91302504811121) #5m:70
        cor_distance_sum += cor_distance_list[i]
        cor_distance_sum_list.append(cor_distance_sum)
    return cor_distance_sum_list


file = "../20230109/accl30m(1).csv"
data = csv_file(file)
time, elapsed_time = time(data)
z, abs_z = accl_z(data)
speed = speed(data, abs_z, time)
distance_sum = distance(data, speed, time)
var = variance(data)
jerk = jerk(data, time)
jerk_max = max(jerk)
print(jerk_max)
print(min(jerk))
print(max(distance_sum))


var_num = []
for i in range(len(data)-1):
    if var[i] <= 0.001:
        var_num.append(i)
cor = WalkStop(data, speed, time, var_num)
