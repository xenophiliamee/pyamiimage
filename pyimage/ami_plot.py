import logging
from collections import Counter

logger = logging.getLogger(__name__)


class AmiPlot:
    pass


class AmiLine:
    """This will probably include a third-party tool supporting geometry for lines"""

    def __init__(self, xy12=None, ami_edge=None):
        """xy12 of form [[x1, y1], [x2, y2]]
        direction is xy1 -> xy2 if significant"""
        self.ami_edge = ami_edge
        if xy12 is not None:
            if len(xy12) != 2 or len(xy12[0]) != 2 or len(xy12[1]) != 2:
                raise ValueError(f"bad xy pair for line {xy12}")
            self.xy1 = [xy12[0][0], xy12[0][1]]
            self.xy2 = [xy12[1][0], xy12[1][1]]
        else:
            self.xy1 = None
            self.xy2 = None

    def __repr__(self):
        return str([self.xy1, self.xy2])

    def __str__(self):
        return str([self.xy1, self.xy2])

    def set_ami_edge(self, ami_edge):
        self.ami_edge = ami_edge

    @property
    def vector(self):
        """vector between end points
        :return: xy2 - xy1
        """
        return None if (self.xy1 is None or self.xy2 is None) else \
            (self.xy2[0] - self.xy1[0], self.xy2[1] - self.xy1[1])

    @property
    def xy_mid(self):
        """get midpoint of line
        :return: 2-array [x, y] of None if coords not set"""

        if self.xy1 is not None and self.xy2 is not None:
            return [(self.xy1[0] + self.xy2[0]) / 2, (self.xy1[1] + self.xy2[1]) // 2]
        return None

    def is_horizontal(self, tolerance=1) -> int:
        return abs(self.vector[1]) <= tolerance < abs(self.vector[0])

    def is_vertical(self, tolerance=1) -> int:
        return abs(self.vector[0]) <= tolerance < abs(self.vector[1])

    @classmethod
    def get_horiz_vert_counter(cls, ami_lines, xy_index) -> Counter:
        """
        counts midpoint coordinates of lines (normally ints)

        :param ami_lines: horiz or vert ami_lines
        :param xy_index: 0 (x) 0r 1 (y) (normally 0 for vert lines, 1 for horiz)
        :return: Counter
        """
        hv_dict = Counter()
        for ami_line in ami_lines:
            xy_mid = ami_line.xy_mid[xy_index]
            if xy_mid is not None:
                hv_dict[int(xy_mid)] += 1
        return hv_dict


class AmiEdgeTool:
    """refines edges (join, straighten, break, corners, segments, curves, etc some NYI)
    Still being actively developed
    """

    def __init__(self, ami_graph=None, ami_edges=None, ami_nodes=None):
        """Best to create this from the factory method create_tool"""
        self.ami_graph = ami_graph
        self.ami_edges = ami_edges
        self.ami_nodes = ami_nodes

    @classmethod
    def create_tool(cls, ami_graph, ami_edges=None, ami_nodes=None):
        """preferred method of instantiating tool
        :param ami_graph: required graph
        :param ami_edges: edges to process
        :param ami_nodes: optional nodes (if none uses ends of edges)
        """
        edge_tool = AmiEdgeTool(ami_graph, ami_edges=ami_edges, ami_nodes=ami_nodes)
        if not ami_nodes:
            edge_tool.create_ami_nodes_from_edges()

        return edge_tool

    def analyze_topology(self):
        """counts nodes and edges by recursively iterating over
        noes and their edges -> edges and their nodes
        also only includes start_id < end_id
        (mainly a check)

         :return: nodes, edges"""

        if self.ami_edges is None:
            logger.error(f"no edges, possible error")
        new_ami_edges = set()
        new_ami_nodes = set()
        while self.ami_nodes:
            ami_node = self.ami_nodes.pop()
            new_ami_nodes.add(ami_node)
            node_ami_edges = ami_node.get_or_create_ami_edges()
            for ami_edge in node_ami_edges:
                if ami_edge.has_start_lt_end():
                    if ami_edge not in self.ami_edges:
                        print(f" cannot find {ami_edge} in edges")
                    else:
                        new_ami_edges.add(ami_edge)
        return new_ami_nodes, new_ami_edges

    def create_ami_nodes_from_edges(self):
        """generates unique ami_nodes from node_ids at ends of edges"""
        if not self.ami_nodes:
            self.ami_nodes = set()
            node_ids = set()
            for ami_edge in self.ami_edges:
                node_ids.add(ami_edge.start_id)
                node_ids.add(ami_edge.end_id)
            self.ami_nodes = self.ami_graph.create_ami_nodes_from_ids(node_ids)
