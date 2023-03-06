import bpy
import os

def import_fbx_file(fbx_path):
    # Import the FBX file and get the imported objects
    bpy.ops.import_scene.fbx(filepath=fbx_path, use_image_search=False)
    imported_objects = bpy.context.selected_objects

    # Separate the mesh and non-mesh objects
    mesh_objects = [obj for obj in imported_objects if obj.type == 'MESH']
    non_mesh_objects = [obj for obj in imported_objects if obj.type != 'MESH']

    # Select all the imported mesh objects and make the first object active
    bpy.ops.object.select_all(action='DESELECT')
    for obj in mesh_objects:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = mesh_objects[0]

    # Join the selected mesh objects and rename to the FBX name
    bpy.ops.object.join()
    bpy.ops.object.parent_clear(type='CLEAR_KEEP_TRANSFORM')
    joined_object = bpy.context.active_object
    fbx_name = os.path.splitext(os.path.basename(fbx_path))[0]

    # Set the origin of the joined object to its geometry
    bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY')

    #Apply Rotation/Scale
    bpy.ops.object.transform_apply(scale = True, rotation = True)

    # Delete the non-mesh objects
    non_mesh_object_names = [obj.name for obj in non_mesh_objects]
    for obj in non_mesh_objects:
        bpy.data.objects.remove(obj, do_unlink=True)

    # Rename the joined object to the FBX name
    joined_object.name = fbx_name

    # Move the joined object to a collection named after the folder the FBX file is in
    collection_name = os.path.basename(os.path.dirname(fbx_path))
    collection = bpy.data.collections.get(collection_name)
    if collection is None:
        collection = bpy.data.collections.new(name=collection_name)
        bpy.context.scene.collection.children.link(collection)

    bpy.ops.object.select_all(action='DESELECT')
    joined_object.select_set(True)
    bpy.context.view_layer.objects.active = joined_object
    for other_collections in joined_object.users_collection:
        other_collections.objects.unlink(joined_object)
    collection.objects.link(joined_object)

    return {'FINISHED'}

class FBXImporterPanel(bpy.types.Panel):
    bl_idname = "OBJECT_PT_browzwear_fbx_importer"
    bl_label = "Browzwear FBX Importer"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Browzwear FBX'

    def draw(self, context):
        layout = self.layout

        # Add dropdown for selecting file or folder
        layout.prop(context.scene, "import_type", text="Select")

        if context.scene.import_type == 'FILE':
            # Add a file browser to select the FBX file
            layout.label(text="Select FBX File to Import")
            layout.prop(context.scene, "fbx_path")
            layout.operator("object.browzwear_fbx_import", text="Import File", icon="FILE")

        elif context.scene.import_type == 'FOLDER':
            # Add a folder browser to select the folder with FBX files
            layout.label(text="Select Folder to import FBX files from")
            layout.prop(context.scene, "fbx_folder")
            layout.operator("object.browzwear_fbx_import_folder", text="Import Folder", icon="FILE_FOLDER")


class FBXImportOperator(bpy.types.Operator):
    """Import FBX File"""
    bl_idname = "object.browzwear_fbx_import"
    bl_label = "Import Browzwear FBX"
    bl_description = "Import a Browzwear FBX file and perform operations on the imported objects"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        # Get the path to the selected FBX file
        fbx_path = bpy.path.abspath(context.scene.fbx_path)

        # Import the FBX file and get the imported objects
        imported_object = import_fbx_file(fbx_path)
        return {'FINISHED'}

class FBXImportFolderOperator(bpy.types.Operator):
    bl_idname = "object.browzwear_fbx_import_folder"
    bl_label = "Import All Browzwear FBX Files in Folder"
    bl_description = "Import all Browzwear FBX files in the selected folder and perform operations on the imported objects"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        # Get the path to the selected folder
        fbx_folder = bpy.path.abspath(context.scene.fbx_folder)

        # Loop through each file in the folder and import FBX files
        for root, dirs, files in os.walk(fbx_folder):
            for file_name in files:
                if file_name.endswith('.fbx'):
                    fbx_path = os.path.join(root, file_name)
                    print(fbx_path)
                    import_fbx_file(fbx_path)

        return {'FINISHED'}

classes = (
    FBXImporterPanel,
    FBXImportOperator,
    FBXImportFolderOperator
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    # Register the EnumProperty
    bpy.types.Scene.import_type = bpy.props.EnumProperty(
        name="Import Type",
        items=[('FILE', "File", ""),
               ('FOLDER', "Folder", "")],
        default='FILE'
    )

    bpy.types.Scene.fbx_path = bpy.props.StringProperty(
        name="FBX File",
        subtype='FILE_PATH'
    )

    bpy.types.Scene.fbx_folder = bpy.props.StringProperty(
        name="FBX Folder",
        subtype='DIR_PATH'
    )

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

    del bpy.types.Scene.fbx_path
    del bpy.types.Scene.fbx_folder
    del bpy.types.Scene.import_type

if __name__ == "__main__":
    register()

