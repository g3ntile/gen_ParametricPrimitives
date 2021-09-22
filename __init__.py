# gen charts
bl_info = {
    "name": "GEN Parametric Primitives",
    "author": "Pablo Gentile",
    "version": (0, 1, 0),
    "blender": (2, 80, 0),
    "category": "Object",
    "location": "View3D > Properties panel > Create",
    "description": "Procedural Primitives",
    "warning": "This is work in progress",
    "doc_url": "",
}

import bpy, math, bmesh, os

def printDiv(count=25): 
    print ("÷" * count)
    return()

def createVert(context, 
    obname="gen_Vert", 
    makenewmesh=True, 
    meshName="gen_onevert", 
    color=(1,1,1,1), 
    matName="__genObjectColor__"
    ): 
    """Creates a new object with one vertex"""
    
    # checks if mesh already exists
    try:
         bpy.data.meshes[meshName]
    # if not, create it
    except:
         print ("gen: one vert mesh doesn' exists") 
         # CREATE VERT MESH
         makenewmesh = True
    # if it exists, use it
    else:
         printDiv()
         print("gen: one vert already created")
         
    if makenewmesh:
         print ( "creating")
         mesh = bpy.data.meshes.new(meshName)
         
         if matName:
            mat = createChartMat(context, matName=matName)
            mesh.materials.append(mat)
         
    else:
         mesh = bpy.data.meshes[meshName]
     
    #CREATE OBJECT with created one vert mesh
    ob = bpy.data.objects.new( obname, mesh)     
    context.collection.objects.link(ob)
    ob.color = color
    ob.location = context.scene.cursor.location
    # or to assign to Collection use: bpy.data.collections["Collection Name"].objects.link(o)
    
    return (ob)


def createParamLadder(context,
        width   =0.28,
        step    =0.3,
        steps   =10,
        thickness   =0.0254,
        height  = 2,
        meshName= "genLadder",
        obname  = "Ladder"
        ):
    mesh = bpy.data.meshes.new(meshName)
    

    # create one vert mesh
    bm = bmesh.new()
    vertone = bm.verts.new((0,0,0))
    #verttwo = bm.verts.new((0,0,height))
    #edge = bm.edges.new([vertone,verttwo])
    bm.to_mesh(mesh)
    ob = bpy.data.objects.new( obname, mesh) 
    context.collection.objects.link(ob)

    # set width
    mod = ob.modifiers.new(name="ladderWidth", type='SCREW')
    mod.angle = 0
    mod.screw_offset = width
    mod.steps = 1
    mod.render_steps = 1
    mod.axis = 'X'
    mod.use_merge_vertices = True

    # step/height
    mod = ob.modifiers.new(name="ladderStep", type='SCREW')
    mod.angle = 0
    mod.screw_offset = step
    mod.axis = 'Z'
    mod.steps = 1
    mod.render_steps = 1
    mod.iterations = steps
    mod.use_merge_vertices = True


    # thickness
    mod = ob.modifiers.new(name="Wireframe", type='WIREFRAME')
    mod.thickness = thickness
    mod.show_in_editmode = True

    # make solid
    mod = ob.modifiers.new(name="Solid", type='SOLIDIFY')
    mod.thickness = thickness*0.6

    # weld
    mod = ob.modifiers.new(name="Weld", type='WELD')
    mod.merge_threshold = thickness/2

    # auto smooth
    ob.data.use_auto_smooth = True


    # To 3D cursor
    ob.location = context.scene.cursor.location    


    return (ob)

def createTruss(context,
        width       = .6, # not yet implemented
        height      =  10, # height of the column
        thickness   =  .0254, # thickness, 1 inch default, metric
        meshName    = "Truss",
        obname      = "Truss"

          ):
              
    # create two vert/one edge mesh
    mesh = bpy.data.meshes.new(meshName)
    
    bm = bmesh.new()
    vertone = bm.verts.new((0,0,0))
    verttwo = bm.verts.new((0,0,height))
    edge = bm.edges.new([vertone,verttwo])
    bm.to_mesh(mesh)
    ob = bpy.data.objects.new( obname, mesh) 
    context.collection.objects.link(ob)
    
    mod = ob.modifiers.new(name="Skin", type='SKIN')
    mod = ob.modifiers.new(name="Triangulate", type='TRIANGULATE')
    mod.quad_method = 'FIXED'
    mod = ob.modifiers.new(name="trussWireframe", type='WIREFRAME')
    mod.thickness = thickness
    mod.show_in_editmode = True
    #ob.data.skin_vertices[0].radius = (0.5,0.5)
    
    # To 3D cursor
    ob.location = context.scene.cursor.location    
    return (ob)

def createRailing(context,
        height      = .85,
        width       = .025,
        smooth      = True,
        thickness   = 0.0254
        ):
    ob = context.active_object

    # if in edit mode, create new object: to do
    
    # SKIN
    mod = ob.modifiers.new(name="divisions", type='SKIN') 
    # set the relative size of the skin vertices
    for v in ob.data.skin_vertices[0].data:
        v.radius = 0.00001, height/4
        
    mod = ob.modifiers.new(name="Weld", type='WELD') 
    
    # SUBDIV 
#    mod = ob.modifiers.new(name="Subd", type='SUBSURF') 
#    mod.subdivision_type = 'SIMPLE'
#    mod.levels = 1
#    mod.render_levels = 1

    # ARRAY 
    mod = ob.modifiers.new(name="DOUBLE", type='ARRAY') 
    mod.use_relative_offset = False
    mod.use_constant_offset = True
    mod.constant_offset_displace =(0,0,height/2)
    mod.use_merge_vertices = True

    # BEVEL: GENERATES INTERESTING PATTERNS
    mod = ob.modifiers.new(name="decoPatterns", type='BEVEL') 
    mod.affect = 'VERTICES'
    mod.offset_type = 'PERCENT'
    mod.width_pct = 0
    mod.segments = 1
    mod.limit_method = 'NONE'

    # thickness
    mod = ob.modifiers.new(name="Wireframe", type='WIREFRAME')
    mod.thickness = thickness
    mod.show_in_editmode = True
    
    ob.location = (
        ob.location[0],
        ob.location[1],
        ob.location[2] + height/4)
    if context.mode == 'OBJECT':
        bpy.ops.object.editmode_toggle()
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.object.skin_root_mark()
    if context.mode == 'EDIT_MESH':
        bpy.ops.object.editmode_toggle()




    
    
    # pseudo code:
    #if (edit mode and edge selected):
        
    return (ob)


#÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷
#    ########
# PANEL
#
class GENCHARTS_PT_main_panel(bpy.types.Panel):
    bl_label = "Gen Primitives"
    bl_idname = "GEN_PT_primitive_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Create"

    def draw(self, context):
        layout = self.layout
        pcoll = preview_collections["main"]
        truss_icon = pcoll["truss_icon"]
        railing_icon = pcoll["railing_icon"]
        ladder_icon = pcoll["ladder_icon"]

        C = context

        obj = context.active_object
        ob = obj
        # obj = context.object

        #row = layout.row()
        #row.label(text="Gen Primitives", icon='WORLD_DATA')
        
        #row = layout.row() 
        layout.operator("gen.myop_createtruss", icon_value=truss_icon.icon_id)
        try:
            layout.prop(ob.modifiers['trussWireframe'], "thickness", text="Beam thickness")
        except:
            print("no truss :-(")

        

        try:
            if ob.modifiers['decoPatterns']:
                layout.label(text="Railing properties", icon_value=railing_icon.icon_id)
            layout.prop(ob.modifiers['decoPatterns'], "width_pct", text="Deco pattern")
            layout.prop(ob.modifiers['decoPatterns'], "segments", text="Pattern steps")
            layout.prop(ob.modifiers['Wireframe'], "thickness", text="Beam thickness")
        except:
            layout.operator( "gen.myop_createrailing", icon_value=railing_icon.icon_id)
            print("no deco :-(")

        # ladder
        try:
            if ob.modifiers['ladderWidth']:
                layout.label(text="Ladder properties", icon_value=ladder_icon.icon_id)
                layout.prop(ob.modifiers['ladderWidth'], "screw_offset", text="Width")
                layout.prop(ob.modifiers['ladderStep'], "screw_offset", text="Step height")
                layout.prop(ob.modifiers['ladderStep'], "iterations", text="Steps")
                layout.prop(ob.modifiers['Wireframe'], "thickness", text="Thickness")
        except:
            layout.operator("gen.myop_createladder", icon_value=ladder_icon.icon_id)

        
class GEN_OT_new_truss(bpy.types.Operator):
    """Adds a parametric low poly trussed tower"""
    bl_label = "Add truss tower"
    bl_idname = "gen.myop_createtruss"
    
    
    
    def execute(self, context):
        
        
        #ob["gen_chartdata"] = bpy.types.Object.gen_chartprops()
        #ob["gen_chart_datalist"] = (45,45,90,180)
        #ob["gen_chart_labellist"] = ("perros", "gatos", "canarios", "elefantes")
        createTruss(context)
        
        return {'FINISHED'}
    
class GEN_OT_new_railing(bpy.types.Operator):
    """Converts active object into a parametric railing"""
    bl_label = "Convert to railing"
    bl_idname = "gen.myop_createrailing"
    
    def execute(self, context):
        createRailing(context)
        
        return {'FINISHED'}

class GEN_OT_new_ladder(bpy.types.Operator):
    """Adds a parametric ladder. Early alpha stage."""
    bl_label = "Add ladder (alpha)"
    bl_idname = "gen.myop_createladder"
    
    def execute(self, context):
        createParamLadder(context)
        
        return {'FINISHED'}


#÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷÷
#                                                    REGISTER

classes = [GENCHARTS_PT_main_panel, GEN_OT_new_truss, GEN_OT_new_railing, GEN_OT_new_ladder]
 
preview_collections = {}
 
def register():
    # icons
    import bpy.utils.previews
    pcoll = bpy.utils.previews.new()
    # path to the folder where the icon is
    # the path is calculated relative to this py file inside the addon folder
    my_icons_dir = os.path.join(os.path.dirname(__file__), "icons")

    # load a preview thumbnail of a file and store in the previews collection
    pcoll.load("truss_icon", os.path.join(my_icons_dir, "icons_truss.png"), 'IMAGE')
    pcoll.load("railing_icon", os.path.join(my_icons_dir, "icons_railing.png"), 'IMAGE')
    pcoll.load("ladder_icon", os.path.join(my_icons_dir, "icons_ladder.png"), 'IMAGE')

    preview_collections["main"] = pcoll

    # regular register
    for cls in classes:
        bpy.utils.register_class(cls)
        
 
def unregister():
    #icons
    for pcoll in preview_collections.values():
        bpy.utils.previews.remove(pcoll)
    preview_collections.clear()

    for cls in classes:
        bpy.utils.unregister_class(cls)
 
 
if __name__ == "__main__":
    register()