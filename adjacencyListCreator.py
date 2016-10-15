import math
import random
import numpy as np
import matplotlib.pyplot as plt
import pylab

class Point(object):
    '''Creates a point on a coordinate plane with values x and y.'''

    COUNT = 0

    def __init__(self, id,x, y):
        self.X = x
        self.Y = y
        self.ID = id
        self.degree = 0
        self.adjacent_points = []

    def __str__(self):
        return "Point %s: %s"%(self.ID,[p.get_ID() for p in self.adjacent_points])


    def get_X(self):
        return self.X

    def get_Y(self):
        return self.Y

    def get_ID(self):
        return self.ID

    def get_degree(self):
        return self.degree

    def get_adjacent_points(self):
        return self.adjacent_points

    def distance(self, other):
        dx = self.X - other.X
        dy = self.Y - other.Y
        return math.hypot(dx, dy)

    def is_inside_unit_circle(self):
        return math.pow(self.X - 1,2) + math.pow(self.Y - 1,2) < 1

    def set_adjacent_points_and_degree(self,point_list,radius):
        for point in point_list:
            if point.get_ID() == self.get_ID():
                #Compare all points up to the current point. Don't compare with the points afterwards.
                return
            if self.distance(point) <= radius:
                self.adjacent_points.append(point)
                self.degree += 1
                point.adjacent_points.append(self)
                point.degree += 1



def get_radius_from_average_degree(average_degree,sensors,disk):
    if disk:
        return math.sqrt((average_degree + 1)/sensors)
    else:
        return math.sqrt((average_degree + 1)/(sensors *math.pi))


def initialize_points_disk(sensors):
    current_sensors = 0
    sensors_array = []
    while current_sensors < sensors:
        x = random.uniform(0,2)
        y = random.uniform(0,2)
        point = Point(current_sensors,x,y)
        if point.is_inside_unit_circle():
            sensors_array.append(point)
            current_sensors += 1
    return sensors_array


def initialize_points_square(sensors):
    sensors_array = []
    for current_sensor in range(0,sensors):
        x = random.random()
        y = random.random()
        point = Point(current_sensor,x,y)
        sensors_array.append(point)
    return sensors_array



def initialize_points(sensors, disk):
    if disk:
        return initialize_points_disk(sensors)
    else:
        return initialize_points_square(sensors)


def create_adjacency_list_with(disk,sensors,radius,name):
    points = initialize_points(sensors, disk)
    xs = [p.get_X() for p in points]
    ys = [p.get_Y() for p in points]
    plt.scatter(xs, ys)
    plt.savefig(name + '_sensor_plot.png')
    number_of_edges = 0
    degree_frequency_dictionary = {}
    points.sort(key=lambda p: p.get_X(), reverse=True)
    for point in points:
        #Uses the sweep method
        point.set_adjacent_points_and_degree(points, radius)
    for point in points:
        number_of_edges += point.get_degree()
        if point.get_degree() in degree_frequency_dictionary:
            degree_frequency_dictionary[point.get_degree()] += 1
        else:
            degree_frequency_dictionary[point.get_degree()] = 1
    real_average_degree = float(number_of_edges) / len(points)
    frequencies = np.arange(len(degree_frequency_dictionary))
    plt.clf()
    plt.bar(frequencies, degree_frequency_dictionary.values(), align='center', width=0.5)
    plt.xticks(frequencies, degree_frequency_dictionary.keys())
    plt.ylim(0, max(degree_frequency_dictionary.values()) + 1)
    plt.savefig(name + '_degree_histogram.png')
    print(points)


def create_adjacency_list():
    try:
        square_or_disk = raw_input('Use a square (s) or a disk (d) area?:')
        disk = False
        if square_or_disk == 'd':
            disk = True
        elif square_or_disk != 's':
            raise ValueError
        sensors = int(raw_input('Enter amount of sensors desired:'))
        radius_or_average_degree = raw_input('Will you enter sensor radius (r) or average degree (d)?:')
        if radius_or_average_degree == 'r':
            radius = float(raw_input('Enter radius:'))
        elif radius_or_average_degree == 'd':
            average_degree = float(raw_input('Enter average degree:'))
            radius = get_radius_from_average_degree(average_degree, sensors, disk)
        else:
            raise ValueError
        create_adjacency_list_with(disk,sensors,radius,"iograph")

    except ValueError:
        print ("Invalid raw_input.")

def execute_benchmark_case(disk,sensors,average_degree,name):
    create_adjacency_list_with(disk,sensors,get_radius_from_average_degree(average_degree,sensors,disk),name)


if __name__ == '__main__':
    #create_adjacency_list()
    execute_benchmark_case(False,1000,32,"benchmark1")
    #execute_benchmark_case(False,4000,64,"benchmark2")
    #execute_benchmark_case(False,16000,64,"benchmark3")
    #execute_benchmark_case(False,64000,64,"benchmark4")
    #execute_benchmark_case(False,64000,128,"benchmark5")
    #execute_benchmark_case(True,4000,64,"benchmark6")
    #execute_benchmark_case(True,4000,128,"benchmark7")
