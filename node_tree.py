"""
A 'Directed Acyclic Graph'(DAG) is a finite, directed graph with no 'directed'
cycles, I.e. There is no way to start at node 'X' and follow the a
consistently-directed sequence of nodes in a way that eventually loops back to 'X'
It is 'Hierarchical'.

Examples of data that fit this type of graph include, but are not limited to:

    Genology or Taxonomy
    Node Trees
    Neural Network
    Causality
    The Flow of Time, outside of certain specific interpretations of QM

'A' causes 'B' causes 'C', but 'C' cannot then cause 'A'. There are no Loops.
"""

from manimlib.imports import *
import uuid

class Node(Circle):
    CONFIG = {
        "radius" : 0.15,
        "stroke_color" : BLUE,
        "stroke_width" : 3,
        "fill_color" : BLUE,
        "fill_opacity" : .5,
    }
    def __init__(self, **kwargs):
        Circle.__init__(self, **kwargs)
        self._id = str(uuid.uuid4())[:8]
        self._data = 0
        self._fpointers = []
        self._bpointers = []

class TestNetwork(object):
    def __init__(self, **kwargs):
        #Network.__init__(self, **kwargs)
        self.root = None
        self.network = [[]]
        self.layer_sizes = []
        self.num_layers = 0

    def __str__(self):
        name_str = "["
        id_str = "["
        for node in self.iter_network():
            name_str += node._name +  ", "
            id_str += str(node._id) + ", "
        name_str = name_str[:-2] + "]"
        id_str = id_str[:-2] + "]"
        return name_str + "\n" + id_str

    def __iter__(self):
        return self

    def __next__(self):
        for layer in self.network:
            for node in layer:
                return node

    def add_node(self, _n_name="", _bp_name=None):
        n_node = Node()
        if self.root is None:
            n_node._name = _n_name
            n_node._id = 0
            n_node._layer = 0
            self.root = n_node
            self.root._bpointers = [None]
            self.network = [[self.root]]
        else:
            __bp = self._fetch_bp(_bp_name)
            self._add_node(n_node, _n_name, __bp)

    def _add_node(self, node, _n_name, bpointer):
        node._name = _n_name
        node._id = -1
        node._bpointers.append(bpointer)
        if bpointer is not None:
            bpointer._fpointers.append(node)
            self._update_network(self.root, [[self.root]])
            self._update_ids(bpointer._id)
        else:
            self._update_network(self.root, [[self.root]])

    def iter_network(self):
        for layer in self.network:
            for node in layer:
                yield node

    def _fetch_bp(self, _bp_name=""):
        __bp = None
        for layer in self.network:
            for node in layer:
                if _bp_name is "None":
                    __bp = None
                    break
                elif node._name == _bp_name:
                    __bp = node
                    break
        return __bp

    def import_network(self, layout):
        for layer_num, layer in layout.items():
            for n_name, bp in layer.items():
                self.add_node(_n_name=n_name, _bp_name=bp)

    def export_network(self):
        layout = {}
        i=0
        for layer in self.network:
            temp_dict = {}
            for node in layer:
                temp_dict.update( {node._name : node._bpointers[0]} )
            layout[i] = temp_dict
            i += 1
        return layout

    def _update_network(self, node, network=[[]], __flag=0):
        __layer = __flag+1
        __temp_network = network

        for fp in node._fpointers:
            if fp._fpointers is not []:
                fp._layer = __layer
                if fp is node._fpointers[0]: __temp_network.append([])
                __temp_network[__layer].append(fp)
                self._update_network(fp, __temp_network, __layer)
            else:
                fp._layer = __layer
                __temp_network[__layer].append(fp)

        if __flag is 0:
            self.network = __temp_network
        else:
            return __temp_network

    def _update_ids(self, new_id):
        __layer_sizes = []
        for layer in self.network:
            __layer_size = 0
            for node in layer:
                __layer_size += 1
                if node._id is -1:
                    node._id = new_id
                elif node._id >= new_id:
                    node._id += 1
            if __layer_size is not 0: __layer_sizes.append(__layer_size)
        self.layer_sizes = __layer_sizes
        self.num_layers = len(self.layer_sizes)


class DAG(VGroup):
    CONFIG = {
        "node_radius" : 0.25,
        "node_buff" : MED_SMALL_BUFF,
        "layer_buff" : LARGE_BUFF,
        "node_stroke_color" : BLUE,
        "node_stroke_width" : 3,
        "node_fill_color" : BLUE,
        "edge_color" : LIGHT_GREY,
        "edge_stroke_width" : 2,
        "edge_propogation_color" : YELLOW,
        "edge_propogation_time" : 1,
        "max_shown_nodes" : 16,
        "brace_for_large_layers" : True,
        "average_shown_activation_of_large_layer" : True,
        "include_output_labels" : False,
    }
    def __init__(self, network=None, **kwargs):
        VGroup.__init__(self, **kwargs)
        if network is None:
            self.network = self.temp_network()
        else:
            self.network = network
        self.add_nodes()
        self.add_edges()

    def add_nodes(self):
        layers = VGroup(*[
            self.get_layer(layer)
            for layer in self.network
        ])

        layers.arrange(UP, buff = self.layer_buff)

        self.layers = layers
        self.add(self.layers)

        if self.include_output_labels:
            self.add_output_labels()

    def get_layer(self, _layer):
        layer = VGroup()
        num_nodes = len(_layer)

        if num_nodes > self.max_shown_nodes: num_nodes = self.max_shown_nodes
        nodes = VGroup(*[
            self.get_node(node)
            for node in _layer
        ])

        nodes.arrange(RIGHT, buff = self.node_buff)

        layer.nodes = nodes
        layer.add(nodes)

        if len(_layer) > num_nodes:
            dots = TexMobject("\\vdots")
            dots.move_to(nodes)
            VGroup(*nodes[:len(nodes) // 2]).next_to(
                dots, UP, MED_SMALL_BUFF
            )
            VGroup(*nodes[len(nodes) // 2:]).next_to(
                dots, DOWN, MED_SMALL_BUFF
            )
            layer.dots = dots
            layer.add(dots)
            if self.brace_for_largesizess:
                brace = Brace(layer, LEFT)
                brace_label = brace.get_tex(str(size))
                layer.brace = brace
                layer.brace_label = brace_label
                layer.add(brace, brace_label)

        return layer

    def get_node(self, node):
        node.edges_in = VGroup()
        node.edges_out = VGroup()

        return node

    def add_edges(self):
        self.edge_groups = VGroup()
        for l1, l2 in zip(self.layers[:-1], self.layers[1:]):
            edge_group = VGroup()
            for n1, n2 in it.product(l1.nodes, l2.nodes):
                for n1_fp in n1._fpointers:
                    if n1_fp._id == n2._id:
                        edge = self.get_edge(n1, n2)
                        edge_group.add(edge)
                        n1.edges_out.add(edge)
                        n2.edges_in.add(edge)
            self.edge_groups.add(edge_group)
        self.add_to_back(self.edge_groups)

    def get_edge(self, n1, n2):
        return Line(
            n1.get_center(),
            n2.get_center(),
            buff = self.node_radius,
            stroke_color = self.edge_color,
            stroke_width = self.edge_stroke_width,
        )


class NetTest(Scene):
    CONFIG = {
        "layout" : {
            0 : {"A":"None"},
            1 : {"B":"A", "D":"A"},
            2 : {"C":"B", "E":"D", "F":"D"},
        },
        "network_mob_config" : {},
    }
    def construct(self):
        self.add_network()

        self.wait()
        self.play(
            DrawBorderThenFill(self.dag.layers),
            lag_ratio = 0.5,
            run_time = 2,
            rate_func=linear
        )
        self.wait()


        self.play(ShowCreation(
            self.dag.edge_groups,
            lag_ratio = 0.5,
            run_time = 2,
            rate_func=linear,
        ))
        self.wait()


    def add_network(self):
        self.network_obj = TestNetwork()
        self.network_obj.import_network(self.layout)
        self.dag = DAG(
            self.network_obj.network,
            **self.network_mob_config
        )
