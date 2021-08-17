import bpy
import bmesh
from bpy.types import Operator
from bpy.props import BoolProperty, IntProperty, FloatProperty, EnumProperty
from mathutils import Matrix, Vector
from math import degrees, atan2, pi


class PS_OT_del_long_faces(Operator):
    bl_idname = "ps.del_long_faces"
    bl_label = "Delete Long Faces"
    #bl_description="To Remove A Single Vertex"
    bl_options = {'REGISTER', 'UNDO'}


    angle: FloatProperty(name='Angle', default=168.0)
    use_face_split: BoolProperty(name='Use Face Split', default=False)
    use_boundary_tear: BoolProperty(name='Use Boundary Tear', default=False)
    selected: BoolProperty(name='Selected Faces', default=False)
    logics: EnumProperty( 
        name = 'Logics',
        items = [
            ("GREATER_THAN", "Greater Than", ""),
            ("NOT_EQUAL_TO", "Not Equal To", ""),
            ("EQUAL_TO", "Equal To", ""), 
            ("LESS_THAN", "Less Than", ""),
            ], 
        default="GREATER_THAN",
        )
    


    @classmethod
    def poll(cls, context):
        return context.mode == 'EDIT_MESH'

    def execute(self, context):
        vCount = 0

        uniques = context.selected_objects
        for obj in uniques:
            me = obj.data

            #bm = bmesh.new()
            #bm.from_mesh(me)
            bm = bmesh.from_edit_mesh(me)
            bm.verts.ensure_lookup_table()

            vDots = []
            

            # project into XY plane, 
            up = Vector((0, 0, 1))

            
            def edge_angle(e1, e2, face_normal):
                b = set(e1.verts).intersection(e2.verts).pop()
                a = e1.other_vert(b).co - b.co
                c = e2.other_vert(b).co - b.co
                a.negate()    
                axis = a.cross(c).normalized()
                if axis.length < 1e-5:
                    return pi # inline vert
                
                if axis.dot(face_normal) < 0:
                    axis.negate()
                M = axis.rotation_difference(up).to_matrix().to_4x4()  

                a = (M @ a).xy.normalized()
                c = (M @ c).xy.normalized()
                
                return pi - atan2(a.cross(c), a.dot(c))


            if self.selected:
                selected_faces = [f for f in bm.faces if f.select]
            else:
                selected_faces = [f for f in bm.faces]


            for f in selected_faces:
                edges = f.edges[:]
                #print("Face", f.index, "Edges:", [e.index for e in edges])
                edges.append(f.edges[0])
                
                for e1, e2 in zip(edges, edges[1:]):

                    angle = edge_angle(e1, e2, f.normal)

                    e1_v0 =  e1.verts[0]
                    e1_v1 =  e1.verts[1]

                    e2_v0 =  e1.verts[0]
                    e2_v1 =  e1.verts[1]

                    if e1_v0 == e2_v0 or e1_v0 == e2_v1:
                        v = e1_v0
                    elif e1_v1 == e2_v0 or e1_v1 == e2_v1:
                        v = e1_v1


                    if self.logics == 'GREATER_THAN':
                        if degrees(angle) > self.angle:
                            vDots.append(v)
                            vCount += 1

                    elif self.logics == 'NOT_EQUAL_TO':
                        if degrees(angle) != self.angle:
                            vDots.append(v)
                            vCount += 1
                    
                    elif self.logics == 'EQUAL_TO':
                        if degrees(angle) == self.angle:
                            vDots.append(v)
                            vCount += 1
                    
                    elif self.logics == 'LESS_THAN':
                        if degrees(angle) < self.angle:
                            vDots.append(v)
                            vCount += 1

                            
                    #print("Edge Corner", e1.index, e2.index, "Angle:", degrees(angle))

            # --- Delete Duplicate Vector
            def del_duplicate(list): # FIXME
                newList = []
                for i in list:
                    if i not in newList:
                        newList.append(i)
                return newList
            vDots = del_duplicate(vDots)


            if len(vDots) > 0:
                #print(vDots)
                bmesh.ops.dissolve_verts(bm, verts=vDots, use_face_split=self.use_face_split, use_boundary_tear=self.use_boundary_tear) 
                #bmesh.ops.delete(mesh, geom=vDots, context='VERTS')
                bmesh.update_edit_mesh(me)
                """ bm.to_mesh(me)
                me.update()
                bm.free() """

        self.report({'INFO'}, "Clear Dots - " + str(vCount))
        return {'FINISHED'}








classes = [
    PS_OT_del_long_faces,
]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)