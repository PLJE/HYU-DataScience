import sys
import math
import copy

global inputFileName
global cluster_n
global eps
global min_pts

cluster = 0


class Point:
    def __init__(self, index, x, y):
        self.x = x
        self.y = y
        self.index = index
        self.neighbor_index = []
        self.label = -1  # 초기값 undefined : -1, noise : -2

    def add_neighbor(self, neighbor_index):
        self.neighbor_index.append(neighbor_index)

    def get_neighbor_num(self):
        return len(self.neighbor_index)

    def __str__(self):
        return f"Point(index:{self.index}, x:{self.x}, y:{self.y}, " \
               f"label:{self.label}, neighbors:{self.neighbor_index})"


Points = []  # Point 클래스 배열


def get_input():
    global inputFileName, cluster_n, eps, min_pts
    inputFileName = sys.argv[1]
    cluster_n = int(sys.argv[2])
    eps = float(sys.argv[3])
    min_pts = int(sys.argv[4])

    f = open(inputFileName, mode='r', encoding='utf-8')
    while True:
        line = f.readline()
        if not line:
            break
        parse = line.split()
        Points.append(Point(int(parse[0]), float(parse[1]), float(parse[2])))


def calculate_neighbors():
    for cur_point in Points:
        cur_idx = cur_point.index
        cur_x = cur_point.x
        cur_y = cur_point.y

        for other_point in Points:
            other_idx = other_point.index
            other_x = other_point.x
            other_y = other_point.y
            if cur_idx == other_idx:
                continue
            distance = math.sqrt((other_x - cur_x) ** 2 + (other_y - cur_y) ** 2)
            if distance <= eps:
                cur_point.add_neighbor(other_idx)


def output_result():
    global cluster
    clusters = [[] for _ in range(cluster)]
    for point in Points:
        if point.label < 0:
            continue
        clusters[point.label].append(point.index)

    if cluster_n < cluster:
        diff = cluster - cluster_n
        sorted_clusters = sorted(clusters, key=len)
        result = sorted_clusters[diff:]
        clusters = result

    for i in range(len(clusters)):
        output_name = inputFileName.split('.')[0] + '_cluster_' + str(i) + '.txt'
        f = open(output_name, 'w')
        for idx in clusters[i]:
            f.write(str(idx))
            f.write('\n')


def set_label():
    global cluster
    for point in Points:
        if point.label != -1:
            continue
        neighbor_num = point.get_neighbor_num()
        if neighbor_num + 1 < min_pts:
            point.label = -2  # noise
            continue
        point.label = cluster

        seed_set = copy.deepcopy(point.neighbor_index)

        for q_idx in seed_set:
            q_point = Points[q_idx]
            if q_point.label == -2:
                q_point.label = cluster
            if q_point.label != -1:
                continue

            tmp_seed = copy.deepcopy(q_point.neighbor_index)
            q_point.label = cluster

            if len(tmp_seed) + 1 < min_pts:
                continue
            seed_set += tmp_seed
        cluster += 1


def main():
    get_input()
    calculate_neighbors()
    set_label()
    output_result()


if __name__ == '__main__':
    main()
