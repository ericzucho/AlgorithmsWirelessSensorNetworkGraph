from __future__ import division
import math
import random
import numpy as np
import matplotlib.pyplot as plt
import collections
import operator

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
        self.visited = 0 #For DPS algorithm
        self.taken = 0 #For smallest last ordering, finding clique size
        self.original_degree = 0 #Do not modify, to be used for the sequential coloring plot.

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

    def copy_point(self):
        p = Point(self.get_ID(),self.get_X(),self.get_Y())
        p.color = self.color
        return p

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
                self.original_degree += 1
                point.adjacent_points.append(self)
                point.degree += 1
                point.original_degree += 1

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


def order_vertices_smallest_last(degree_list,name,points,min_degree):
    smallest_last_vertex_ordering = []
    degree_when_deleted = []
    original_degree = []
    max_degree_when_deleted = -99999
    degree_list_ordered = collections.OrderedDict(sorted(degree_list.items()))
    complete_graph_found = False
    amount_of_points = len(points)
    while len(degree_list_ordered) > 0:
        if not complete_graph_found:
            complete_graph = True
            for point in points:
                if point.taken == 1:
                    continue
                if len(point.adjacent_points) != amount_of_points - 1:
                    complete_graph = False
                    break
            if complete_graph:
                print("Terminal clique size: " + str(amount_of_points))
                complete_graph_found = True
        #Get the first point from the ordered degree list.
        point_found = False
        while not point_found:
            if min_degree in degree_list_ordered:
                point = degree_list_ordered[min_degree][0]
                point_found = True
            else:
                min_degree += 1
        #Fill in the lists for the graph
        degree_when_deleted.append(point.get_degree())
        original_degree.append(point.original_degree)

        if point.get_degree() > max_degree_when_deleted:
            max_degree_when_deleted = point.get_degree()
        #Insert it into the smallest last degree list
        smallest_last_vertex_ordering.append(point)
        #Delete it from the ordered degree list
        del degree_list_ordered[min_degree][0]
        #Delete the whole key if it no longer has values
        point.taken = 1
        amount_of_points -= 1
        #Reduce de degree of all adjacent points by one.
        for adjacent_point in point.get_adjacent_points():
            degree_list_ordered[adjacent_point.get_degree()].remove(adjacent_point)
            if adjacent_point.get_degree() - 1 in degree_list_ordered:
                degree_list_ordered[adjacent_point.get_degree() - 1].append(adjacent_point)
            else:
                degree_list_ordered[adjacent_point.get_degree() - 1] = []
                degree_list_ordered[adjacent_point.get_degree() - 1].append(adjacent_point)
            adjacent_point.degree -= 1
            if adjacent_point.get_degree() < min_degree:
                min_degree = adjacent_point.get_degree()
            adjacent_point.adjacent_points.remove(point)
        for amount in degree_list_ordered.items():
            if len(amount[1]) == 0:
                del degree_list_ordered[amount[0]]


    #Save plot
    plt.clf()
    fig = plt.figure()
    ax1 = fig.add_subplot(111)
    points_index = list(range(1, len(points) + 1))
    plt.plot(points_index, degree_when_deleted[::-1], c='b', label='Degree when deleted')
    plt.plot(points_index,original_degree[::-1],c='r', label='Original degree')
    plt.legend(loc='upper right')
    plt.savefig(name + '_sequential_coloring_plot.png')

    print("Maximum degree when deleted: " + str(max_degree_when_deleted))

    return smallest_last_vertex_ordering


def color_points(smallest_last_vertex_ordering,original_point_adjacency_list,nodes,colors,name,color_frequency_dictionary,color_dictionary):
    smallest_last_vertex_ordering[nodes-1].color = 0
    for point in reversed(smallest_last_vertex_ordering[:nodes-1]):
        point_original = next(i for i in original_point_adjacency_list if i.get_ID() == point.get_ID())
        point = try_to_put_point_color(0,point,point_original,colors)
    for point in original_point_adjacency_list:
        if point.get_color() in color_frequency_dictionary:
            color_frequency_dictionary[point.get_color()] += 1
            color_dictionary[point.get_color()].append(point)
        else:
            color_frequency_dictionary[point.get_color()] = 1
            color_dictionary[point.get_color()] = []
            color_dictionary[point.get_color()].append(point)

    plt.clf()
    frequencies = np.arange(len(color_frequency_dictionary))
    plt.bar(frequencies, color_frequency_dictionary.values(), align='center', width=0.5)
    plt.xticks(frequencies, color_frequency_dictionary.keys())
    plt.ylim(0, max(color_frequency_dictionary.values()) + 1)
    plt.savefig(name + '_color_frequency.png')
    print("Amount of colors: " + str(len(colors)))
    print("Largest color class size: " + str(max(color_frequency_dictionary.values())))

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

def depth_first_search(points,initial_point_id,seen=None,path=None):
    point_object = next((x for x in points if x.get_ID() == initial_point_id), None)
    if seen is None: seen = []
    if path is None: path = [point_object]

    seen.append(initial_point_id)

    for adjacent_point in point_object.adjacent_points:
        if adjacent_point.get_ID() not in seen:
            path.append(adjacent_point)
            path = depth_first_search(points, adjacent_point.get_ID(), seen, path)
    return path


def plot_backbone(backbone,problem_name,backbone_name,sensors):
    plt.clf()
    fig= plt.gcf()
    ax = plt.gca()
    starting_point = backbone[0]
    initial_color = starting_point.get_color()
    plt.scatter([starting_point.get_X()],[starting_point.get_Y()],color='b')
    vertices = 1
    edges = []
    edges_count = 0
    for point in backbone[1:]:
        vertices = vertices + 1
        if point.get_color() == initial_color:
            plt.scatter([point.get_X()],[point.get_Y()],color='b')
        else:
            plt.scatter([point.get_X()],[point.get_Y()],color='r')
        for adjacent_point in point.adjacent_points:
            if any(subgraph_item.get_ID() == adjacent_point.get_ID() for subgraph_item in backbone) and not ({point.get_ID(),adjacent_point.get_ID()} in edges or {adjacent_point.get_ID(),point.get_ID()} in edges ):
                plt.plot([point.get_X(), adjacent_point.get_X()], [point.get_Y(), adjacent_point.get_Y()], color='k', linestyle='-', linewidth=1)
                edges_count = edges_count + 1
                edges.append({adjacent_point.get_ID(),point.get_ID()})
    print("Number of vertices: " +str(vertices))
    print("Number of edges: " +str(edges_count))
    print("Domination: " + "{0:.2f}".format(vertices/sensors * 100)+ "%")
    plt.ylim(0, 1.1)
    plt.xlim(0, 1.1)
    fig.savefig(problem_name + '_'+backbone_name+'.png')

def find_backbones(color_dictionary,color_frequency_dictionary,name,sensors):
    sorted_colors =  sorted(color_frequency_dictionary.items(), key=operator.itemgetter(1),reverse=True)
    largest_backbone = []
    second_largest_backbone = []
    largest_backbone_size = -99999
    second_largest_backbone_size = -99999
    largest_backbone_color_1 = -1
    largest_backbone_color_2 = -1
    second_largest_backbone_color_1 = -1
    second_largest_backbone_color_2 = -1

    for i, (color1, color1frequency) in enumerate(sorted_colors[:4]):
        for j, (color2, color2frequency) in enumerate(sorted_colors[:4]):
            if color1 == color2:
                continue
            if i > j:
                continue
            subgraph = []
            for point in color_dictionary[color1]:
                point_copy = point.copy_point()
                for adjacent_point in point.adjacent_points:
                    if adjacent_point.get_color() == color2:
                        if  any(subgraph_item.get_ID() == adjacent_point.get_ID() for subgraph_item in subgraph):
                            previously_copied_point = next((x for x in subgraph if x.get_ID() == adjacent_point.get_ID()), None)
                            previously_copied_point.adjacent_points.append(point_copy)
                            point_copy.adjacent_points.append(previously_copied_point)
                        else:
                            adjacent_point_copy = adjacent_point.copy_point()
                            adjacent_point_copy.adjacent_points.append(point_copy)
                            point_copy.adjacent_points.append(adjacent_point_copy)
                            subgraph.append(adjacent_point_copy)
                subgraph.append(point_copy)
            all_backbones = []
            for start_possibility in subgraph:
                path = depth_first_search(subgraph, start_possibility.get_ID())
                all_backbones.append(path)
            largest_backbone_this_iteration  = max(all_backbones, key=lambda l: len(l))
            if len(largest_backbone_this_iteration) > largest_backbone_size:
                second_largest_backbone_size = largest_backbone_size
                second_largest_backbone = largest_backbone
                largest_backbone_size = len(largest_backbone_this_iteration)
                largest_backbone = largest_backbone_this_iteration
                second_largest_backbone_color_1 = largest_backbone_color_1
                second_largest_backbone_color_2 = largest_backbone_color_2
                largest_backbone_color_1 = color1
                largest_backbone_color_2 = color2
            else:
                if len(largest_backbone_this_iteration) > second_largest_backbone_size:
                    second_largest_backbone_size = len(largest_backbone_this_iteration)
                    second_largest_backbone = largest_backbone_this_iteration
                    second_largest_backbone_color_1 = color1
                    second_largest_backbone_color_2 = color2
    print("---Largest backbone---")
    print("Colors: " + str(largest_backbone_color_1) +", " + str(largest_backbone_color_2))
    plot_backbone(largest_backbone,name,"largest_backbone",sensors)
    print("---Second largest backbone---")
    print("Colors: " + str(second_largest_backbone_color_1) +", " + str(second_largest_backbone_color_2))

    plot_backbone(second_largest_backbone,name,"second_largest_backbone",sensors)





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

    smallest_last_vertex_ordering = order_vertices_smallest_last(degree_list,name,points,min_degree)
    for point in points:
        point.adjacent_points = []
        point.set_adjacent_points_and_degree(points, radius)
    colors = [0]
    color_frequency_dictionary = {}
    color_dictionary = {}
    colored_points = color_points(smallest_last_vertex_ordering,points,sensors,colors,name,color_frequency_dictionary,color_dictionary)

    backbones = find_backbones(color_dictionary,color_frequency_dictionary,name,sensors)



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
    #execute_benchmark_case(False,20,3,"benchmark0")
    execute_benchmark_case(False,1000,32,"benchmark1")
    #execute_benchmark_case(False,4000,64,"benchmark2")
    #execute_benchmark_case(False,16000,64,"benchmark3")
    #execute_benchmark_case(False,64000,64,"benchmark4")
    #execute_benchmark_case(False,64000,128,"benchmark5")
    #execute_benchmark_case(True,4000,64,"benchmark6")
    #execute_benchmark_case(True,4000,128,"benchmark7")
