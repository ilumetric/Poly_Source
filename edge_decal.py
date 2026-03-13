import bpy
import bmesh
from bpy.types import Operator
from bpy.props import FloatProperty, EnumProperty, IntProperty, StringProperty, BoolProperty
from mathutils import Vector
import random


class PS_OT_create_edge_decal(Operator):
    bl_idname = 'mesh.ps_create_edge_decal'
    bl_label = 'Edge Decal Tool'
    bl_description = 'Create a separate edge decal mesh from selected edges'
    bl_options = {'REGISTER', 'UNDO'}

    width: FloatProperty(
        name='Side Width',
        description='Width of the side faces from the selected edge loop',
        default=0.03,
        min=0.0001,
        soft_max=1.0,
    )
    offset: FloatProperty(
        name='Offset',
        description='Offset along polygon normals',
        default=0.001,
        soft_min=0.0,
        soft_max=0.1,
        precision=6,
        step=1,
    )
    uv_orientation: EnumProperty(
        name='UV Orientation',
        description='Trim orientation on the texture atlas',
        items=[
            ('VERTICAL', 'Vertical', 'Use vertical trims (default)'),
            ('HORIZONTAL', 'Horizontal', 'Use horizontal trims'),
        ],
        default='VERTICAL',
    )
    uv_trim_count: IntProperty(
        name='Trim Count',
        description='How many equal trims texture is divided into',
        default=4,
        min=1,
        soft_max=32,
    )
    uv_trim_index: IntProperty(
        name='Trim Index',
        description='Target trim slot index (1-based)',
        default=1,
        min=1,
        soft_max=32,
    )
    uv_scale: FloatProperty(
        name='UV Scale',
        description='Uniform UV scale around trim center',
        default=1.0,
        min=0.0001,
        soft_max=4.0,
    )
    uv_split_flaps: BoolProperty(
        name='Split UV Flaps',
        description='Keep center seam shared; map side flaps proportionally to mesh shape (paper-craft style)',
        default=False,
    )
    uv_random_shift: FloatProperty(
        name='UV Random Shift',
        description='Random offset along the main UV axis per group (0 = no shift)',
        default=0.0,
        min=0.0,
        soft_max=1.0,
    )
    uv_random_seed: IntProperty(
        name='Random Seed',
        description='Seed for random UV shift',
        default=0,
        min=0,
        soft_max=9999,
    )
    material_name: StringProperty(
        name='Material',
        description='Optional material to assign to generated edge decal',
        default='',
    )
    conform_to_face: BoolProperty(
        name='Conform to Face',
        description='Project decal flaps onto adjacent face planes so they follow geometry at sharp corners',
        default=False,
    )

    @classmethod
    def poll(cls, context):
        ob = context.active_object
        return ob is not None and ob.type == 'MESH' and context.mode == 'EDIT_MESH'

    def draw(self, context):
        layout = self.layout
        layout.prop(self, 'width')
        layout.prop(self, 'offset')
        layout.prop(self, 'conform_to_face')

        box = layout.box()
        box.label(text='UV Trims')
        box.prop(self, 'uv_orientation')
        box.prop(self, 'uv_trim_count')
        box.prop(self, 'uv_trim_index')
        box.prop(self, 'uv_scale')
        box.prop(self, 'uv_split_flaps')
        box.prop(self, 'uv_random_shift')
        box.prop(self, 'uv_random_seed')

        layout.separator()
        layout.prop_search(self, 'material_name', bpy.data, 'materials', text='Material')

    def _calc_inset_direction(self, face, edge):
        v0, v1 = edge.verts
        edge_vec = v1.co - v0.co
        if edge_vec.length < 1e-9:
            return None

        side = face.normal.cross(edge_vec)
        if side.length < 1e-9:
            return None

        edge_mid = (v0.co + v1.co) * 0.5
        to_center = face.calc_center_median() - edge_mid
        if to_center.dot(side) < 0.0:
            side.negate()

        side.normalize()
        return side

    def _calc_corner_point(self, vert, vectors):
        if not vectors:
            return vert.co.copy()

        if len(vectors) == 1:
            return vert.co + vectors[0] * self.width

        base = vectors[0].normalized()
        acc = Vector((0.0, 0.0, 0.0))
        aligned = []

        for vec in vectors:
            current = vec.normalized()
            if current.dot(base) < 0.0:
                current.negate()
            aligned.append(current)
            acc += current

        if acc.length < 1e-9:
            return vert.co + base * self.width

        miter = acc.normalized()
        dot_values = [miter.dot(vec) for vec in aligned]
        safe_dot = max(0.15, min(dot_values))
        miter_scale = self.width / safe_dot
        return vert.co + miter * miter_scale

    def _calc_vert_even_offset(self, vert):
        """Even offset like Shrink/Fatten + Offset Even.
        Uses vertex normal with angle-weighted 1/cos correction from all adjacent faces."""
        if abs(self.offset) < 1e-10:
            return Vector((0.0, 0.0, 0.0))

        n = vert.normal.copy()
        if n.length < 1e-9:
            return Vector((0.0, 0.0, 0.0))
        n.normalize()

        if not vert.link_faces:
            return n * self.offset

        total_angle = 0.0
        weighted_dot = 0.0

        for loop in vert.link_loops:
            angle = loop.calc_angle()
            if angle > 1e-9:
                dot = max(n.dot(loop.face.normal), 0.01)
                weighted_dot += angle * dot
                total_angle += angle

        if total_angle < 1e-9:
            return n * self.offset

        avg_dot = max(weighted_dot / total_angle, 0.1)
        return n * (self.offset / avg_dot)

    def _calc_slide_direction(self, face, edge, vert):
        """Return the direction along the adjacent face edge from vert, skipping the selected edge."""
        for fe in face.edges:
            if fe == edge:
                continue
            if vert in fe.verts:
                other_v = fe.other_vert(vert)
                direction = other_v.co - vert.co
                if direction.length < 1e-9:
                    return None
                direction.normalize()
                return direction
        return None

    def _ordered_path_from_edges(self, selected_edges):
        vert_edges = {}
        for edge in selected_edges:
            a = edge.verts[0].index
            b = edge.verts[1].index
            vert_edges.setdefault(a, []).append(edge)
            vert_edges.setdefault(b, []).append(edge)

        endpoints = [vid for vid, edges in vert_edges.items() if len(edges) == 1]
        if endpoints:
            start_vert = endpoints[0]
        else:
            start_vert = selected_edges[0].verts[0].index

        ordered_verts = [start_vert]
        ordered_edges = []
        used_edges = set()
        current_vid = start_vert

        while True:
            linked = vert_edges.get(current_vid, [])
            next_edge = None
            for edge in linked:
                if edge not in used_edges:
                    next_edge = edge
                    break

            if next_edge is None:
                break

            used_edges.add(next_edge)
            ordered_edges.append(next_edge)
            a = next_edge.verts[0].index
            b = next_edge.verts[1].index
            next_vid = b if a == current_vid else a
            ordered_verts.append(next_vid)
            current_vid = next_vid

            if current_vid == start_vert and len(used_edges) == len(selected_edges):
                break

        if len(ordered_edges) != len(selected_edges):
            return None, None

        return ordered_verts, ordered_edges

    def _build_vertex_distances(self, bm, ordered_verts):
        if not ordered_verts or len(ordered_verts) < 2:
            return {vid: 0.0 for vid in ordered_verts}, 0.0

        cumulative = [0.0]
        total = 0.0
        for i in range(len(ordered_verts) - 1):
            v0 = bm.verts[ordered_verts[i]].co
            v1 = bm.verts[ordered_verts[i + 1]].co
            total += (v1 - v0).length
            cumulative.append(total)

        dist_values = {}
        for i, vid in enumerate(ordered_verts):
            if vid not in dist_values:
                dist_values[vid] = cumulative[i]

        return dist_values, total

    def _assign_edge_sides(self, ordered_edges, selected_edge_set):
        """Assign consistent side_0 / side_1 face along the ordered edge loop."""
        edge_side = {}  # edge -> (side0_face, side1_face)
        if not ordered_edges:
            return edge_side

        e0 = ordered_edges[0]
        edge_side[e0] = (e0.link_faces[0], e0.link_faces[1])

        for i in range(1, len(ordered_edges)):
            prev = ordered_edges[i - 1]
            curr = ordered_edges[i]
            prev_s0 = edge_side[prev][0]

            cf = list(curr.link_faces)

            # try direct face sharing (common case for edge loops on quads)
            if prev_s0 in cf:
                other = cf[1] if cf[0] == prev_s0 else cf[0]
                edge_side[curr] = (prev_s0, other)
                continue

            # fan-walk at shared vertex to find which face of curr is on same side
            shared = set(prev.verts) & set(curr.verts)
            if not shared:
                edge_side[curr] = (cf[0], cf[1])
                continue

            sv = shared.pop()
            visited = {prev_s0}
            queue = [prev_s0]
            found = None

            while queue and found is None:
                f = queue.pop(0)
                for e in f.edges:
                    if e in selected_edge_set or sv not in e.verts:
                        continue
                    for nf in e.link_faces:
                        if nf in visited:
                            continue
                        if nf in cf:
                            found = nf
                            break
                        visited.add(nf)
                        queue.append(nf)
                    if found:
                        break

            if found is not None:
                other = cf[1] if cf[0] == found else cf[0]
                edge_side[curr] = (found, other)
            else:
                edge_side[curr] = (cf[0], cf[1])

        return edge_side

    def _assign_trim_uv(self, bm_new, src_vert_layer, vert_kind_layer, face_side_layer, vertex_distance, total_length, faces=None, along_offset=0.0):
        uv_layer = bm_new.loops.layers.uv.get("UVMap") or bm_new.loops.layers.uv.new("UVMap")

        trim_count = max(1, self.uv_trim_count)
        trim_index = max(1, min(self.uv_trim_index, trim_count)) - 1
        trim_size = 1.0 / trim_count
        trim_min = trim_index * trim_size

        center_trim = (trim_min + trim_size * 0.5)
        strip_world_width = max(2.0 * self.width, 1e-9)
        uv_per_meter = trim_size / strip_world_width

        # align to bottom of UV quad; scale around bottom-center
        base_along = along_offset

        target_faces = faces if faces is not None else bm_new.faces

        if self.uv_split_flaps:
            # ---- Paper-craft unfold: per-face projection onto base edge ----
            for face in target_faces:
                side = int(face[face_side_layer])
                outer_loops = []
                inner_loops = []
                for loop in face.loops:
                    if int(loop.vert[vert_kind_layer]) == 0:
                        outer_loops.append(loop)
                    else:
                        inner_loops.append(loop)

                if len(outer_loops) != 2 or len(inner_loops) != 2:
                    continue

                # sort outer loops so o0 has smaller along-distance
                outer_loops.sort(key=lambda l: vertex_distance.get(int(l.vert[src_vert_layer]), 0.0))
                o0_loop, o1_loop = outer_loops

                o0_3d = o0_loop.vert.co
                o1_3d = o1_loop.vert.co
                o0_along = vertex_distance.get(int(o0_loop.vert[src_vert_layer]), 0.0) * uv_per_meter
                o1_along = vertex_distance.get(int(o1_loop.vert[src_vert_layer]), 0.0) * uv_per_meter

                base_vec = o1_3d - o0_3d
                base_len = base_vec.length
                base_dir = base_vec / base_len if base_len > 1e-9 else Vector((0, 0, 1))

                # place outer verts on the center line
                for ol in (o0_loop, o1_loop):
                    a_uv = vertex_distance.get(int(ol.vert[src_vert_layer]), 0.0) * uv_per_meter
                    a_scaled = base_along + a_uv * self.uv_scale
                    if self.uv_orientation == 'VERTICAL':
                        ol[uv_layer].uv = (center_trim, a_scaled)
                    else:
                        ol[uv_layer].uv = (a_scaled, center_trim)

                # unfold each inner vert: project onto base edge
                for il in inner_loops:
                    i_3d = il.vert.co
                    v = i_3d - o0_3d
                    along_proj = v.dot(base_dir)
                    perp = v - along_proj * base_dir
                    across_proj = perp.length

                    t = along_proj / base_len if base_len > 1e-9 else 0.0
                    inner_along_uv = o0_along + t * (o1_along - o0_along)
                    inner_across_uv = across_proj * uv_per_meter

                    if side == 0:
                        band = center_trim - inner_across_uv
                    else:
                        band = center_trim + inner_across_uv

                    a_scaled = base_along + inner_along_uv * self.uv_scale
                    b_scaled = center_trim + (band - center_trim) * self.uv_scale

                    if self.uv_orientation == 'VERTICAL':
                        il[uv_layer].uv = (b_scaled, a_scaled)
                    else:
                        il[uv_layer].uv = (a_scaled, b_scaled)
        else:
            # ---- Ribbon mode: flat strip UV ----
            for face in target_faces:
                side = int(face[face_side_layer])
                for loop in face.loops:
                    src_index = int(loop.vert[src_vert_layer])
                    kind = int(loop.vert[vert_kind_layer])
                    along_raw = vertex_distance.get(src_index, 0.0) * uv_per_meter

                    if side == 0:
                        across = 0.5 if kind == 0 else 0.0
                    else:
                        across = 0.5 if kind == 0 else 1.0
                    band_value = trim_min + across * trim_size

                    if self.uv_orientation == 'VERTICAL':
                        u = center_trim + (band_value - center_trim) * self.uv_scale
                        v = base_along + along_raw * self.uv_scale
                    else:
                        u = base_along + along_raw * self.uv_scale
                        v = center_trim + (band_value - center_trim) * self.uv_scale

                    loop[uv_layer].uv = (u, v)

    def _split_into_connected_groups(self, selected_edges):
        """Split selected edges into connected groups (edge chains/loops)."""
        remaining = set(selected_edges)
        groups = []

        while remaining:
            seed = next(iter(remaining))
            group = []
            queue = [seed]
            remaining.discard(seed)

            while queue:
                edge = queue.pop()
                group.append(edge)
                for vert in edge.verts:
                    for linked in vert.link_edges:
                        if linked in remaining:
                            remaining.discard(linked)
                            queue.append(linked)

            groups.append(group)

        return groups

    def _split_faces_into_connected_groups(self, selected_faces):
        """Split selected faces into connected groups by shared edges."""
        remaining = set(selected_faces)
        groups = []

        while remaining:
            seed = next(iter(remaining))
            group = []
            queue = [seed]
            remaining.discard(seed)

            while queue:
                face = queue.pop()
                group.append(face)
                for edge in face.edges:
                    for linked_face in edge.link_faces:
                        if linked_face in remaining:
                            remaining.discard(linked_face)
                            queue.append(linked_face)

            groups.append(group)

        return groups

    def _build_poly_strip(self, group_faces):
        """Build ordered poly strip with two rail edge chains for poly-loop decal.

        The selected quad faces form a strip (e.g. a bevel).  The two border
        edge chains ("rails") run along the strip on opposite sides.  The
        decal flaps will extend outward from these rails into the
        neighbouring non-selected faces.
        """
        face_set = set(group_faces)

        # Only quads supported
        if not all(len(f.verts) == 4 for f in group_faces):
            return None

        # Classify edges per face: shared with another selected face (cross)
        # or unshared (rail / end-cap).
        face_cross = {}
        for face in group_faces:
            cross = []
            for edge in face.edges:
                if any(f != face and f in face_set for f in edge.link_faces):
                    cross.append(edge)
            face_cross[face] = cross

        # Build face adjacency via shared (cross) edges
        face_neighbors = {f: [] for f in group_faces}
        seen_pairs = set()
        for face in group_faces:
            for edge in face_cross[face]:
                for f in edge.link_faces:
                    if f != face and f in face_set:
                        pair = (id(face), id(f))
                        rpair = (id(f), id(face))
                        if pair not in seen_pairs and rpair not in seen_pairs:
                            face_neighbors[face].append((f, edge))
                            face_neighbors[f].append((face, edge))
                            seen_pairs.add(pair)

        # No branching allowed
        if any(len(nbrs) > 2 for nbrs in face_neighbors.values()):
            return None

        endpoints = [f for f, nbrs in face_neighbors.items() if len(nbrs) <= 1]

        # Single face – no cross edges, treat as open strip of length 1
        if len(group_faces) == 1:
            is_closed = False
            endpoints = [group_faces[0]]
        else:
            is_closed = len(endpoints) == 0
            if not is_closed and len(endpoints) != 2:
                return None

        start = group_faces[0] if is_closed else endpoints[0]

        # Walk the strip in order
        ordered = [start]
        visited = {start}
        cross_edges_seq = []
        current = start

        while True:
            nbrs = [(f, e) for f, e in face_neighbors[current] if f not in visited]
            if not nbrs:
                if is_closed and len(ordered) == len(group_faces):
                    for f, e in face_neighbors[current]:
                        if f == start:
                            cross_edges_seq.append(e)
                            break
                break
            next_face, ce = nbrs[0]
            cross_edges_seq.append(ce)
            ordered.append(next_face)
            visited.add(next_face)
            current = next_face

        if len(ordered) != len(group_faces):
            return None

        cross_edge_set = set()
        for edges in face_cross.values():
            cross_edge_set.update(edges)

        # For each face determine the two rail edges
        face_rails = {}
        for i, face in enumerate(ordered):
            loops = list(face.loops)
            edges = [l.edge for l in loops]
            cross_in_face = [e for e in edges if e in cross_edge_set]
            non_cross = [e for e in edges if e not in cross_edge_set]

            if len(cross_in_face) == 2:
                if len(non_cross) != 2:
                    return None
                face_rails[face] = non_cross
            elif len(cross_in_face) == 1:
                cross_e = cross_in_face[0]
                cross_idx = edges.index(cross_e)
                opposite_e = edges[(cross_idx + 2) % 4]
                rails = [e for e in non_cross if e != opposite_e]
                if len(rails) != 2:
                    return None
                face_rails[face] = rails
            elif len(cross_in_face) == 0:
                len02 = (edges[0].calc_length() + edges[2].calc_length()) * 0.5
                len13 = (edges[1].calc_length() + edges[3].calc_length()) * 0.5
                if len02 >= len13:
                    face_rails[face] = [edges[0], edges[2]]
                else:
                    face_rails[face] = [edges[1], edges[3]]
            else:
                return None

        # Assign consistent side 0 / side 1 across the strip
        first_face = ordered[0]
        r0, r1 = face_rails[first_face]
        face_sides = {first_face: {0: r0, 1: r1}}

        for i in range(1, len(ordered)):
            face = ordered[i]
            r_a, r_b = face_rails[face]
            prev_side0 = face_sides[ordered[i - 1]][0]
            prev_s0_verts = set(prev_side0.verts)

            if prev_s0_verts & set(r_a.verts):
                face_sides[face] = {0: r_a, 1: r_b}
            elif prev_s0_verts & set(r_b.verts):
                face_sides[face] = {0: r_b, 1: r_a}
            else:
                face_sides[face] = {0: r_a, 1: r_b}

        # Build ordered vert-index chains along each rail
        def build_rail_chain(side_idx):
            chain_verts = []
            chain_edges = []

            for i, face in enumerate(ordered):
                rail_edge = face_sides[face][side_idx]
                v0, v1 = rail_edge.verts

                if not chain_verts:
                    if len(ordered) > 1:
                        cross_verts = set(cross_edges_seq[0].verts)
                        if v0 in cross_verts and v1 not in cross_verts:
                            chain_verts.extend([v1.index, v0.index])
                        elif v1 in cross_verts and v0 not in cross_verts:
                            chain_verts.extend([v0.index, v1.index])
                        else:
                            chain_verts.extend([v0.index, v1.index])
                    else:
                        chain_verts.extend([v0.index, v1.index])
                    chain_edges.append(rail_edge)
                else:
                    last_vid = chain_verts[-1]
                    if v0.index == last_vid:
                        chain_verts.append(v1.index)
                    elif v1.index == last_vid:
                        chain_verts.append(v0.index)
                    else:
                        return None, None
                    chain_edges.append(rail_edge)

            return chain_verts, chain_edges

        rail_0_verts, rail_0_edges = build_rail_chain(0)
        rail_1_verts, rail_1_edges = build_rail_chain(1)

        if rail_0_verts is None or rail_1_verts is None:
            return None

        # For single-face strips there are no cross-edges to orient
        # the two rail chains consistently.  Ensure start verts of
        # both rails share a face edge (= same geometric end).
        if len(ordered) == 1 and rail_0_verts and rail_1_verts:
            r0s, r1s = rail_0_verts[0], rail_1_verts[0]
            shares_edge = any(
                r0s in {v.index for v in e.verts} and
                r1s in {v.index for v in e.verts}
                for e in ordered[0].edges
            )
            if not shares_edge:
                rail_1_verts.reverse()

        return {
            'ordered_faces': ordered,
            'face_sides': face_sides,
            'rail_0_verts': rail_0_verts,
            'rail_0_edges': rail_0_edges,
            'rail_1_verts': rail_1_verts,
            'rail_1_edges': rail_1_edges,
            'is_closed': is_closed,
        }

    def execute(self, context):
        obj = context.active_object
        if obj is None or obj.type != 'MESH' or context.mode != 'EDIT_MESH':
            self.report({'WARNING'}, 'Run in Edit Mode on a mesh object')
            return {'CANCELLED'}

        # Cache the source object's transform via stored properties.
        # matrix_world is a computed value that can be stale after an
        # undo (which Blender performs before every operator redo),
        # so we read the raw location/rotation/scale instead.
        source_loc = obj.location.copy()
        source_rot_mode = obj.rotation_mode
        source_rot_euler = obj.rotation_euler.copy()
        source_rot_quat = obj.rotation_quaternion.copy()
        source_scale = obj.scale.copy()

        obj.update_from_editmode()

        bm = bmesh.from_edit_mesh(obj.data)
        bm.verts.ensure_lookup_table()
        bm.edges.ensure_lookup_table()
        bm.faces.ensure_lookup_table()

        selected_edges = [edge for edge in bm.edges if edge.select]
        selected_faces = [face for face in bm.faces if face.select]

        select_mode = context.tool_settings.mesh_select_mode
        prefer_poly_mode = bool(select_mode[2] and selected_faces)

        if prefer_poly_mode:
            mode = 'POLY'
        elif selected_edges:
            mode = 'EDGE'
        elif selected_faces:
            mode = 'POLY'
        else:
            self.report({'WARNING'}, 'No edges or polygons selected')
            return {'CANCELLED'}

        # split selection into connected groups
        if mode == 'EDGE':
            bad_edges = [edge for edge in selected_edges if len(edge.link_faces) != 2]
            if bad_edges:
                self.report({'WARNING'}, 'All selected edges must have polygons on both sides')
                return {'CANCELLED'}
            edge_groups = self._split_into_connected_groups(selected_edges)
            face_groups = []
        else:
            edge_groups = []
            face_groups = self._split_faces_into_connected_groups(selected_faces)

        # shared output bmesh for ALL groups
        bm_new = bmesh.new()
        src_vert_layer = bm_new.verts.layers.int.new('ps_src_vert')
        vert_kind_layer = bm_new.verts.layers.int.new('ps_kind')
        face_side_layer = bm_new.faces.layers.int.new('ps_side')

        all_selected_edge_keys = set()
        total_created_faces = 0
        skipped_groups = 0

        if mode == 'EDGE':
            for group_idx, group_edges in enumerate(edge_groups):
                group_edge_set = set(group_edges)
                group_face_count = 0

                # check for branching within this group
                has_branching = False
                group_verts = {v for e in group_edges for v in e.verts}
                for vert in group_verts:
                    connected = sum(1 for e in vert.link_edges if e in group_edge_set)
                    if connected > 2:
                        has_branching = True
                        break
                if has_branching:
                    skipped_groups += 1
                    continue

                ordered_verts, ordered_edges = self._ordered_path_from_edges(group_edges)
                if ordered_verts is None:
                    skipped_groups += 1
                    continue

                vertex_distance, total_length = self._build_vertex_distances(bm, ordered_verts)
                edge_side = self._assign_edge_sides(ordered_edges, group_edge_set)

                # collect selected edge keys for sharp marking
                for edge in group_edges:
                    a = edge.verts[0].index
                    b = edge.verts[1].index
                    if a > b:
                        a, b = b, a
                    all_selected_edge_keys.add((a, b))

                # collect inset directions per (side, vert_index)
                corner_dirs = {}
                for edge in group_edges:
                    s0_face, s1_face = edge_side[edge]
                    for face in edge.link_faces:
                        side_idx = 0 if face == s0_face else 1
                        if self.conform_to_face:
                            for vert in edge.verts:
                                direction = self._calc_slide_direction(face, edge, vert)
                                if direction is None:
                                    continue
                                key = (side_idx, vert.index)
                                corner_dirs.setdefault(key, []).append(direction)
                        else:
                            inset = self._calc_inset_direction(face, edge)
                            if inset is None:
                                continue
                            for vert in edge.verts:
                                key = (side_idx, vert.index)
                                corner_dirs.setdefault(key, []).append(inset.copy())

                if not corner_dirs:
                    skipped_groups += 1
                    continue

                # inner positions
                inner_positions = {}
                for key, vectors in corner_dirs.items():
                    _side, vert_index = key
                    vert = bm.verts[vert_index]
                    inner_positions[key] = self._calc_corner_point(vert, vectors)

                # even offset per source vertex
                vert_displacement = {}
                for vert_index in set(vi for (_, vi) in corner_dirs.keys()):
                    vert_displacement[vert_index] = self._calc_vert_even_offset(bm.verts[vert_index])

                # at open-loop endpoints, remove edge-tangent component
                is_closed = ordered_verts[0] == ordered_verts[-1]
                if not is_closed and len(ordered_verts) >= 2:
                    v0 = bm.verts[ordered_verts[0]]
                    v1 = bm.verts[ordered_verts[1]]
                    t_out_0 = (v0.co - v1.co).normalized()

                    vn = bm.verts[ordered_verts[-1]]
                    vn1 = bm.verts[ordered_verts[-2]]
                    t_out_n = (vn.co - vn1.co).normalized()

                    for vert_index, t_out in [(ordered_verts[0], t_out_0),
                                               (ordered_verts[-1], t_out_n)]:
                        if vert_index in vert_displacement:
                            disp = vert_displacement[vert_index]
                            disp = disp - disp.dot(t_out) * t_out
                            vert_displacement[vert_index] = disp

                # --- build geometry for this group into shared bm_new ---
                # each group gets its own outer/inner vert maps (no sharing across groups)
                outer_verts = {}
                inner_verts_map = {}

                def get_outer(vert):
                    if vert.index in outer_verts:
                        return outer_verts[vert.index]
                    new_v = bm_new.verts.new(vert.co)
                    new_v[src_vert_layer] = int(vert.index)
                    new_v[vert_kind_layer] = 0
                    outer_verts[vert.index] = new_v
                    return new_v

                def get_inner(side_idx, vert):
                    key = (side_idx, vert.index)
                    if key in inner_verts_map:
                        return inner_verts_map[key]
                    pos = inner_positions[key]
                    new_v = bm_new.verts.new(pos)
                    new_v[src_vert_layer] = int(vert.index)
                    new_v[vert_kind_layer] = 1
                    inner_verts_map[key] = new_v
                    return new_v

                for edge in group_edges:
                    v0, v1 = edge.verts
                    s0_face, s1_face = edge_side[edge]

                    for face in edge.link_faces:
                        side_idx = 0 if face == s0_face else 1
                        i0_key = (side_idx, v0.index)
                        i1_key = (side_idx, v1.index)
                        if i0_key not in inner_positions or i1_key not in inner_positions:
                            continue
                        o0 = get_outer(v0)
                        o1 = get_outer(v1)
                        i0 = get_inner(side_idx, v0)
                        i1 = get_inner(side_idx, v1)

                        test_normal = (o1.co - o0.co).cross(i1.co - o0.co)
                        if test_normal.dot(face.normal) >= 0.0:
                            loop = (o0, o1, i1, i0)
                        else:
                            loop = (o1, o0, i0, i1)

                        try:
                            new_face = bm_new.faces.new(loop)
                            new_face[face_side_layer] = int(side_idx)
                            new_face.smooth = True
                            total_created_faces += 1
                            group_face_count += 1
                        except ValueError:
                            continue

                # apply offset for this group
                if self.offset != 0.0:
                    for vert_index, new_v in outer_verts.items():
                        new_v.co += vert_displacement.get(vert_index, Vector((0, 0, 0)))
                    for key, new_v in inner_verts_map.items():
                        _, src_index = key
                        new_v.co += vert_displacement.get(src_index, Vector((0, 0, 0)))

                # collect faces created by this group for UV assignment
                bm_new.verts.ensure_lookup_table()
                bm_new.edges.ensure_lookup_table()
                bm_new.faces.ensure_lookup_table()

                group_faces_new = list(bm_new.faces)[-group_face_count:] if group_face_count > 0 else []

                if self.uv_random_shift > 0:
                    rng = random.Random(self.uv_random_seed + group_idx)
                    along_offset = rng.uniform(0, self.uv_random_shift)
                else:
                    along_offset = 0.0

                self._assign_trim_uv(
                    bm_new,
                    src_vert_layer,
                    vert_kind_layer,
                    face_side_layer,
                    vertex_distance,
                    total_length,
                    faces=group_faces_new,
                    along_offset=along_offset,
                )
        else:
            # ---- POLY-LOOP MODE ----
            # Selected quad-face strip (e.g. bevel): duplicate the strip
            # as the center part and grow side flaps outward from each
            # border rail into neighbouring non-selected faces.
            for group_idx, group_faces in enumerate(face_groups):
                strip = self._build_poly_strip(group_faces)
                if strip is None:
                    skipped_groups += 1
                    continue

                face_set = set(group_faces)
                ordered_faces = strip['ordered_faces']
                face_sides_map = strip['face_sides']

                rail_0_verts = strip['rail_0_verts']
                rail_1_verts = strip['rail_1_verts']
                rail_0_edges = strip['rail_0_edges']
                rail_1_edges = strip['rail_1_edges']

                # Rail membership per vert index
                rail_membership = {}
                for vi in rail_0_verts:
                    rail_membership[vi] = 0
                for vi in rail_1_verts:
                    rail_membership[vi] = 1

                # Along-distance for each rail
                vd_r0, tl_r0 = self._build_vertex_distances(bm, rail_0_verts)
                vd_r1, tl_r1 = self._build_vertex_distances(bm, rail_1_verts)

                total_length = max(tl_r0, tl_r1)

                # Build a unified along-distance map.
                # For rail_0 verts use their own distance; for rail_1 verts
                # project each vert onto the corresponding position along
                # rail_0 so that cross-edge partners get the same along-value.
                vertex_distance = dict(vd_r0)

                # Build cross-edge pairing: for each face the two rail verts
                # on opposite sides should share the same along-distance.
                r0_set = set(rail_0_verts)
                r1_set = set(rail_1_verts)
                r1_to_r0_along = {}
                for face in ordered_faces:
                    face_verts = [v.index for v in face.verts]
                    fv_r0 = [vi for vi in face_verts if vi in r0_set]
                    fv_r1 = [vi for vi in face_verts if vi in r1_set]
                    if len(fv_r0) == 2 and len(fv_r1) == 2:
                        # pair by matching along-order within face
                        fv_r0.sort(key=lambda vi: vd_r0.get(vi, 0.0))
                        fv_r1.sort(key=lambda vi: vd_r1.get(vi, 0.0))
                        for r0v, r1v in zip(fv_r0, fv_r1):
                            r1_to_r0_along[r1v] = vd_r0.get(r0v, 0.0)

                for vi in rail_1_verts:
                    if vi not in vertex_distance:
                        if vi in r1_to_r0_along:
                            vertex_distance[vi] = r1_to_r0_along[vi]
                        else:
                            # fallback: scale proportionally
                            scale = (tl_r0 / tl_r1) if tl_r1 > 1e-9 else 1.0
                            vertex_distance[vi] = vd_r1.get(vi, 0.0) * scale

                # Measure average strip cross-width for UV layout
                cross_widths = []
                for face in ordered_faces:
                    r0e = face_sides_map[face][0]
                    r1e = face_sides_map[face][1]
                    m0 = (r0e.verts[0].co + r0e.verts[1].co) * 0.5
                    m1 = (r1e.verts[0].co + r1e.verts[1].co) * 0.5
                    cross_widths.append((m1 - m0).length)
                avg_strip_width = sum(cross_widths) / len(cross_widths) if cross_widths else 0.01
                total_decal_width = max(2.0 * self.width + avg_strip_width, 1e-9)

                # --- Create shared vert map for center strip ---
                strip_vert_map = {}
                for face in ordered_faces:
                    for vert in face.verts:
                        if vert.index not in strip_vert_map:
                            new_v = bm_new.verts.new(vert.co)
                            new_v[src_vert_layer] = int(vert.index)
                            new_v[vert_kind_layer] = 0
                            strip_vert_map[vert.index] = new_v

                group_new_faces = []

                # --- Center strip faces ---
                for face in ordered_faces:
                    face_loop_verts = [strip_vert_map[v.index] for v in face.verts]
                    try:
                        new_face = bm_new.faces.new(face_loop_verts)
                        new_face[face_side_layer] = 2  # center
                        new_face.smooth = True
                        total_created_faces += 1
                        group_new_faces.append(new_face)
                    except ValueError:
                        continue

                # --- Side flaps for each rail ---
                all_inner_verts = {}

                for side_idx, rail_verts_ids, rail_edges_list in [
                    (0, rail_0_verts, rail_0_edges),
                    (1, rail_1_verts, rail_1_edges),
                ]:
                    corner_dirs = {}
                    for rail_edge in rail_edges_list:
                        outer_face = None
                        for f in rail_edge.link_faces:
                            if f not in face_set:
                                outer_face = f
                                break
                        if outer_face is None:
                            continue
                        if self.conform_to_face:
                            for vert in rail_edge.verts:
                                direction = self._calc_slide_direction(outer_face, rail_edge, vert)
                                if direction is None:
                                    continue
                                key = (side_idx, vert.index)
                                corner_dirs.setdefault(key, []).append(direction)
                        else:
                            inset = self._calc_inset_direction(outer_face, rail_edge)
                            if inset is None:
                                continue
                            for vert in rail_edge.verts:
                                key = (side_idx, vert.index)
                                corner_dirs.setdefault(key, []).append(inset.copy())

                    if not corner_dirs:
                        continue

                    inner_positions = {}
                    for key, vectors in corner_dirs.items():
                        _side, vert_index = key
                        vert = bm.verts[vert_index]
                        inner_positions[key] = self._calc_corner_point(vert, vectors)

                    inner_verts_map = {}
                    for key, pos in inner_positions.items():
                        _side, vert_index = key
                        new_v = bm_new.verts.new(pos)
                        new_v[src_vert_layer] = int(vert_index)
                        new_v[vert_kind_layer] = 1
                        inner_verts_map[key] = new_v
                        all_inner_verts[key] = new_v

                    for rail_edge in rail_edges_list:
                        outer_face = None
                        for f in rail_edge.link_faces:
                            if f not in face_set:
                                outer_face = f
                                break
                        if outer_face is None:
                            continue

                        v0, v1 = rail_edge.verts
                        o0 = strip_vert_map[v0.index]
                        o1 = strip_vert_map[v1.index]
                        i0_key = (side_idx, v0.index)
                        i1_key = (side_idx, v1.index)
                        if i0_key not in inner_verts_map or i1_key not in inner_verts_map:
                            continue
                        i0 = inner_verts_map[i0_key]
                        i1 = inner_verts_map[i1_key]

                        test_normal = (o1.co - o0.co).cross(i1.co - o0.co)
                        if test_normal.dot(outer_face.normal) >= 0.0:
                            loop = (o0, o1, i1, i0)
                        else:
                            loop = (o1, o0, i0, i1)

                        try:
                            new_face = bm_new.faces.new(loop)
                            new_face[face_side_layer] = int(side_idx)
                            new_face.smooth = True
                            total_created_faces += 1
                            group_new_faces.append(new_face)
                        except ValueError:
                            continue

                    # Rail edge keys for sharp marking
                    for rail_edge in rail_edges_list:
                        a = rail_edge.verts[0].index
                        b = rail_edge.verts[1].index
                        if a > b:
                            a, b = b, a
                        all_selected_edge_keys.add((a, b))

                # --- Apply offset ---
                if self.offset != 0.0:
                    offset_cache = {}
                    for vert_index in strip_vert_map:
                        offset_cache[vert_index] = self._calc_vert_even_offset(bm.verts[vert_index])

                    # Tangent correction at open endpoints
                    if not strip['is_closed']:
                        for rail_verts_ids in [rail_0_verts, rail_1_verts]:
                            if len(rail_verts_ids) >= 2:
                                v0i = rail_verts_ids[0]
                                v1i = rail_verts_ids[1]
                                t = (bm.verts[v0i].co - bm.verts[v1i].co)
                                if t.length > 1e-9:
                                    t.normalize()
                                    if v0i in offset_cache:
                                        d = offset_cache[v0i]
                                        offset_cache[v0i] = d - d.dot(t) * t

                                vni = rail_verts_ids[-1]
                                vn1i = rail_verts_ids[-2]
                                t = (bm.verts[vni].co - bm.verts[vn1i].co)
                                if t.length > 1e-9:
                                    t.normalize()
                                    if vni in offset_cache:
                                        d = offset_cache[vni]
                                        offset_cache[vni] = d - d.dot(t) * t

                    for vert_index, new_v in strip_vert_map.items():
                        new_v.co += offset_cache.get(vert_index, Vector((0, 0, 0)))
                    for key, new_v in all_inner_verts.items():
                        _, vert_index = key
                        new_v.co += offset_cache.get(vert_index, Vector((0, 0, 0)))

                # --- Compute random along offset ---
                if self.uv_random_shift > 0:
                    rng = random.Random(self.uv_random_seed + group_idx)
                    along_offset = rng.uniform(0, self.uv_random_shift)
                else:
                    along_offset = 0.0

                # --- UV assignment for poly-mode faces ---
                bm_new.verts.ensure_lookup_table()
                bm_new.edges.ensure_lookup_table()
                bm_new.faces.ensure_lookup_table()

                uv_layer = bm_new.loops.layers.uv.get("UVMap") or bm_new.loops.layers.uv.new("UVMap")
                trim_count = max(1, self.uv_trim_count)
                ti = max(1, min(self.uv_trim_index, trim_count)) - 1
                trim_size = 1.0 / trim_count
                trim_min = ti * trim_size
                center_trim = trim_min + trim_size * 0.5

                uv_per_meter = trim_size / total_decal_width

                # Across fractions within the trim band
                frac_rail_0 = self.width / total_decal_width
                frac_rail_1 = (self.width + avg_strip_width) / total_decal_width

                # Helper: assign ribbon UV to a loop
                def _ribbon_uv(lp, face_side_val):
                    src_idx = int(lp.vert[src_vert_layer])
                    kind = int(lp.vert[vert_kind_layer])
                    along_uv = vertex_distance.get(src_idx, 0.0) * uv_per_meter

                    if face_side_val == 2:  # center strip
                        rail = rail_membership.get(src_idx, 0)
                        across_frac = frac_rail_0 if rail == 0 else frac_rail_1
                    elif face_side_val == 0:  # flap side 0
                        across_frac = frac_rail_0 if kind == 0 else 0.0
                    else:  # flap side 1
                        across_frac = frac_rail_1 if kind == 0 else 1.0

                    across_uv = trim_min + across_frac * trim_size
                    a_scaled = along_offset + along_uv * self.uv_scale
                    b_scaled = center_trim + (across_uv - center_trim) * self.uv_scale

                    if self.uv_orientation == 'VERTICAL':
                        lp[uv_layer].uv = (b_scaled, a_scaled)
                    else:
                        lp[uv_layer].uv = (a_scaled, b_scaled)

                for face in group_new_faces:
                    face_side = int(face[face_side_layer])
                    loops_list = list(face.loops)

                    # Center strip always uses ribbon UV (continuous)
                    if face_side == 2:
                        for lp in loops_list:
                            _ribbon_uv(lp, 2)
                        continue

                    # Side flaps
                    if not self.uv_split_flaps:
                        # Ribbon mode for flaps too
                        for lp in loops_list:
                            _ribbon_uv(lp, face_side)
                    else:
                        # Paper-craft unfold for flaps only
                        outer_loops = [l for l in loops_list if int(l.vert[vert_kind_layer]) == 0]
                        inner_loops = [l for l in loops_list if int(l.vert[vert_kind_layer]) == 1]
                        if len(outer_loops) != 2 or len(inner_loops) != 2:
                            for lp in loops_list:
                                _ribbon_uv(lp, face_side)
                            continue

                        outer_loops.sort(key=lambda l: vertex_distance.get(int(l.vert[src_vert_layer]), 0.0))
                        o0_3d = outer_loops[0].vert.co
                        o1_3d = outer_loops[1].vert.co
                        base_3d = o1_3d - o0_3d
                        base_len = base_3d.length
                        base_dir = base_3d / base_len if base_len > 1e-9 else Vector((0, 0, 1))

                        a0 = vertex_distance.get(int(outer_loops[0].vert[src_vert_layer]), 0.0) * uv_per_meter
                        a1 = vertex_distance.get(int(outer_loops[1].vert[src_vert_layer]), 0.0) * uv_per_meter

                        rail_frac = frac_rail_0 if face_side == 0 else frac_rail_1
                        across_outer = trim_min + rail_frac * trim_size

                        for ol in outer_loops:
                            al = vertex_distance.get(int(ol.vert[src_vert_layer]), 0.0) * uv_per_meter
                            a_s = along_offset + al * self.uv_scale
                            b_s = center_trim + (across_outer - center_trim) * self.uv_scale
                            if self.uv_orientation == 'VERTICAL':
                                ol[uv_layer].uv = (b_s, a_s)
                            else:
                                ol[uv_layer].uv = (a_s, b_s)

                        for il in inner_loops:
                            v_3d = il.vert.co - o0_3d
                            proj = v_3d.dot(base_dir)
                            perp = v_3d - proj * base_dir
                            across_world = perp.length

                            t = proj / base_len if base_len > 1e-9 else 0.0
                            inner_along = a0 + t * (a1 - a0)

                            if face_side == 0:
                                across_uv_raw = trim_min + (rail_frac - across_world / total_decal_width) * trim_size
                            else:
                                across_uv_raw = trim_min + (rail_frac + across_world / total_decal_width) * trim_size

                            a_s = along_offset + inner_along * self.uv_scale
                            b_s = center_trim + (across_uv_raw - center_trim) * self.uv_scale
                            if self.uv_orientation == 'VERTICAL':
                                il[uv_layer].uv = (b_s, a_s)
                            else:
                                il[uv_layer].uv = (a_s, b_s)

        if total_created_faces == 0:
            bm_new.free()
            self.report({'WARNING'}, 'No decal faces were generated')
            return {'CANCELLED'}

        # mark sharp edges on center seams across all groups
        bm_new.verts.ensure_lookup_table()
        bm_new.edges.ensure_lookup_table()
        bm_new.faces.ensure_lookup_table()

        for edge_new in bm_new.edges:
            if mode == 'POLY':
                edge_new.smooth = True
                continue

            a = int(edge_new.verts[0][src_vert_layer])
            b = int(edge_new.verts[1][src_vert_layer])
            if a > b:
                a, b = b, a
            kind_a = int(edge_new.verts[0][vert_kind_layer])
            kind_b = int(edge_new.verts[1][vert_kind_layer])

            if kind_a == 0 and kind_b == 0 and (a, b) in all_selected_edge_keys:
                edge_new.smooth = False
            else:
                edge_new.smooth = True

        new_mesh = bpy.data.meshes.new(f'{obj.name}_EdgeDecal')
        bm_new.to_mesh(new_mesh)
        bm_new.free()
        new_mesh.update()

        new_obj = bpy.data.objects.new(new_mesh.name, new_mesh)
        if obj.users_collection:
            obj.users_collection[0].objects.link(new_obj)
        elif context.collection is not None:
            context.collection.objects.link(new_obj)
        else:
            context.scene.collection.objects.link(new_obj)

        # Copy transform from the source object using stored property
        # values that remain valid even when the depsgraph hasn't been
        # evaluated (e.g. during operator redo after an internal undo).
        new_obj.location = source_loc
        new_obj.rotation_mode = source_rot_mode
        new_obj.rotation_euler = source_rot_euler
        new_obj.rotation_quaternion = source_rot_quat
        new_obj.scale = source_scale

        # If the source is parented, parent the decal the same way
        # so local transforms produce the correct world position.
        if obj.parent:
            new_obj.parent = obj.parent
            new_obj.parent_bone = obj.parent_bone
            new_obj.matrix_parent_inverse = obj.matrix_parent_inverse.copy()

        if self.material_name:
            mat = bpy.data.materials.get(self.material_name)
            if mat is not None:
                if not new_obj.data.materials:
                    new_obj.data.materials.append(mat)
                else:
                    new_obj.data.materials[0] = mat
            else:
                self.report({'WARNING'}, 'Custom material not found, no material assigned')

        if hasattr(new_obj.data, 'use_auto_smooth'):
            new_obj.data.use_auto_smooth = True
        for poly in new_obj.data.polygons:
            poly.use_smooth = True

        # keep Edit Mode on source object so redo/operator options stay available
        # mark created object as selected, but do not change active object or mode
        try:
            new_obj.select_set(True)
            obj.select_set(True)
            context.view_layer.objects.active = obj
        except RuntimeError:
            pass

        total_groups = len(edge_groups) if mode == 'EDGE' else len(face_groups)
        groups_ok = total_groups - skipped_groups
        if mode == 'POLY' and skipped_groups > 0:
            self.report({'WARNING'}, f'Some polygon groups were skipped (non-quad or branched): {skipped_groups}')
        self.report({'INFO'}, f'Edge decal created: {total_created_faces} faces from {groups_ok} group(s)')
        return {'FINISHED'}


classes = [
    PS_OT_create_edge_decal,
]


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
