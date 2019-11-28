
import GameLogic
import bge
import aud
import os
import random
from mathutils import Matrix 
from mathutils import Vector 
import math


cont = bge.logic.getCurrentController()
own = cont.owner

def init():
    if own["startedScene"]==0:
        own["Armature"] = GameLogic.getCurrentScene().objects['Armature']
        own["FPScounter"] = GameLogic.getCurrentScene().objects['FPScounter']
        own["VROBJECT"] = GameLogic.getCurrentScene().objects['VROBJECT']
        own["ActionCounter"] = GameLogic.getCurrentScene().objects['ActionCounter']
        own["AnimSpeedCounter"] = GameLogic.getCurrentScene().objects['AnimSpeedCounter']
        
        own["SceneLogic"] = GameLogic.getCurrentScene().objects['SceneLogic']
        own["MouseCont"]=cont.sensors['Mouse']
        
        textres=8.0
        Textcol=[ 0.0, 0.5, 0.0, 0.5]
        
        own["FPScounter"].resolution = textres
        own["ActionCounter"].resolution = textres
        own["AnimSpeedCounter"].resolution = textres
        
        own["FPScounter"].color=Textcol
        own["ActionCounter"].color=Textcol
        own["AnimSpeedCounter"].color=Textcol
        own["mouseLock"]=True
        own["timer"]=1
        
        SceneOBJs = GameLogic.getCurrentScene().objects
        HairOBJs = []
        for OBJ in SceneOBJs:
            if "Hair" in OBJ:
                HairOBJs.append(OBJ)
        own["HairsOBJs"] = HairOBJs
        
        randomHairScale=random.uniform(0.4,1.1)
        GameLogic.getCurrentScene().objects['hairScaler'].localScale=Vector([randomHairScale,randomHairScale,randomHairScale])
        JiggleOBJs = []
        for OBJ in SceneOBJs:
            if "Jiggler" in OBJ:
                OBJ["Track"]=OBJ.parent
                OBJ.parent["changeTrackerChild"]=0
                OBJ.parent["LastPos"]=0
                OBJ["speed"]=55.0
                OBJ["Parent"]=OBJ.parent
                OBJ.removeParent()
                JiggleOBJs.append(OBJ)
        own["JiggleOBJs"] = JiggleOBJs
        own["startedScene"]=1
        
def changeObjectColor(ObjectName):
    ObjectName.color = ObjectName.color
    #[1.0, 0.0, 0.0, 1.0]

#def debugInfo():
#    cont = bge.logic.getCurrentController()
#    own = cont.owner
    #GameLogic.getCurrentScene().objects['debugText']['Text']='tet'
    
    
def jiggleHandler():
    for OBJ in own["JiggleOBJs"]:
        ForceVec = (OBJ["Track"].position-OBJ.position)*(OBJ["speed"]*random.uniform(0.8,1.0))
        
        if OBJ["Parent"]["LastPos"]<25:
            OBJ["Parent"]["LastPos"]+=1
            OBJ.position = OBJ["Parent"].position
            OBJ.applyForce((0,0,0),False)
        if own["Armature"]["ChangeTracker"]!=OBJ["Parent"]["changeTrackerChild"]:
            OBJ["Parent"]["LastPos"]=0
            OBJ["Parent"]["changeTrackerChild"]=own["Armature"]["ChangeTracker"]
        if "OrgasmOffsetVector" in OBJ:
            obvec=OBJ["OrgasmOffsetVector"]
            speed=0.95
            OBJ["OrgasmOffsetVector"] = Vector([obvec.x*speed,obvec.y*speed,obvec.z*speed])
        
            ForceVec=ForceVec+OBJ["OrgasmOffsetVector"]
        OBJ.applyForce(ForceVec,False)
def truncate(f, n):
    return math.floor(f * 10 ** n) / 10 ** n
def editMesh():
    armcont = bge.logic.getCurrentController()
    armown = cont.owner
    scene=GameLogic.getCurrentScene()
    meshOBJ=scene.objects['GIRLOBJECT-LP']
    

    m_i = 0
    
    #print(meshOBJ.meshes)
    ##print('that was one pulse')
    mesh = meshOBJ.meshes[0]
    #armown.removeParent()

    # Iterates through all vertices:
    #print(mesh.getVertexArrayLength(1))
    #print(dir(mesh))
    #print(mesh.transform())
    for mat in range(mesh.numMaterials):
        ##print(mesh.getVertexArrayLength(mat))
        for v_index in range(mesh.getVertexArrayLength(mat)):
            vertex = mesh.getVertex(mat, v_index)
             # Do something with vertex here...
            # ... eg: colour the vertex red.
            vertex.color = [1.0, 0.0, 0.0, 1.0]
            
            
            
    

    
def display():
    own["timer"]=own["timer"]+1
    if own["timer"]>30:
        trunc=3

        own["FPScounter"]["Text"]="FPS "+ (str)(truncate(GameLogic.getAverageFrameRate(),trunc))
        own["ActionCounter"]["Text"]="Action ("+ (str)(own["Armature"]["CurrentAction"]) +"/"+ (str)(21) +")"
        
        
        own["AnimSpeedCounter"]["Text"]="AnimSpeed - "+(str)(truncate(own["Armature"]["FinalAnimSpeed"],trunc))
        own["timer"]=0
def mouseControls():
    if own['mouseLock']==True:
        if own["MouseCont"].positive:
            halfW=bge.render.getWindowWidth()//2
            halfH=bge.render.getWindowHeight()//2
            pos=own["MouseCont"].position
            mult=0.001
            #if own["MouseCont"].positive:
            MouseVel=[(halfW-pos[0])*mult,(halfH-pos[1])*mult]
            
            ##print(MouseVel)
            #bge.render.getWindowHeight()
            bge.render.getWindowHeight()
            own["VROBJECT"].applyRotation([0,0,MouseVel[0]],0)
            if own["SceneLogic"]['startedVR']==False:
                own["VROBJECT"].applyRotation([MouseVel[1],0,0],1)
            
            bge.render.setMousePosition(halfW,halfH)
            
            
            
            #bge.render.getWindowHeight()
            ##print(dir(bge.render))
            ##print(bge.render.RAS_OFS_RENDER_BUFFER)
            #bge.render.showProperties(1)
            #bge.render.showProfile(1)
#def run():
    ##print(own["mouseLock"])
    #own["FPScounter"].color=[0,0,1,1]
    #jiggleHandler()
    #debugInfo()
    #editMesh()
    #display()
    #mouseControls()
    ##print(len(own["HairsOBJs"]))
    #for OBJ in own["HairsOBJs"]:
        
    #    changeObjectColor(OBJ)

    