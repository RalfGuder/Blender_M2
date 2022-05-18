
#from . import m2_format
#from .m2_format import *

#from . import m2_file
#from .m2_file import *

#import bpy
import os
import m2_format
import m2_file
from m2_file import M2SkinFile, M2File 
import dbcpy.records
import configparser


config = None # Konfiguration

def openSkinFiles(root):

    skin_list = []
    # Meshes aus den Skin-Profilen erzeugen 
    for i in range(root.header.num_skin_profiles):
        skinName = f"{root.path}/{root.modelName}{i:02d}.skin"
        
        if(os.path.isfile(skinName) == False):
            # Datei ist nicht vorhanden
            break
        
        skin = M2SkinFile()
        skin.read(open(skinName, 'rb'))
        
        # Skin-File hinzufügen
        skin_list.append(skin)

    return skin_list

def read(filename):
    '''
    Einlesen der *.m2-Datei
    '''
    xxx = os.path.join(os.path.dirname(__file__), "config.ini")
    print(xxx)
    config = configparser.ConfigParser()
    config.read(xxx, "utf-8")
    
    
    f = open(str(filename), "rb")
    skin_list = []

    # root WMO
    root = M2File(config)
    root.read(f)
    skin_list.extend(openSkinFiles(root))

    root.createBlender()
    # load all materials in root file
    #root.LoadMaterials(bpy.path.display_name_from_filepath(rootName), os.path.dirname(filename) + "\\")

    # load all lights
    #root.LoadLights(bpy.path.display_name_from_filepath(rootName))
    #root.LoadPortals(bpy.path.display_name_from_filepath(rootName))
    '''
    # Meshes erzeugen
    for skinfile in skin_list:
        skinfile.draw_submesh(root)
    '''
    

#if __name__ == "__main__":


#read("C:/Users/10170328/git/Slick2D/bundeswehr-slick2d/src/main/resources/creature/raptor/raptor.m2")
#read("C:/Users/10170328/git/Slick2D/bundeswehr-slick2d/src/main/resources/creature/Chicken/Chicken.M2")
#read("C:/Users/10170328/git/Slick2D/bundeswehr-slick2d/src/main/resources/creature/crawler/crawler.M2")
read("C:/Users/10170328/git/Slick2D/bundeswehr-slick2d/src/main/resources/creature/rexxar/rexxar.M2")