import math
import bpy
from bpy.types import Operator
from bpy.props import IntProperty, FloatProperty, BoolProperty
import bmesh # FIXME

from bpy_extras.object_utils import AddObjectHelper, object_data_add



####################################################################################################### CILINDER
class PS_OT_create_cylinder(Operator, AddObjectHelper): #FIXME
    bl_idname = 'ps.create_cylinder'
    bl_label = 'Create Cylinder'
    bl_options = {"REGISTER", "UNDO"}
 

    count: IntProperty(name = "Edges", description = "Edges count", default = 8, min = 3)
    radius: FloatProperty(name = "Radius", default = 1)
    
    h: FloatProperty(name = "Height", description = "Height", default = 1.0)
    
    used_eSize: BoolProperty(name="Use The Edge Size", default=False)
    eSize: FloatProperty(name = "Edge Length Min", description = "Set the minimum edge length", default = 0.5)
    


    def create_verts(self, context):
        verts = []
        ring1 = []
        ring2 = []
        faces = []

        if self.used_eSize:
            length = self.eSize * self.count
            radius_ = length / (2 * math.pi)
        else:   
            radius_ = self.radius


        
        for i in range(self.count):
            grad = (360 * i / self.count) * math.pi / 180
            ring1.append([radius_ * math.cos(grad), radius_ * math.sin(grad), 0])
            ring2.append([radius_ * math.cos(grad), radius_ * math.sin(grad), self.h])
            
            if i == 0:
                faces.append([i - 1 + self.count, i - 1 + 2 * self.count, i + self.count, i])
            
            else:
                faces.append([i - 1, i - 1 + self.count, i + self.count, i])

        verts.extend(ring2)
        verts.extend(ring1)
        

        return verts, faces


    def execute(self, context):

        verts, faces = self.create_verts(context)

  
        me = bpy.data.meshes.new("Cylinder")
        me.from_pydata(verts, [], faces)
        

        # useful for development when the mesh may be invalid.
        # mesh.validate(verbose=True)
        object_data_add(context, me, operator=self)
        
        
        return {'FINISHED'}


    def draw(self, context):
        layout = self.layout

        layout.prop(self, "used_eSize")
        if self.used_eSize:
            layout.prop(self, "eSize")

        layout.separator()
        layout.prop(self, "count")
        layout.prop(self, "radius")

        layout.separator()
        layout.prop(self, "h")  
        
        layout.separator()
        layout.prop(self, "align")
        layout.prop(self, "location")
        layout.prop(self, "rotation")



####################################################################################################### TUBE
class PS_OT_create_tube(Operator, AddObjectHelper): #FIXME
    bl_idname = 'ps.create_tube'
    bl_label = 'Create Tube'
    bl_options = {"REGISTER", "UNDO"}
 
    count: IntProperty(name = "Edges", description = "Edges count", default = 8, min = 3)
    r1: FloatProperty(name = "O-Radius", description = "Outer radius", default = 1)
    r2: FloatProperty(name = "I-Radius", description = "Inner radius", default = 0.5)
    h: FloatProperty(name = "Height", description = "Height", default = 1.0)
    
    used_eSize: BoolProperty(name="Use The Edge Size", default=False)
    eSize: FloatProperty(name = "Edge Length Min", description = "Set the minimum edge length", default = 0.5)

    def create_verts(self, context):
        verts = []
        ring1 = []
        ring2 = []
        ring3 = []
        ring4 = []
        faces = []

        if self.used_eSize:
            length = self.eSize * self.count
            radius_ = length / (2 * math.pi)
        else:   
            radius_ = self.r1

    
        if self.r2 > radius_: #FIXME add none
            iner_radius_ = radius_
        elif self.r2 <= 0.0: # add cup
            iner_radius_ = 0.0
        else:
            iner_radius_ = self.r2



        for i in range(self.count):
            grad = (360 * i / self.count) * math.pi / 180
            ring1.append([radius_ * math.cos(grad), radius_ * math.sin(grad), 0])
            ring2.append([iner_radius_ * math.cos(grad), iner_radius_ * math.sin(grad), 0])
            ring3.append([radius_ * math.cos(grad), radius_ * math.sin(grad), self.h])
            ring4.append([iner_radius_ * math.cos(grad), iner_radius_ * math.sin(grad), self.h])
            if i == 0:
                faces.append([i - 1 + self.count, i, i + 2 * self.count, i - 1 + 3 * self.count])
                faces.append([i - 1 + 2 * self.count, i - 1 + 4 * self.count, i + 3 * self.count, i + self.count])
                faces.append([i - 1 + self.count, i - 1 + 2 * self.count, i + self.count, i])
                faces.append([i - 1 + 3 * self.count, i + 2 * self.count, i + 3 * self.count, i - 1 + 4 * self.count])
            else:
                faces.append([i - 1, i, i + 2 * self.count, i - 1 + 2 * self.count])
                faces.append([i - 1 + self.count, i - 1 + 3 * self.count, i + 3 * self.count, i + self.count])
                faces.append([i - 1, i - 1 + self.count, i + self.count, i])
                faces.append([i - 1 + 2 * self.count, i + 2 * self.count, i + 3 * self.count, i - 1 + 3 * self.count])
 









 
        verts.extend(ring1)
        verts.extend(ring2)
        verts.extend(ring3)
        verts.extend(ring4)

        return verts, faces


    def execute(self, context):
        verts, faces = self.create_verts(context)



        me = bpy.data.meshes.new("Tube")
        me.from_pydata(verts, [], faces)


        # useful for development when the mesh may be invalid.
        # mesh.validate(verbose=True)
        object_data_add(context, me, operator=self)


        return {'FINISHED'}


    def draw(self, context):
        layout = self.layout

        layout.prop(self, "used_eSize")
        if self.used_eSize:
            layout.prop(self, "eSize")

        layout.separator()
        layout.prop(self, "count")

        row = layout.row()
        row.prop(self, "r1")
        row.prop(self, "r2")


        layout.separator()
        layout.prop(self, "h")  
        
        layout.separator()
        layout.prop(self, "align")
        layout.prop(self, "location")
        layout.prop(self, "rotation")




classes = [
    PS_OT_create_cylinder,
    PS_OT_create_tube,
    ]

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls) 