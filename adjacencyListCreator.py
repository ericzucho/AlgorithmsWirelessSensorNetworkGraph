import copy
import math
import random
import numpy as np
import matplotlib.pyplot as plt
import pylab
import collections

class Point(object):
    '''Creates a point on a coordinate plane with values x and y.'''

    COUNT = 0

    def __init__(self, id,x, y):
        self.X = x
        self.Y = y
        self.ID = id
        self.degree = 0
        self.adjacent_points = []
        self.color = -1

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

    def get_color(self):
        return self.color

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


def print_part_1_output(sensors, number_of_edges, radius, real_average_degree,min_degree,max_degree):
    print("Sensors: " + str(sensors))
    print("Number of distinct pairwise sensor adjacencies: " + str(number_of_edges/2))
    print("Distance bound for adjacency: " + str(radius))
    print("Average degree: " + str(real_average_degree))
    print("Minimum degree: " + str(min_degree))
    print("Maximum degree: " + str(max_degree))


def order_vertices_smallest_last(degree_list,name):
    smallest_last_vertex_ordering = []
    degree_when_deleted_dictionary = {}
    max_degree_when_deleted = -99999
    degree_list_ordered = collections.OrderedDict(sorted(degree_list.items()))
    while len(degree_list_ordered) > 0:
        #Get the first point from the ordered degree list.
        point = degree_list_ordered.items()[0][1][0]
        #Fill in the dictionary for the graph
        if point.get_degree() in degree_when_deleted_dictionary:
            degree_when_deleted_dictionary[point.get_degree()] += 1
        else:
            degree_when_deleted_dictionary[point.get_degree()] = 1
        if point.get_degree() > max_degree_when_deleted:
            max_degree_when_deleted = point.get_degree()
        #Insert it into the smallest last degree list
        smallest_last_vertex_ordering.append(point)
        #Delete it from the ordered degree list
        del degree_list_ordered.items()[0][1][0]
        #Delete the whole key if it no longer has values
        if len(degree_list_ordered.items()[0][1]) == 0:
            del degree_list_ordered[point.get_degree()]
        #Reduce de degree of all adjacent points by one.
        for adjacent_point in point.get_adjacent_points():
            degree_list_ordered[adjacent_point.get_degree()].remove(adjacent_point)
            if len(degree_list_ordered[adjacent_point.get_degree()]) == 0:
                del degree_list_ordered[adjacent_point.get_degree()]
            if adjacent_point.get_degree() - 1 in degree_list_ordered:
                degree_list_ordered[adjacent_point.get_degree() - 1].append(adjacent_point)
            else:
                degree_list_ordered[adjacent_point.get_degree() - 1] = []
                degree_list_ordered[adjacent_point.get_degree() - 1].append(adjacent_point)
            adjacent_point.degree -= 1
            adjacent_point.adjacent_points.remove(point)

    #Save plot
    degrees_when_deleted = np.arange(len(degree_when_deleted_dictionary))
    plt.clf()
    plt.bar(degrees_when_deleted, degree_when_deleted_dictionary.values(), align='center', width=0.5)
    plt.xticks(degrees_when_deleted, degree_when_deleted_dictionary.keys())
    plt.ylim(0, max(degree_when_deleted_dictionary.values()) + 1)
    plt.savefig(name + '_degree_when_deleted.png')

    print("Maximum degree when deleted: " + str(max_degree_when_deleted))

    return smallest_last_vertex_ordering


def color_points(smallest_last_vertex_ordering,original_point_adjacency_list,nodes,colors,name):
    smallest_last_vertex_ordering[nodes-1].color = 0
    for point in reversed(smallest_last_vertex_ordering[:nodes-1]):
        point_original = next(i for i in original_point_adjacency_list if i.get_ID() == point.get_ID())
        point = try_to_put_point_color(0,point,point_original,colors)
    color_frequency_dictionary = {}
    for point in original_point_adjacency_list:
        if point.get_color() in color_frequency_dictionary:
            color_frequency_dictionary[point.get_color()] += 1
        else:
            color_frequency_dictionary[point.get_color()] = 1
    plt.clf()
    frequencies = np.arange(len(color_frequency_dictionary))
    plt.bar(frequencies, color_frequency_dictionary.values(), align='center', width=0.5)
    plt.xticks(frequencies, color_frequency_dictionary.keys())
    plt.ylim(0, max(color_frequency_dictionary.values()) + 1)
    plt.savefig(name + '_color_frequency.png')


def try_to_put_point_color(candidate_color,point,point_original,colors):
    this_color_viable = True
    for adjacent_point in point_original.get_adjacent_points():
        if adjacent_point.get_color() != -1 and adjacent_point.get_color() == candidate_color:
            this_color_viable = False
            if candidate_color == len(colors) - 1:
                colors.append(candidate_color+1)
                point.color = candidate_color + 1
            else:
                point = try_to_put_point_color(candidate_color+1,point,point_original,colors)
    if this_color_viable:
        point.color = candidate_color
    return point


def create_adjacency_list_with(disk,sensors,radius,name):
    points = initialize_points(sensors, disk)
    number_of_edges = 0
    degree_frequency_dictionary = {}
    degree_list = {}
    points.sort(key=lambda p: p.get_X(), reverse=True)
    min_degree = 999999
    max_degree = -999999
    for point in points:
        #Uses the sweep method
        point.set_adjacent_points_and_degree(points, radius)
    for point in points:
        number_of_edges += point.get_degree()
        if point.get_degree() > max_degree:
            max_degree = point.get_degree()
        if point.get_degree() < min_degree:
            min_degree = point.get_degree()
        if point.get_degree() in degree_frequency_dictionary:
            degree_frequency_dictionary[point.get_degree()] += 1
        else:
            degree_frequency_dictionary[point.get_degree()] = 1
            degree_list[point.get_degree()] = []
        degree_list[point.get_degree()].append(point)
    real_average_degree = float(number_of_edges) / len(points)
    frequencies = np.arange(len(degree_frequency_dictionary))
    fig= plt.gcf()
    ax = plt.gca()
    for point in points:
        if point.get_degree() == min_degree or point.get_degree() == max_degree:
            ax.add_artist(plt.Circle((point.get_X(), point.get_Y()), radius, color='black', fill=False))
        if point.get_degree() == min_degree:
            color = 'y'
        else:
            if point.get_degree() == max_degree:
                color = 'r'
            else:
                color = 'b'
        plt.scatter([point.get_X()],[point.get_Y()],color=color)
    fig.savefig(name + '_sensor_plot.png')
    plt.clf()
    plt.bar(frequencies, degree_frequency_dictionary.values(), align='center', width=0.5)
    plt.xticks(frequencies, degree_frequency_dictionary.keys())
    plt.ylim(0, max(degree_frequency_dictionary.values()) + 1)
    plt.savefig(name + '_degree_histogram.png')
    print_part_1_output(sensors,number_of_edges,radius,real_average_degree,min_degree,max_degree)

    smallest_last_vertex_ordering = order_vertices_smallest_last(degree_list,name)
    for point in points:
        point.adjacent_points = []
        point.set_adjacent_points_and_degree(points, radius)
    colors = [0]
    colored_points = color_points(smallest_last_vertex_ordering,points,sensors,colors,name)
    print (smallest_last_vertex_ordering)


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
