import bpy
import blf
import bmesh
from bpy.types import Gizmo, GizmoGroup








def polycount(self, context):
    if context.active_object != None:
        font_info = {
            "font_id": 0,
            "handler": None,
        }

        props = context.preferences.addons[__package__].preferences
        settings = context.scene.ps_set_

 
    

        font_id_name = font_info["font_id"]

        width = 10
        height = 45
        name = "Polycount: " + str(settings.tris_count) + "/"
        blf.position(font_id_name, width, height, 0)
        blf.size(font_id_name, 14, 72)
        blf.color(font_id_name, 0.58, 0.72, 0.0, 1.0)
        blf.draw(font_id_name, name)
        
        

        if props.low_suffix == False:
            viewlayer = context.view_layer
            collection = context.scene.statistics(viewlayer).split(" | ")[4]
            string = collection[5:].replace(',', '')
            tris = int(string)

        else:
            tris = 0
            for collection in bpy.data.collections:
                name = collection.name
                if name.endswith("_low") or name.endswith("_Low") or name.endswith("_LOW"):
                    for obj in collection.objects:
                        if obj.type == 'MESH':
                            if obj.mode != 'EDIT': 
                                tris += sum( [len(f.vertices) - 2 for f in obj.data.polygons] )

                            elif obj.mode == 'EDIT':  
                                bm = bmesh.from_edit_mesh(obj.data)
                                tris += sum( [len(f.verts) - 2 for f in bm.faces] )
                            else:
                                pass
            
        if tris > 0:
            coef = settings.tris_count / tris
        else:
            coef = 1

        
        
        if coef < 1:
            col = (1.0, 0.1, 0.0) 
        elif 1.2 > coef > 1:
            col = (1.0, 0.5, 0.0) 
        else:
            col = (0.9, 0.9, 0.9) 


        offset = len(str(settings.tris_count)) * 6

        width = 110 + offset
        apply_text = str(tris)
        blf.position(font_id_name, width, height, 0)
        blf.size(font_id_name, 14, 72)
        blf.color(font_id_name, col[0], col[1], col[2], 1.0)
        blf.draw(font_id_name, apply_text)

        #blf.shadow(font_id_name, 6, 0.0, 0.0, 0.0, 1.0)
        




        # ACTIVE
        tris = 0
        sel_obj = context.objects_in_mode_unique_data
        for obj in sel_obj: 
            if obj.type == 'MESH':
                if obj.mode != 'EDIT': 
                    tris += sum( [len(f.vertices) - 2 for f in obj.data.polygons] )

                elif obj.mode == 'EDIT':  
                    bm = bmesh.from_edit_mesh(obj.data)
                    tris += sum( [len(f.verts) - 2 for f in bm.faces] )
                else:
                    pass

    

        width = 10
        height = 30
        name = "Active Object: "
        blf.position(font_id_name, width, height, 0)
        blf.size(font_id_name, 14, 72)
        blf.color(font_id_name, 0.58, 0.72, 0.0, 1.0)
        blf.draw(font_id_name, name)



        width = 110 + offset
        apply_text = str(tris)
        blf.position(font_id_name, width, height, 0)
        blf.size(font_id_name, 14, 72)
        blf.color(font_id_name, 0.9, 0.9, 0.9, 1.0)
        blf.draw(font_id_name, apply_text)



class PS_GT_polycount(Gizmo):
    bl_idname = 'PS_GT_polycount'

    def draw(self, context):
        polycount(self, context)

    """ def test_select(self, context, location):
        if context.area.type == 'VIEW_3D':
            context.area.tag_redraw()
        return -1 """



class PS_GGT_polycount_group(GizmoGroup):
    
    bl_idname = 'PS_GGT_polycount_group'
    bl_label = 'Poly Count'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'WINDOW'
    bl_options = {'SHOW_MODAL_ALL'} #'DEPTH_3D' , 'TOOL_INIT', 'SELECT', , 'SCALE' , 'SHOW_MODAL_ALL' 'PERSISTENT', 
 

    @classmethod
    def poll(cls, context):
        if context.active_object != None:
            settings = context.scene.ps_set_
            return settings.PS_polycount
        
  
    def setup(self, context):
        mesh = self.gizmos.new('PS_GT_polycount')
        mesh.use_draw_modal = True
        self.mesh = mesh 


    def draw_prepare(self, context):
        settings = context.scene.ps_set_
        #props = context.preferences.addons[__package__.split(".")[0]].preferences
        mesh = self.mesh
        if settings.PS_polycount:
            mesh.hide = False
        else:
            mesh.hide = True





















classes = [
    PS_GT_polycount,
    PS_GGT_polycount_group,
]


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

   
def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)