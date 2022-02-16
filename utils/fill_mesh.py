##
# A script to split simple, architectural geometry into convex pieces.
#
# This script makes use of Blender's built-in "Split Concave Faces" clean-up
# algorithm to break-up the faces of an object into convex pieces. The script
# attempts to identify all the edges that represent convex boundaries, and then
# it splits objects up along those edges. Each resulting piece is then made into
# a closed object by converting it into a convex hull.
#
# Be sure to select the object you wish the split into convex pieces before
# running the script.
#
# NOTE: This script is expecting to work with flat, reasonably clean geometry.
# For example, it is expected to be used when generating collision on the
# ceiling and walls of an architectural visualization project, but is not
# expected to perform well with round or n-gon geometry. Using 
# create_closed_objects=True and matchup_degenerates=True, in particular, does
# not work well with objects that have openings inside.
#
# If this script doesn't work for you, a plug-in like V-HACD may work better.
# This script was written to handle cases V-HACD did not handle well -- flat,
# reasonably rectangular arch. vis. geometry.
#
# @author Guy Elsmore-Paddock <guy.paddock@gmail.com>
#

import bmesh
import bpy
from bpy.types import Operator
import re

from itertools import combinations, count
from math import atan2, pi, radians, degrees
from mathutils import Vector


def split_into_convex_pieces(ob, create_closed_objects=True,
                             matchup_degenerates=True):
    object_name = ob.name

    deselect_all_objects()
    make_all_faces_convex(ob)

    eliminated_piece_names = \
        split_on_convex_boundaries(
            ob,
            create_closed_objects,
            matchup_degenerates
        )

    rename_pieces(object_name, eliminated_piece_names)

    # Deselect everything, for the convenience of the user.
    deselect_all_objects()


def make_all_faces_convex(ob):
    bpy.context.view_layer.objects.active = ob
    bpy.ops.object.mode_set(mode='EDIT')

    # This is what actually defines the new geometry -- Blender creates the
    # convex shapes we need to split by.
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.vert_connect_concave()
    bpy.ops.mesh.select_all(action='DESELECT')


##
# Splits an object into smaller pieces by its convex, planar edges.
#
# In an ideal world, we could just split the object by all the edges that are
# attached to -- and are co-planar with -- the faces of the object, since those
# edges are most likely to represent the convex boundaries of the object. But,
# Blender does not provide an easy way to find such edges.
#
# Instead, we use several heuristics to simulate this type of selection:
#   1. First, we select all the sharp edges of the object, since sharp edges are
#      only co-planar with one of the faces they connect with and are therefore
#      unlikely to represent convex boundary edges.
#   2. Second, we select all edges that are similar in angle to the sharp edges,
#      to catch any edges that are almost steep enough to be sharp edges.
#   3. Third, we invert the selection, which should (hopefully) cause all the
#      convex boundary edges we want to be selected.
#   4. Fourth, we seek out any sharp edges that connect with the convex boundary
#      edges, since we will need to split on these edges as well so that our
#      "cuts" go all the way around the object (e.g. if the convex boundary
#      edges lay on the top and bottom faces of an object, we need to select
#      sharp edges to connect the top and bottom edges on the left and right
#      sides so that each split piece is a complete shape instead of just
#      disconnected, detached planes).
#   4. Next, we split the object by all selected edges, which should result in
#      creation of each convex piece we seek.
#
def split_on_convex_boundaries(ob, create_closed_objects=True,
                               matchup_degenerates=True):
    bpy.ops.object.mode_set(mode='EDIT')

    select_convex_boundary_edges(ob)

    # Now perform an vertex + edge split along each selected edge, which should
    # result in the object being broken-up along each planar edge and connected
    # sharp edges (e.g. on corners).
    bpy.ops.mesh.edge_split(type='VERT')

    # Now, just break each loose part off into a separate object.
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.separate(type='LOOSE')

    if create_closed_objects:
        # And then make each piece fully enclosed.
        return create_closed_shapes_from_pieces(ob, matchup_degenerates)
    else:
        return []


##
# Selects all edges that denote the boundaries of convex pieces.
#
# This is a multi-step process driven by heuristics:
#   1. First, we select all the sharp edges of the object, since sharp edges are
#      only co-planar with one of the faces they connect with and are therefore
#      unlikely to represent convex boundary edges.
#   2. Second, we select all edges that are similar in length to the sharp
#      edges, to catch any edges that are almost steep enough to be sharp edges.
#   3. Third, we invert the selection, which should (hopefully) cause all the
#      convex boundary edges we want to be selected.
#
def select_convex_boundary_edges(ob, max_edge_length_proportion=0.1):
    bpy.ops.object.mode_set(mode='EDIT')

    mesh = ob.data
    bm = bmesh.from_edit_mesh(mesh)

    # Enter "Edge" select mode
    bpy.context.tool_settings.mesh_select_mode = [False, True, False]

    # Find all sharp edges and edges of similar length
    bpy.ops.mesh.select_all(action='DESELECT')
    bpy.ops.mesh.edges_select_sharp()
    bpy.ops.mesh.select_similar(type='LENGTH', threshold=0.01)

    # Invert the selection to find the convex boundary edges.
    bpy.ops.mesh.select_all(action='INVERT')

    bm.faces.ensure_lookup_table()
    bm.edges.ensure_lookup_table()

    edges_to_select = []
    max_edge_length = max(ob.dimensions) * max_edge_length_proportion

    for selected_edge in [e for e in bm.edges if e.select]:
        edge_bridges =\
            find_shortest_edge_bridges(
                selected_edge,
                max_edge_length=max_edge_length
            )

        for path in edge_bridges.values():
            for edge in path:
                edges_to_select.append(edge)

    # Select the edges after we pick which edges we *want* to select, to ensure
    # that we only base our decisions on the initial convex boundary edges.
    for edge in edges_to_select:
        edge.select = True


##
# Locate the shortest path of edges to connect already-selected edges.
#
# This is used to find the additional edges that must be selected for a cut
# along a convex boundary to create a complete, closed object shape.
#
# The max edge length argument can be provided to avoid trying to find
# connections between convex boundaries that are very far apart in the same
# object.
#
def find_shortest_edge_bridges(starting_edge, max_edge_length=None):
    edge_bridges = find_bridge_edges(starting_edge, max_edge_length)
    sorted_edge_bridges = sorted(edge_bridges, key=lambda eb: eb[0])
    edge_solutions = {}

    for edge_bridge in sorted_edge_bridges:
        path_distance, final_edge, path = edge_bridge

        # Skip edges we've already found a min-length path to
        if final_edge not in edge_solutions.keys():
            edge_solutions[final_edge] = path

    print(f"Shortest edge bridges for starting edge '{str(starting_edge.index)}':")

    if len(edge_solutions) > 0:
        print(
            "  - " +
            "\n  - ".join(map(
                lambda i: str(
                    (i[0].index, str(list(map(lambda e: e.index, i[1]))))
                ),
                edge_solutions.items()
            )))
    print("")
    print("")

    return edge_solutions


##
# Performs a recursive, depth-first search from a selected edge to other edges.
#
# This returns all possible paths -- and distances of those paths -- to traverse
# the mesh from the starting, selected edge to another selected edge. To avoid
# a lengthy search, the max_depth parameter controls how many levels of edges
# are searched.
#
# The result is an array of tuples, where each tuple contains the total distance
# of the path, the already-selected edge that the path was able to reach, and
# the list of edges that would need to be selected in order to reach that
# destination edge.
#
def find_bridge_edges(edge, max_edge_length=None, max_depth=3, current_depth=0,
                      path_distance=0, edge_path=None, seen_verts=None):
    if edge_path is None:
        edge_path = []

    if seen_verts is None:
        seen_verts = []

    # Don't bother searching edges we've seen
    if edge in edge_path:
        return []

    if (current_depth > 0):
        first_edge = edge_path[0]
        edge_length = edge.calc_length()

        # Don't bother searching edges along the same normal as the first edge.
        # We want our cuts to be along convex boundaries that are perpendicular.
        if have_common_face(first_edge, edge):
            return []

        if edge.select:
            return [(path_distance, edge, edge_path)]

        # Disqualify edges that are too long.
        if max_edge_length is not None and edge_length > max_edge_length:
            print(
                f"Disqualifying edge {edge.index} because length [{edge_length}] > [{max_edge_length}"
            )

            return []

    if current_depth == max_depth:
        return []

    new_edge_path = edge_path + [edge]
    bridges = []

    for edge_vert in edge.verts:
        # Don't bother searching vertices we've already seen (no backtracking).
        if edge_vert in seen_verts:
            continue

        new_seen_verts = seen_verts + [edge_vert]

        for linked_edge in edge_vert.link_edges:
            # Don't bother searching selected edges connected to the starting
            # edge, since that gets us nowhere.
            if linked_edge.select and current_depth == 0:
                continue

            edge_length = linked_edge.calc_length()

            found_bridge_edges = find_bridge_edges(
                edge=linked_edge,
                max_edge_length=max_edge_length,
                max_depth=max_depth,
                current_depth=current_depth + 1,
                path_distance=path_distance + edge_length,
                edge_path=new_edge_path,
                seen_verts=new_seen_verts
            )

            bridges.extend(found_bridge_edges)

    return bridges


def create_closed_shapes_from_pieces(ob, matchup_degenerates=True,
                                     min_volume=0.1):
    print("Converting each piece into a closed object...")

    degenerate_piece_names = []

    for piece in name_duplicates_of(ob):
        if not make_piece_convex(piece):
            degenerate_piece_names.append(piece.name)

    degenerate_count = len(degenerate_piece_names)

    print("")
    print(f"Total degenerate (flat) pieces: {degenerate_count}")
    print("")

    eliminated_piece_names = []

    if matchup_degenerates:
        if degenerate_count > 10:
            # TODO: Hopefully, some day, find a good deterministic way to
            # automatically match up any number of degenerate pieces using a
            # heuristic that generates sane geometry.
            print(
                "There are too many degenerates for reliable auto-matching, so "
                "it will not be performed. You will need to manually combine "
                "degenerate pieces.")
            print("")
        else:
            eliminated_piece_names.extend(
                matchup_degenerate_pieces(degenerate_piece_names, min_volume)
            )

            eliminated_piece_names.extend(
                eliminate_tiny_pieces(degenerate_piece_names, min_volume)
            )

    return eliminated_piece_names


def matchup_degenerate_pieces(degenerate_piece_names, min_volume=0.1):
    pieces_eliminated = []
    degenerate_volumes = find_degenerate_combos(degenerate_piece_names)

    print("Searching for a way to match-up degenerates into volumes...")

    for piece1_name, piece1_volumes in degenerate_volumes.items():
        # Skip pieces already joined with degenerate pieces we've processed
        if piece1_name not in degenerate_piece_names:
            continue

        piece1 = bpy.data.objects[piece1_name]

        piece1_volumes_asc = dict(
            sorted(
                piece1_volumes.items(),
                key=operator.itemgetter(1)
            )
        )

        piece2 = None

        for piece2_name, combo_volume in piece1_volumes_asc.items():
            # Skip pieces that would make a volume that's too small, or that
            # have been joined with degenerate pieces we've processed
            if combo_volume < min_volume or piece2_name not in degenerate_piece_names:
                continue
            else:
                piece2 = bpy.data.objects[piece2_name]
                break

        if piece2 is not None:
            degenerate_piece_names.remove(piece2.name)
            pieces_eliminated.append(piece2.name)

            print(
                f"  - Combining parallel degenerate '{piece1.name}' with "
                f"'{piece2.name}' to form complete mesh '{piece1.name}'."
            )

            bpy.ops.object.mode_set(mode='OBJECT')
            bpy.ops.object.select_all(action='DESELECT')

            bpy.context.view_layer.objects.active = piece1

            piece1.select_set(True)
            piece2.select_set(True)

            bpy.ops.object.join()

            make_piece_convex(piece1)

    return pieces_eliminated


def find_degenerate_combos(degenerate_piece_names):
    volumes = {}

    for piece_combo in combinations(degenerate_piece_names, 2):
        piece1_name, piece2_name = piece_combo
        piece1 = bpy.data.objects[piece1_name]
        piece2 = bpy.data.objects[piece2_name]

        if not volumes.get(piece1_name):
            volumes[piece1_name] = {}

        piece1_mesh = piece1.data
        piece1_bm = bmesh.new()
        piece1_bm.from_mesh(piece1_mesh)

        piece2_mesh = piece2.data
        piece2_bm = bmesh.new()
        piece2_bm.from_mesh(piece2_mesh)

        piece1_bm.faces.ensure_lookup_table()
        piece2_bm.faces.ensure_lookup_table()

        if (len(piece1_bm.faces) == 0) or (len(piece2_bm.faces) == 0):
            continue

        piece1_face = piece1_bm.faces[0]
        piece2_face = piece2_bm.faces[0]

        combo_angle_radians = piece1_face.normal.angle(piece2_face.normal)
        combo_angle_degrees = int(round(degrees(combo_angle_radians)))

        # We only combine faces that are parallel to each other
        if combo_angle_degrees in [0, 180]:
            combo_volume = convex_volume(piece1, piece2)

            volumes[piece1.name][piece2.name] = combo_volume

    return volumes


def eliminate_tiny_pieces(degenerate_piece_names, min_volume=0.1):
    eliminated_piece_names = []

    tiny_piece_names = [
        n for n in degenerate_piece_names
        if n not in eliminated_piece_names
           and convex_volume(bpy.data.objects.get(n)) < min_volume
    ]

    print("")
    print(f"Total remaining tiny pieces: {len(tiny_piece_names)}")

    # Delete tiny pieces that are too small to be useful
    for tiny_piece_name in tiny_piece_names:
        print(f"  - Eliminating tiny piece '{tiny_piece_name}'...")

        tiny_piece = bpy.data.objects[tiny_piece_name]

        bpy.data.objects.remove(tiny_piece, do_unlink=True)
        eliminated_piece_names.append(tiny_piece_name)

    print("")

    return eliminated_piece_names


def make_piece_convex(ob, min_volume=0.1):
    print(
        f"  - Attempting to make '{ob.name}' into a closed, convex "
        f"shape."
    )

    volume_before = convex_volume(ob)

    make_convex_hull(ob)

    volume_after = convex_volume(ob)
    volume_delta = abs(volume_after - volume_before)

    # If the volume of the piece is very small when we tried making it convex,
    # then it's degenerate -- it's a plane or something flat that we need to
    # remove.
    is_degenerate = (volume_after < min_volume)

    print(f"    - Volume before: {volume_before}")
    print(f"    - Volume after: {volume_after}")
    print(f"    - Volume delta: {volume_delta}")
    print(f"    - Is degenerate: {is_degenerate}")

    return not is_degenerate


def make_convex_hull(ob):
    deselect_all_objects()

    bpy.context.view_layer.objects.active = ob
    ob.select_set(True)

    bpy.ops.object.mode_set(mode='EDIT')

    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.convex_hull()

    mesh = ob.data
    bm = bmesh.from_edit_mesh(mesh)

    # Clean-up unnecessary edges
    bmesh.ops.dissolve_limit(
        bm,
        angle_limit=radians(5),
        verts=bm.verts,
        edges=bm.edges,
    )

    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.ops.object.select_all(action='DESELECT')


def have_common_normal(e1, e2):
    e1_normals = map(lambda f: f.normal, e1.link_faces)
    e2_normals = map(lambda f: f.normal, e2.link_faces)

    common_normals = [n for n in e1_normals if n in e2_normals]

    return len(common_normals) > 0


def have_common_face(e1, e2):
    common_faces = [f for f in e1.link_faces if f in e2.link_faces]

    return len(common_faces) > 0


def convex_volume(*obs):
    meshes = []
    verts = []

    for ob in obs:
        mesh = ob.data
        bm = bmesh.new()

        bm.from_mesh(mesh)

        bm.verts.ensure_lookup_table()
        bm.edges.ensure_lookup_table()
        bm.faces.ensure_lookup_table()

        # Prevent early garbage collection.
        meshes.append(bm)

        geom = list(bm.verts) + list(bm.edges) + list(bm.faces)

        for g in geom:
            if hasattr(g, "verts"):
                verts.extend(v.co for v in g.verts)
            else:
                verts.append(g.co)

    return build_volume_from_verts(verts)


def build_volume_from_verts(verts):
    # Based on code from:
    # https://blender.stackexchange.com/questions/107357/how-to-find-if-geometry-linked-to-an-edge-is-coplanar
    origin = sum(verts, Vector((0, 0, 0))) / len(verts)
    bm = bmesh.new()

    for v in verts:
        bm.verts.new(v - origin)

    bmesh.ops.convex_hull(bm, input=bm.verts)

    return bm.calc_volume()


def deselect_all_objects():
    try:
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.select_all(action='DESELECT')
    except:
        pass


def rename_pieces(object_name, name_skiplist=None):
    if name_skiplist is None:
        name_skiplist = []

    for duplicate_name, old_index_str, new_index in dupe_name_sequence(object_name, name_skiplist):
        piece = bpy.data.objects.get(duplicate_name)

        if not piece:
            break

        old_name = piece.name
        new_name = re.sub(fr"(?:01)?\.{old_index_str}$", f"{new_index:02d}", piece.name)

        if old_name != new_name:
            print(f"Renaming piece '{old_name}' to '{new_name}'.")
            piece.name = new_name


def name_duplicates_of(ob):
    duplicates = []

    for duplicate_name, _, _ in dupe_name_sequence(ob.name):
        piece = bpy.data.objects.get(duplicate_name)

        if not piece:
            break
        else:
            duplicates.append(piece)

    return duplicates


def dupe_name_sequence(base_name, skiplist=None):
    if skiplist is None:
        skiplist = []

    yield base_name, "", 1

    new_index = 1

    for old_name_index in count(start=1):
        old_index_str = f"{old_name_index:03d}"
        duplicate_name = f"{base_name}.{old_index_str}"

        if duplicate_name in skiplist:
            continue
        else:
            new_index = new_index + 1

            yield duplicate_name, old_index_str, new_index



class PS_OT_fill_mesh(Operator):
    bl_idname = 'ps.fill_mesh'
    bl_label = 'Fill Mesh'
    bl_description = ''

    """ @classmethod
    def poll(cls, context):
        return context.mode == 'EDIT_MESH' """

    def execute(self, context):
        obj = context.active_object
        me = obj.data
        bm = bmesh.from_edit_mesh(me)
        #verts = [v for v in bm.verts if v.select]
        #edges = [e for e in bm.edges]
        #bmesh.ops.triangle_fill(bm, use_beauty=True, use_dissolve=False, edges=edges) #normal

        bm_new = bmesh.new()
        bm_new.from_mesh(me, face_normals=True, use_shape_key=False)
        verts = [v for v in bm_new.verts if v.select]
        convex_hull = bmesh.ops.convex_hull(bm_new, input=verts, use_existing_faces=True)
        
        bm_new.verts.ensure_lookup_table()
        bm_new.edges.ensure_lookup_table()
        bm_new.faces.ensure_lookup_table()

        vI, eI, fI = [], [], []
        for i in convex_hull['geom']: # geom, geom_interior, geom_unused, geom_holes
            if isinstance(i, bmesh.types.BMVert):
                vI.append(i)
            elif isinstance(i, bmesh.types.BMEdge):
                eI.append(i)
            elif isinstance(i, bmesh.types.BMFace):
                fI.append(i)

        for f_idx in fI:
            bm.faces.new([bm.verts[i.index] for i in f_idx.verts])
        # --- New
        #bm = bmesh.new()

        print(vI)        
        bmesh.update_edit_mesh(me)
        return {'FINISHED'}




classes = [
    PS_OT_fill_mesh,
]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)