"""Integration of image processing, binarization, skeletonization and netwprk analysis"""
import matplotlib.pyplot as plt
from skan.pre import threshold

from test.resources import Resources
from skimage import filters, color, io, data, draw
from skimage import morphology
import numpy as np
from skan import skeleton_to_csgraph
import networkx as nx

from pyimage.graph_lib import AmiSkeleton
import sknw



class TestAmiSkeleton:
    def test_basics_biosynth1_no_text(self):
        """Primarily for validating the image data which will be used elsewhere
        Uncomment for debug-like printing"""

        file = Resources.BIOSYNTH1_ARROWS
        assert file.exists()
        image = io.imread(file)
        assert image.shape == (315, 1512)
        npix = image.size
        nwhite = np.sum(image == 255)
        assert nwhite == 469624
        nblack = np.sum(image == 0)
        assert nblack == 1941
        ndark = np.sum(image <= 127)
        assert ndark == 4285
        nlight = np.sum(image > 127)
        assert nlight == 471995
        print(f"\nnpix {npix}, nwhite {nwhite}, nblack {nblack}  nother {npix - nwhite - nblack}, ndark {ndark}, "
              f"nlight {nlight}")
        # print(image)
        # images are not shown in tests, I think
        fig, ax = plt.subplots()
        ax.imshow(image, cmap='gray')

        binary = threshold(image)
        assert binary.shape == (315, 1512)
        nwhite = np.count_nonzero(binary)
        assert nwhite == 471788
        nblack = npix - nwhite
        # print(f"npix {npix}, nwhite {nwhite} nblack {nblack} nother {npix - nwhite - nblack}")
        # print(binary)

        fig, ax = plt.subplots()
        ax.imshow(binary, cmap="gray")

        binary = np.invert(binary)
        nwhite = np.count_nonzero(binary)
        assert nwhite == 4492
        ax.imshow(binary, cmap="gray")

        return

    def test_skeletonize_biosynth1_no_text(self):
        file = Resources.BIOSYNTH1_ARROWS
        assert file.exists()
        skeleton = AmiSkeleton().create_white_skeleton(file)
        assert np.count_nonzero(skeleton) == 1378
        # will be white on gray
        plt.imshow(skeleton, cmap="gray")
        print("\n", skeleton)

    def test_skeleton_to_graph(self):
        ami_skel = AmiSkeleton()
        skeleton = ami_skel.create_white_skeleton(Resources.BIOSYNTH1_ARROWS)
        # build graph from skeleton
        nx_graph = sknw.build_sknw(skeleton)
        ami_skel.plot_nx_graph(nx_graph)

    def test_skeleton_to_graph_text(self):
        ami_skel = AmiSkeleton()
        ami_skel.binarize_skeletonize_sknw_nx_graph_plot(Resources.BIOSYNTH1_TEXT)

    def test_skeleton_to_graph_path1(self):
        AmiSkeleton().binarize_skeletonize_sknw_nx_graph_plot(Resources.BIOSYNTH1)

    def test_skeleton_to_graph_path2(self):
        AmiSkeleton().binarize_skeletonize_sknw_nx_graph_plot(Resources.BIOSYNTH2)

    def test_skeleton_to_graph_path3(self):
        AmiSkeleton().binarize_skeletonize_sknw_nx_graph_plot(Resources.BIOSYNTH3)

    def test_skeleton_to_graph_components_with_nodes(self):
        nx_graph = AmiSkeleton().create_nx_graph_via_skeleton_sknw(Resources.BIOSYNTH1_ARROWS)
        assert nx.algorithms.components.number_connected_components(nx_graph) == 4
        connected_components = list(nx.algorithms.components.connected_components(nx_graph))
        assert connected_components == [{0, 1, 2, 3, 4, 5, 6, 7},
                                        {8, 9, 26, 19},
                                        {10, 11, 12, 13, 14, 15, 16, 17, 18, 20},
                                        {21, 22, 23, 24, 25}]
        assert connected_components[0] == {0,1,2,3,4,5,6,7}
        assert connected_components[1] == {8,9,26,19}

    def test_create_bounding_box_from_node_list(self):
        ami_skeleton = AmiSkeleton()
        nx_graph = ami_skeleton.create_nx_graph_via_skeleton_sknw(Resources.BIOSYNTH1_ARROWS)
        node_ids = {0, 1, 2, 3, 4, 5, 6, 7}
        # coord_list = np.array([0,0])
        coord_list = []

        # "pts" gives all points in the node, "o" gives the centroid
        for id in node_ids:
            centroid_xy = nx_graph.nodes[id][AmiSkeleton.CENTROID]
            print("centroid", centroid_xy, type(centroid_xy))
            coord_list.append(centroid_xy)
            # np.concatenate(np_coords, centroid_xy)
        print("pts ", coord_list)






