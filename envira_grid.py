import bpy


from gpu_extras.batch import batch_for_shader
from bpy.types import Operator, GizmoGroup, Gizmo
import bmesh






import bgl 

import gpu
from math import sin, cos, pi
from gpu.types import (
        GPUBatch,
        GPUVertBuf,
        GPUVertFormat,
    )
from mathutils import Matrix, Vector
import mathutils


 


def generate_grid():
    settings = bpy.context.scene.ps_set_
    unit = settings.one_unit_length
    

    if settings.one_unit == 'CM':
        #unit = 0.01
        x = settings.unit_x  / 100
        y = settings.unit_y / 100
        z = settings.float_z / 100

        if settings.one2one:
            size = int( abs(x*200) )
        else:
            if x > y:
                size = int( abs(x*200) )
            else:
                size = int( abs(y*200) )


    elif settings.one_unit == 'M':
        #unit = 1
        x = settings.unit_x
        y = settings.unit_y
        z = settings.float_z


        if settings.one2one:
            size = int( abs(x*2) )
        else:
            if x > y:
                size = int( abs(x*2) )
            else:
                size = int( abs(y*2) )

    #size = settings.grid_count
    

    #print(size)

    line_co = []
    for i in range(size):
        
        #coef = i * 0.5
        xZero = x/2 - unit * i
        yZero = y/2 - unit * i
     
        if settings.one2one:
            if xZero <= x/2 and xZero >= -x/2:
                vec1Y = (x/2, xZero, z)
                vec2Y = (-x/2, xZero, z)

        else:
            if yZero <= y/2 and yZero >= -y/2:
                vec1Y = (x/2, yZero, z)
                vec2Y = (-x/2, yZero, z)

        line_co.append(vec1Y)
        line_co.append(vec2Y)


        if xZero <= x/2 and xZero >= -x/2:
            if settings.one2one:
                vec1X = (xZero, x/2, z)
                vec2X = (xZero, -x/2, z)
            else:
                vec1X = (xZero, y/2, z)
                vec2X = (xZero, -y/2, z)

        line_co.append(vec1X)
        line_co.append(vec2X)


    return line_co



def lines():
    settings = bpy.context.scene.ps_set_

    if settings.one_unit == 'CM':
        x = settings.unit_x / 100
        y = settings.unit_y / 100
        z = settings.float_z / 100

    elif settings.one_unit == 'M':
        x = settings.unit_x
        y = settings.unit_y
        z = settings.float_z

    if settings.one_unit == 'CM':
        xPad = (settings.unit_x - (settings.padding * 2) ) / 100
        yPad = (settings.unit_y - (settings.padding * 2) ) / 100

    elif settings.one_unit == 'M':
        xPad = (settings.unit_x - (settings.padding * 2/ 100) )
        yPad = (settings.unit_y - (settings.padding * 2/ 100) )



    linesCo = []

    if settings.one2one:
        linesCo = [
            (x/2, x/2, z), (-x/2, x/2, z),
            (-x/2, x/2, z), (-x/2, -x/2, z),
            (-x/2, -x/2, z), (x/2, -x/2, z),
            (x/2, -x/2, z), (x/2, x/2, z),

            (xPad/2, xPad/2, z), (-xPad/2, xPad/2, z),
            (-xPad/2, xPad/2, z), (-xPad/2, -xPad/2, z),
            (-xPad/2, -xPad/2, z), (xPad/2, -xPad/2, z),
            (xPad/2, -xPad/2, z), (xPad/2, xPad/2, z),
        ]

    else:
        linesCo = [
            (x/2, y/2, z), (-x/2, y/2, z),
            (-x/2, y/2, z), (-x/2, -y/2, z),
            (-x/2, -y/2, z), (x/2, -y/2, z),
            (x/2, -y/2, z), (x/2, y/2, z),

            (xPad/2, yPad/2, z), (-xPad/2, yPad/2, z),
            (-xPad/2, yPad/2, z), (-xPad/2, -yPad/2, z),
            (-xPad/2, -yPad/2, z), (xPad/2, -yPad/2, z),
            (xPad/2, -yPad/2, z), (xPad/2, yPad/2, z),
        ]


    return linesCo



def box():
    settings = bpy.context.scene.ps_set_
    
    if settings.one_unit == 'CM':
        xPad = (settings.unit_x - (settings.padding * 2) ) / 100
        yPad = (settings.unit_y - (settings.padding * 2) ) / 100
        z = settings.float_z / 100
        h = settings.box_height / 100

    elif settings.one_unit == 'M':
        xPad = (settings.unit_x - (settings.padding * 2 / 100) )
        yPad = (settings.unit_y - (settings.padding * 2 / 100) )
        z = settings.float_z
        h = settings.box_height

    faceCo = []


    if settings.one2one:
        faceCo = [
            (xPad/2, xPad/2, z),
            (xPad/2, -xPad/2, z),
            (-xPad/2, -xPad/2, z),
            (-xPad/2, xPad/2, z),
            (xPad/2, xPad/2, h),
            (xPad/2, -xPad/2, h),
            (-xPad/2, -xPad/2, h),
            (-xPad/2, xPad/2, h),
        ]
    else:
        faceCo = [
            (xPad/2, yPad/2, z),
            (xPad/2, -yPad/2, z),
            (-xPad/2, -yPad/2, z),
            (-xPad/2, yPad/2, z),
            (xPad/2, yPad/2, h),
            (xPad/2, -yPad/2, h),
            (-xPad/2, -yPad/2, h),
            (-xPad/2, yPad/2, h),
        ]


    faces_indices = [
        (0, 1, 3), (1, 2, 3),
        (4, 5, 7), (5, 6, 7),
        (1, 2, 5), (2, 5, 6),
        (0, 1, 4), (1, 4, 5),
        (0, 3, 7), (0, 4, 7),
        (2, 3, 6), (3, 6, 7),
    ]



    return faceCo, faces_indices



def draw_grid(self, context):
    settings = context.scene.ps_set_



    shader = gpu.shader.from_builtin('3D_UNIFORM_COLOR')
    shader.bind()

    # Color
    props = context.preferences.addons[__package__].preferences
    line_color = props.lines_props_grid
    box_color = props.box_props_grid
    unit_grid_color = props.unit_grid


    lineWidth = 3.0
    lineSmooth = True
    xray = False


    bgl.glEnable(bgl.GL_BLEND)
    bgl.glLineWidth(lineWidth)

    bgl.glDepthMask(False)

    if xray == False:
        bgl.glEnable(bgl.GL_DEPTH_TEST)


    if lineSmooth:
        bgl.glEnable(bgl.GL_LINE_SMOOTH)

    

    if settings.box:
        faceCo, faces_indices = box()
        FACES = batch_for_shader(shader, 'TRIS', {"pos": faceCo}, indices=faces_indices)
        shader.uniform_float("color", box_color)
        FACES.draw(shader)


    if settings.draw_unit_grid:
        gridCo = generate_grid()
        GRID_EDGES = batch_for_shader(shader, 'LINES', {"pos": gridCo}) 
        shader.uniform_float("color", unit_grid_color)
        GRID_EDGES.draw(shader)


    linesCo = lines()
    EDGES = batch_for_shader(shader, 'LINES', {"pos": linesCo}) 
    shader.uniform_float("color", line_color)
    EDGES.draw(shader)





    bgl.glDisable(bgl.GL_LINE_SMOOTH)

    bgl.glDisable(bgl.GL_DEPTH_TEST)
    #bgl.glDisable(bgl.GL_CULL_FACE)
    bgl.glLineWidth(1)
    bgl.glDisable(bgl.GL_BLEND) 



class PS_GT_draw_grid(Gizmo):
    bl_idname = "ps.draw_grid"

    def draw(self, context):
        draw_grid(self, context)
    

    def setup(self):
        self.use_draw_modal = False


    """ def test_select(self, context, location):
        if context.area.type == 'VIEW_3D':
            context.area.tag_redraw()
        return -1 """



class PS_GGT_draw_grid_group(GizmoGroup):
    
    bl_idname = "PS_GGT_draw_grid_group"
    bl_label = "PS Draw Grid"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'WINDOW'
    bl_options = {'3D','SHOW_MODAL_ALL'} #'DEPTH_3D' , 'TOOL_INIT', 'SELECT', , 'SCALE' , 'SHOW_MODAL_ALL'  'PERSISTENT', 
 

    """ @classmethod
    def poll(cls, context):
        settings = context.scene.ps_set_
        return settings.PS_envira_grid """
        

    def setup(self, context):
        mesh = self.gizmos.new(PS_GT_draw_grid.bl_idname)
        self.mesh = mesh 



classes = [
    PS_GT_draw_grid,
    PS_GGT_draw_grid_group,
]


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

   
def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)