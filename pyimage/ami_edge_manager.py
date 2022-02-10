import logging
import pprint
# local
from ..pyimage.ami_plot import AmiLine, AmiPolyline
from ..pyimage.ami_plot import POLYLINE
from ..pyimage.ami_plot import AmiLineTool
from ..pyimage.ami_graph_all import AmiEdge

logger = logging.getLogger(__name__)

COORD = 0
COUNT = 1
X = 0
Y = 1
XY = ["X", "y"]

""" terms
AmiEdge is a graph-edge between 2 AmiNodes. It need not be straight (but normally cannot intersect itself)
There can be 2 or more AmiEdges between 2 AmiNodes. It normally contains a thread of pixels "points";
 
AmiLine represents straight lines between 2 points (often AmiNodes, but often unnamed). 
an AmiEdge containa 0, 1 or many AmiLines.
AmiLines should retain backreferences to the AmiEdges - not fully implemented.

X is horizontal
Y is vertical (normally increasing down the page, origin is top-left)

"""


class AmiEdgeAnalyzer:
    """
    contains and analyzes edges, building higher-level objects
    """

    def __init__(self, tolerance=1, island=None):
        self.horizontal_edges = None
        self.horiz_ami_lines = None
        self.horiz_ami_polylines = []
        self.horiz_line_tool = None
        self.horiz_dict = dict()
        self.line_y_coords_by_count = None

        self.vertical_edges = None
        self.vert_ami_lines = None
        self.vert_ami_polylines = []
        self.vert_line_tool = None
        self.vert_dict = dict()
        self.line_x_coords_by_count = None

        self.non_axial_edges = None
        self.axial_polylines = None
        self.tolerance = tolerance
        self.island = island

    def read_edges(self, ami_edges):
        self.horizontal_edges = AmiEdge.get_horizontal_edges(ami_edges, tolerance=self.tolerance)
        self.vertical_edges = AmiEdge.get_vertical_edges(ami_edges, tolerance=self.tolerance)
        self.non_axial_edges = AmiEdge.get_non_axial_edges(ami_edges, tolerance=self.tolerance)
        print(f"non_axial {len(self.non_axial_edges)}")
        for non_axial_edge in self.non_axial_edges:
            logger.debug(f"non-axial {non_axial_edge.pixel_length()} {round(non_axial_edge.get_cartesian_length(), 2)}"
                         f" {non_axial_edge.xdelta_direct} {non_axial_edge.ydelta_direct}")

        self.horiz_ami_lines = AmiEdge.get_single_lines(self.horizontal_edges)
        self.vert_ami_lines = AmiEdge.get_single_lines(self.vertical_edges)

        self.axial_polylines = AmiEdge.get_axial_polylines(ami_edges, tolerance=self.tolerance)

        self.extract_lines_from_polylines()

        self.vert_dict = AmiLine.get_horiz_vert_counter(self.vert_ami_lines, xy_index=0)
        self.horiz_dict = AmiLine.get_horiz_vert_counter(self.horiz_ami_lines, xy_index=1)

    def extract_lines_from_polylines(self):
        """find horizonatl and verticakl segments in polylines/edges"""
        logger.debug(f"extracting lines from axial polylines {len(self.axial_polylines)}")
        for axial_polyline in self.axial_polylines:
            logger.debug(f"axial polyline: {axial_polyline}")
            for ami_line in axial_polyline:
                if ami_line.is_vertical(tolerance=self.tolerance):
                    self.vert_ami_lines.append(ami_line)
                elif ami_line.is_horizontal(tolerance=self.tolerance):
                    self.horiz_ami_lines.append(ami_line)
                else:
                    raise ValueError(f"line {ami_line} must be horizontal or vertical")

    def merge_neighbouring_coords(self) -> tuple:
        """
        create Counters for vertical lines (x coord) and horizontal (y-coords)
        :return: x_counter, y_counter
        """
        self.line_x_coords_by_count = self._merge_close_bins(self.vert_dict.most_common())
        self.line_y_coords_by_count = self._merge_close_bins(self.horiz_dict.most_common())
        return self.line_x_coords_by_count, self.line_y_coords_by_count

    def _merge_close_bins(self, coord_counts):
        """merge counts of bins within tolerance

        :param coord_counts: Counter of count by coordinate
        :return: updated counter"""

        filtered_counts = []
        while len(coord_counts) > 0:
            coord_count = coord_counts[0]
            change = False
            for filtered_count in filtered_counts:
                if abs(filtered_count[COORD] - coord_count[COORD]) <= self.tolerance:
                    filtered_count[COUNT] += coord_count[COUNT]
                    change = True
                    break
            if not change:
                filtered_counts.append([coord_count[COORD], coord_count[COUNT]])
            coord_counts.remove(coord_count)
        return filtered_counts

    # TODO move to AmiLineTool
    def join_ami_lines(self, xy_flag):
        """
        join lines with constant coordinate (vert/X, or horiz/Y)

        :param xy_flag: 0 or 1 for X/Y
        :return: joined lines as list

        default is lines must touch within self.tolerance. gap_factor = 1.0 gives
        ___   ___   ___ (uniformly spaded white/black)

        """

        line_coords_by_count = self.line_x_coords_by_count if xy_flag == X else self.line_y_coords_by_count
        line_tool = AmiLineTool(mode=POLYLINE, xy_flag=xy_flag)
        for this_coord, count in line_coords_by_count:
            ami_lines = self.find_sorted_ami_lines_with_coord(xy_flag, this_coord)
            for segment in ami_lines:
                line_tool.add_segment(segment)
        return line_tool

    @classmethod
    def _delta(cls, point0, point1):
        return min(abs(point0[0] - point1[0]), abs(point0[0] - point1[1]))

    @classmethod
    def _join(cls, long_ami_line, ami_line):
        """joins growing end of long_ami_line to ami_line
        """
        long_ami_line.xy2 = ami_line.xy2
        long_ami_line.mid_points.append(ami_line.xy1)
        return long_ami_line

    # def add_ami_lines_to_long_lines(self, ami_line, long_ami_line):
    #     """
    #
    #     :param ami_line:
    #     :param long_ami_line:
    #     :return: list of long_ami_lines
    #
    #     """
    #     long_ami_lines = []
    #     if long_ami_line is None:
    #         long_ami_line = ami_line
    #         long_ami_lines.append(long_ami_line)
    #         long_ami_line.mid_points = []
    #         return
    #     else:
    #         point0 = long_ami_line.xy2  # joinable point
    #         point1 = ami_line.xy1  # incoming joinable point
    #         if self._delta(point0, point1) <= self.tolerance:
    #             # close enough? join
    #             long_ami_line = self._join(long_ami_line, ami_line)
    #         else:
    #             # no, create new line
    #             long_ami_line = None
    #
    #     return long_ami_lines

    # @classmethod
    # def create_new_line_with_ascending_coords(cls, ami_line, xy_flag):
    #     """NOT TESTED"""
    #     # [[[66, 61], [66, 131]], [[66, 131], [66, 185]],...
    #     other = 1 - xy_flag
    #     swap = ami_line.xy1[other] < ami_line.xy2[other]
    #     xy1 = [ami_line.xy1[xy_flag], ami_line.xy1[other]] if swap else [ami_line.xy2[xy_flag], ami_line.xy2[other]]
    #     xy2 = [ami_line.xy2[xy_flag], ami_line.xy2[other]] if swap else [ami_line.xy1[xy_flag], ami_line.xy1[other]]
    #     return AmiLine(xy12=[xy1, xy2])

    def find_sorted_ami_lines_with_coord(self, xy_flag, coord):
        """
        finds axial lines with coord within self.tolerance
        :param xy_flag: X or Y
        :param coord:
        :return: list of lines
        """
        ami_lines = []
        lines_to_search = self.vert_ami_lines if xy_flag == X else self.horiz_ami_lines
        for line in lines_to_search:
            if abs(line.xy_mid[xy_flag] - coord) <= self.tolerance:
                ami_lines.append(line)
        other_coord = 1 - xy_flag
        ami_lines = sorted(ami_lines, key=lambda linex: linex.xy1[other_coord])
        return ami_lines

    def create_horiz_vert_line_tools(self, island):
        """create horizontal and vertical line_tools
        :param island:
        :return: horizontal line tool, vertical line tool

        """
        ami_edges = island.get_or_create_ami_edges()
        self.read_edges(ami_edges)
        self.merge_neighbouring_coords()
        self.vert_line_tool = self.join_ami_lines(X)
        self.horiz_line_tool = self.join_ami_lines(Y)

    def make_horiz_vert_polylines(self, min_horiz_length=0, min_vert_length=0):
        self.create_horiz_vert_line_tools(self.island)

        self.horiz_ami_polylines = self._create_polylines(min_horiz_length, self.horiz_line_tool.line_points_list)
        self.vert_ami_polylines = self._create_polylines(min_vert_length, self.vert_line_tool.line_points_list)

        self.find_crossing_horiz_vert_polylines()

    @classmethod
    def _create_polylines(cls, min_length, points_list_x):
        polylines = []
        for line in points_list_x:
            ami_polyline = AmiPolyline(points_list=line)
            if ami_polyline.get_cartesian_length() > min_length:
                polylines.append(ami_polyline)
        return polylines

    def find_crossing_horiz_vert_polylines(self):

        h_poly_dict = dict()
        h_poly_dict["intersect"] = []
        v_poly_dict = dict()
        v_poly_dict["intersect"] = []
        for h_ami_polyline in self.horiz_ami_polylines:
            h_box = h_ami_polyline.get_bounding_box()
            for v_ami_polyline in self.vert_ami_polylines:
                v_box = v_ami_polyline.get_bounding_box()
                intersect_box = h_box.intersect(v_box)
                if intersect_box and intersect_box.is_valid():
                    h_points = h_ami_polyline.find_points_in_box(intersect_box)
                    if len(h_points) == 1:
                        h_point = h_points[0]
                        v_points = v_ami_polyline.find_points_in_box(intersect_box)
                        if len(v_points) == 1:
                            v_point = v_points[0]
                            h_poly_dict["intersect"].append((h_point, v_point, v_ami_polyline.id))
                            h_lines = h_ami_polyline.split_line(h_point)
                            v_poly_dict["intersect"].append((v_point, h_point, h_ami_polyline.id))
                            v_lines = v_ami_polyline.split_line(v_point)
                            print(
                                f"H  {h_point} // {len(h_lines)} {h_lines} // "
                                f"\nV {v_point} // {len(v_lines)} {v_lines}")
                        else:
                            print(f"too many v_points {v_points}")
                    else:
                        print(f"too many h_points {h_points}")
        pprinter = pprint.PrettyPrinter(indent=4)
        pprinter.pprint(h_poly_dict)
        pprinter.pprint(v_poly_dict)
