import GameLogic
import bge
import aud
import os
import random
import math
from mathutils import Vector
from mathutils import Matrix
from mathutils import Euler 
import numpy
import blenderVR


def init():
    #bge.render.showMouse(True)
    obScaler(-100.0,"hairScaler","hairScaleDisp", "Hair Scale - ")
    cont = bge.logic.getCurrentController()
    own = cont.owner
    own['UIenabled']=True
    scene=GameLogic.getCurrentScene()

    # making menu farer
    scene.objects["screenInterface"].position=Vector([-1.95, 0.5955, 0.8511])
    scene.objects["screenInterface"].scaling=Vector([1, 1, 1])
    
    own["nonVrCamera"] = GameLogic.getCurrentScene().objects['nonVrCamera']
    #scene.active_camera=own["nonVrCamera"]        
    own['buttonAction']=""
    own['animButtonAdder']=scene.objects["animButtonAdder"]
    scene.objects['ColPickBar']['HUE']=[1.0,0.0,0.0]
    
    scene.objects['ColPickCanvas'].meshes[0].getVertex(0, 1).color = [1.0,0.0,0.0, 1.0]
    
    #own['sexcharacterhead']=GameLogic.getCurrentScene().objects['sexcharacterhead']
    #own['viewerpoint']=GameLogic.getCurrentScene().objects['viewerpoint']
    scene.objects['Point'].energy=random.uniform(0,0.15)
    scene.objects['lightPower']['Text']="Camera Light - "+ (str)("{0:.3f}".format(scene.objects['Point'].energy))
    scene.objects['spotlightPower']['Text']="Spot Light - "+ (str)("{0:.3f}".format(scene.objects['Point.001'].energy))
    
    
    own['setColorOB']=scene.objects["setColor"]
    own['uiUpdatePeriod']=0
    own['CURSOR']=scene.objects["CURSOR"]
    own['braCounter']=1
    own['lastAnimFrame']=0
    own['lastObjectPicked']=None
    renderTextureInit()
    renderTextureRefresh("Texture","screenInterface")
    
    scene.objects['SceneLogic']['mouseLock']=False      
    
    uiOBJs = []    
    for obj in scene.objects:
        if "UI" in obj:
            uiOBJs.append(obj)
    own["UIOBJs"]=uiOBJs
    
    topclothmeshes = [] 
    bottomclothmeshes = [] 
    accessclothmeshes = [] 
    fronthairclothmeshes = [] 
    backhairclothmeshes = [] 
    footclothmeshes=[]
    
    createTexture("GIRLOBJECT-LP","Face","lipstick",1024,1024,"lipstick Camera",5)
    renderTextureRefresh("lipstick","GIRLOBJECT-LP")
    
    top=scene.objects['topClothManager']
    bottom=scene.objects['bottomClothManager']  
    
    top['startPos']=Vector([top.localPosition.x,top.localPosition.y,top.localPosition.z])
    bottom['startPos']=Vector([bottom.localPosition.x,bottom.localPosition.y,bottom.localPosition.z])
    
    
    zoffsetOBJs = []
    for obj in scene.objects:
        if "Cloth" in obj:
            if obj["Cloth"]=="top":               
                topclothmeshes.append(obj.meshes[0].name)
            if obj["Cloth"]=="bottom":               
                bottomclothmeshes.append(obj.meshes[0].name)
            if obj["Cloth"]=="access":
                accessclothmeshes.append(obj.meshes[0].name)
            if obj["Cloth"]=="fronthair":
                fronthairclothmeshes.append(obj.meshes[0].name)
            if obj["Cloth"]=="backhair":
                backhairclothmeshes.append(obj.meshes[0].name)
            if obj["Cloth"]=="foot":
                footclothmeshes.append(obj.meshes[0].name)
            obj.endObject()
            
            
    misclist = []
    misclist.append(scene.objects['eyes'].name)
    own['zoffsetOBJs']=zoffsetOBJs

    addListButtons(topclothmeshes,"topClothManager-",Vector([0,0,0]))
    addListButtons(bottomclothmeshes,"bottomClothManager-",Vector([1,0,0]))
    addListButtons(accessclothmeshes,"accClothManager-",Vector([2,0,0]))
    addListButtons(footclothmeshes,"footClothManager-",Vector([3,0,0]))
    addListButtons(fronthairclothmeshes,"fronthairClothManager-",Vector([4,0,0]))
    addListButtons(backhairclothmeshes,"backhairClothManager-",Vector([4,1.2,0]))
    addListButtons(misclist,"miscColors-",Vector([5,0,0]))
    addListButtons(["GIRLOBJECT-LP","Lipstick","EyeBrows"],"miscColors-",Vector([5,.26,0]))

    #moveButtonsOffscreen("Clothbuttons")

    own['animButtonsHidden']=False
    addAnimButtons()
    
    moveButtonsOffscreen('tmpanimBUTTON')
    
    own["buttonOBJs"]=None
    relistButtons()
    ##print(uiOBJs)
    vrScale(0)
    own['scaleTimer']=0.0
    own['startGirlOBMesh']=scene.objects["GIRLOBJECT-LP"].meshes[0].name


    
def clothSwitcher():
    
    scene=GameLogic.getCurrentScene()
    cont = bge.logic.getCurrentController()
    own = cont.owner
    #print(own['buttonAction'].split('-')[0])
    selectedCLothManager=scene.objects[own['buttonAction'].split('-')[0]]
    selectedCLothManager.replaceMesh(own['buttonAction'].replace(selectedCLothManager.name+"-",""))
    own['lastObjectPicked']=selectedCLothManager
    
    #setClothColor()
    if "topClothManager" in own['buttonAction']:
        if "Full " in own['buttonAction']:
            scene.objects["GIRLOBJECT-LP"].replaceMesh("1.No Accessory_Cloth-LP-mesh")
        else:
            scene.objects["GIRLOBJECT-LP"].replaceMesh(own['startGirlOBMesh'])
            
    if "topClothManager" in own['buttonAction']:
        if "No Top" in own['buttonAction'] or "Exposed" in own['buttonAction'] or "Full " in own['buttonAction']:
            breastConfine(False)
        else:
            breastConfine(True)
    #own['buttonAction']
    
    #topClothManager
    
    
def zoffsetCloths():#not used
    cont = bge.logic.getCurrentController()
    own = cont.owner
    scene=GameLogic.getCurrentScene()
    
    
    top=scene.objects['topClothManager']
    bottom=scene.objects['bottomClothManager']  
    viewer=scene.objects['nonVrCamera']  
    accClothManager=scene.objects['accClothManager']
    
    top.localPosition=top['startPos']
    bottom.localPosition=bottom['startPos']
    
    #bottom.position=bottom.position+Vector([.84,.0073,.1])+((viewer.position-accClothManager.position)*.01)
    
    #bottom.localPosition=Vector([0,0,0])
    
    #print(bottom['startPos'])

def loop(): 
    ##print(dir(bge.render.showProperties))
    cont = bge.logic.getCurrentController()
    own = cont.owner
    scene=GameLogic.getCurrentScene()
    
    #zoffsetCloths()
    
    own['leftClick']=cont.sensors['leftMouse']
    own['mouseOver']=cont.sensors['mouseover']

    own['Keyboard']=cont.sensors['Keyboard']

        
    
    
    #testOBJ = scene.objects['Point.001']
    ##print(dir(testOBJ))
    ##print(testOBJ.shadowMatrix)
    #testOBJ.shadowMapType
    #import openvr
    
    ##print(openvr.VRControllerState_t.rAxis )
    
    mouseCursor()
    ##print(own["buttonOBJs"])
    if(own['uiUpdatePeriod']<3):
        renderTextureRefresh("Texture","screenInterface")   
        
        own['uiUpdatePeriod']+=1
        if own['uiUpdatePeriod']==2:
            own['buttonAction']=''
    if(own['braCounter']==10):
        
        
        
        ArmatureOB = scene.objects['Armature']
        try:
            cont.actuators['Action'].action="SEX"+(str)(ArmatureOB['CurrentAction'])
        except:
            #addDebugaddDebugInfo("failed acction set..")
            print()
        ArmatureOB['AnimFrame']=own['lastAnimFrame']
        
    if(own['braCounter'])<12:
        
        own['braCounter']+=1
        
    
    
    if (own['Keyboard'].status==3):
        endScene()
        
    if(own['leftClick'].status==3):
        relistButtons()
        resetButtonScale()

    if(own['mouseOver'].positive or own['leftClick'].status==3 or own['leftClick'].positive):
        renderTextureRefresh("Texture","screenInterface")
            
    if (own['leftClick'].positive):
        
        ray = own['CURSOR'].rayCast(own['CURSOR'].position, own['CURSOR'].position-Vector([0,0,+1]), 1, "BUTTON", 0, 1, 0)

        if ray[0] != None:            
        
            preScale = ray[0].localScale
            ray[0].localScale=Vector([preScale.x,preScale.y,-5])
            own['buttonAction']=ray[0]['BUTTON']
            #print(own['buttonAction'])
            
            if "_Cloth-LP-mesh" in own['buttonAction'] or "miscColors-" in own['buttonAction']:   
                own['setColorOB'].position=ray[0].position  
            
    if own['buttonAction'] == "speedSlider":        
        adjustAnimSpeed(ray)

        
    if "SEX" in own['buttonAction']:        
        setSexAnim()

    
    if "startVR" in own['buttonAction']:        
        VRstarter()  

    if "_Cloth-LP-mesh" in own['buttonAction']:   
        
        clothSwitcher()
        
        
    if own['buttonAction'] == "pose" and own['leftClick'].status==3:        
        togglePoseButtons()

    if own['buttonAction'] == "vrScaleDown" and own['leftClick'].positive:
        vrScale(-1.0)

    if own['buttonAction'] == "vrScaleUp" and own['leftClick'].positive:
        vrScale(1.0)
        
        
    if own['buttonAction'] == "fovDown" and own['leftClick'].positive:
        nonvrFOV(-1.0)
    if own['buttonAction'] == "fovUp" and own['leftClick'].positive:
        nonvrFOV(1.0)
        
    if own['buttonAction'] == "breastDown" and own['leftClick'].positive:
        breastScaler(-1.0)
    if own['buttonAction'] == "breastUp" and own['leftClick'].positive:
        breastScaler(1.0)
    if own['buttonAction'] == "hairDown" and own['leftClick'].positive:
        obScaler(-1.0,"hairScaler","hairScaleDisp", "Hair Scale - ")
    if own['buttonAction'] == "hairUp" and own['leftClick'].positive:
        obScaler(1.0,"hairScaler","hairScaleDisp", "Hair Scale - ") 
    #if own['buttonAction'] == "Donate" and own['leftClick'].status==3:
     #   donatePage()       

    if own['buttonAction'] == "penisDown" and own['leftClick'].positive:
        miscSize(0.995,"penisSize")
    if own['buttonAction'] == "penisUp" and own['leftClick'].positive:
        miscSize(1.005,"penisSize")    
        
    if own['buttonAction'] == "headDown" and own['leftClick'].positive:
        miscSize(0.998,"headSize")
    if own['buttonAction'] == "headUp" and own['leftClick'].positive:
        miscSize(1.002,"headSize")         
        
    if own['buttonAction'] == "colorpickerbar" and own['leftClick'].positive:
        ColorPickerBar()
    if own['buttonAction'] == "colorpickercanvas" and own['leftClick'].positive:
        ColorPickerCanvas()
        
    if own['buttonAction'] == "POV" and own['leftClick'].status==3:
        povlock()   
    if own['buttonAction'] == "resetVRpos" and own['leftClick'].status==3:
        resetVRpos()   
    
    if own['buttonAction'] == "miscColors-eyes" and own['leftClick'].status==3:
        own['lastObjectPicked']=scene.objects['eyes']
    if own['buttonAction'] == "miscColors-GIRLOBJECT-LP" and own['leftClick'].status==3:
        own['lastObjectPicked']=scene.objects['GIRLOBJECT-LP']
        
    if own['buttonAction'] == "miscColors-Lipstick" and own['leftClick'].status==3:
        own['lastObjectPicked']=scene.objects['Lipstick']
    if own['buttonAction'] == "miscColors-EyeBrows" and own['leftClick'].status==3:
        own['lastObjectPicked']=scene.objects['EyeBrows-LP']
        
        
    if own['buttonAction'] == "camlightDown" and own['leftClick'].positive:
        camLightupdown(0.98)
    if own['buttonAction'] == "camlightUp" and own['leftClick'].positive:
        camLightupdown(1.02)   
        
    if own['buttonAction'] == "spotlightDown" and own['leftClick'].positive:
        spotLightupdown(0.98)
    if own['buttonAction'] == "spotlightUp" and own['leftClick'].positive:
        spotLightupdown(1.02)   

        
    if own['buttonAction'] == "hide" and own['leftClick'].status==3:
        endScene()
        
    
    if own['leftClick'].status==3:        
        own['uiUpdatePeriod']=0        
        
def camLightupdown(direction):
    cont = bge.logic.getCurrentController()
    own = cont.owner
    scene=GameLogic.getCurrentScene()
    scene.objects['Point'].energy=scene.objects['Point'].energy*direction
    scene.objects['lightPower']['Text']="Camera Light - "+ (str)("{0:.3f}".format(scene.objects['Point'].energy))
    
def spotLightupdown(direction):
    cont = bge.logic.getCurrentController()
    own = cont.owner
    scene=GameLogic.getCurrentScene()
    scene.objects['Point.001'].energy=scene.objects['Point.001'].energy*direction
    scene.objects['spotlightPower']['Text']="Spot Light - "+ (str)("{0:.3f}".format(scene.objects['Point.001'].energy))

    
def miscSize(direction,objectstr):
    cont = bge.logic.getCurrentController()
    own = cont.owner
    scene=GameLogic.getCurrentScene()
    scene.objects[objectstr].localScale=scene.objects[objectstr].localScale*direction
    
    
def resetVRpos():
    scene=GameLogic.getCurrentScene()
    cont = bge.logic.getCurrentController()
    own = cont.owner
    viewer=GameLogic.getCurrentScene().objects['headtrackpos'] #this one moves based on VR inputs
    shoulder=GameLogic.getCurrentScene().objects['headtrackrot'] #this one moves based on VR rotation
    VROBJECT=GameLogic.getCurrentScene().objects['VROBJECT']#this is the root object
    arma=GameLogic.getCurrentScene().objects['Armature']
    
    positiondif=VROBJECT.worldPosition-viewer.worldPosition
    
    #rotationdif=viewer.orientation-shoulder.orientation
    rotationdif=viewer.orientation.to_euler().z-shoulder.orientation.to_euler().z
    
    if "preVRPos" in arma:
        positiondif=VROBJECT.worldPosition-arma["preVRPos"]
        #rotationdif=viewer.orientation.to_euler().z-shoulder.orientation.to_euler().z
    GameLogic.getCurrentScene().objects['Armature']['rotoffs']=rotationdif
    
    GameLogic.getCurrentScene().objects['Armature']['posoffs']=positiondif

    #addDebugInfo(positiondif)
    #print(GameLogic.getCurrentScene().objects['Armature']['rotoffs'])
    #scene.objects['headtrackpos'].position=newpos
    #scene.objects['headtrackrot'].orientation=q

def povlock():
    scene=GameLogic.getCurrentScene()
    cont = bge.logic.getCurrentController()
    armaOBJ=GameLogic.getCurrentScene().objects['Armature']
    armaOBJ['POVLock']= not armaOBJ['POVLock']
    
def setClothColor():
    scene=GameLogic.getCurrentScene()
    cont = bge.logic.getCurrentController()
    own = cont.owner
    if own['lastObjectPicked']!=None:
        ColPickBar=scene.objects['ColPickBar']
        ColPickCanvas=scene.objects['ColPickCanvas']
        value=ColPickCanvas['brightness']        
        hue=ColPickBar['HUE']
        combine=[hue[0]*value,hue[1]*value,hue[2]*value]
        
        
        
        maxComine=max(combine)
        singleSaturation=ColPickCanvas['saturation']
        saturation=[numpy.clip(combine[0]+(singleSaturation+combine[0]),0.0,maxComine),numpy.clip(combine[1]+(singleSaturation+combine[1]),0.0,maxComine),numpy.clip(combine[2]+(singleSaturation+combine[2]),0.0,maxComine)]
        #print(maxComine)
        #print(combine[0])
        #print(singleSaturation-combine[0])
        
        

        
        finalRGB=[
        saturation[0]*value*2.5,
        saturation[1]*value*2.5,
        saturation[2]*value*2.5
        ]      
        

        
        
        own['lastObjectPicked'].color=[finalRGB[0],finalRGB[1],finalRGB[2],1.0]
        if own['lastObjectPicked']==scene.objects['Lipstick']:
            renderTextureRefresh("lipstick","GIRLOBJECT-LP")

        

def ColorPickerBar():
    scene=GameLogic.getCurrentScene()
    cont = bge.logic.getCurrentController()
    own = cont.owner
    ColPickBar=scene.objects['ColPickBar']
    ColPickCanvas=scene.objects['ColPickCanvas']
    ColPickBardot=scene.objects['ColPickBardot']
    ray = own['CURSOR'].rayCast(own['CURSOR'].position, own['CURSOR'].position-Vector([0,0,+1]), 1, "BUTTON", 0, 1, 0)
    xBarPosition=ray[1][0]-ColPickBar.position.x
    locBarPos=ColPickBardot.localPosition
    ColPickBardot.localPosition=Vector([xBarPosition,locBarPos.y,locBarPos.z])    
    HUE=[0,0,0]    
    colorSectors=xBarPosition*6    
    sectorMath=colorSectors-(float((int)(colorSectors)))
    if((float((int)(colorSectors)))==0):
        HUE=[1.0,sectorMath,0]
    if((float((int)(colorSectors)))==1):
        HUE=[1.0-sectorMath,1.0,0]
    if((float((int)(colorSectors)))==2):
        HUE=[0,1.0,sectorMath]
    if((float((int)(colorSectors)))==3):
        HUE=[0,1.0-sectorMath,1.0]
    if((float((int)(colorSectors)))==4):
        HUE=[sectorMath,0,1.0]
    if((float((int)(colorSectors)))==5):
        HUE=[1.0,0,1.0-sectorMath]
    HUE = [max(HUE[0],0),max(HUE[1],0),max(HUE[2],0)]
    ColPickCanvas.meshes[0].getVertex(0, 1).color = [HUE[0], HUE[1], HUE[2], 1.0]
    ColPickBar['HUE']=HUE
    setClothColor()
    


def ColorPickerCanvas():
    scene=GameLogic.getCurrentScene()
    cont = bge.logic.getCurrentController()
    own = cont.owner
    ColPickBar=scene.objects['ColPickBar']
    ColPickCanvas=scene.objects['ColPickCanvas']
    ColPickCanvasdot=scene.objects['ColPickCanvasdot']
    ray = own['CURSOR'].rayCast(own['CURSOR'].position, own['CURSOR'].position-Vector([0,0,+1]), 1, "BUTTON", 0, 1, 0)
    xBarPosition=ray[1][0]-ColPickBar.position.x
    locPos=ray[1]-ColPickCanvas.position
    ColPickCanvasdot.localPosition=Vector([locPos.x,locPos.y,0])  

    ColPickCanvas['saturation']=1.0-locPos[0]
    ColPickCanvas['brightness']=locPos[1]*1.5  
    setClothColor()

    
    
#def donatePage():
#    import sys
#    cont = bge.logic.getCurrentController()
#    own = cont.owner
#    url=own["donate"]
#    if sys.platform=='win32':
#        os.startfile(url)
#    elif sys.platform=='darwin':
#        subprocess.Popen(['open', url])
#    else:
#        try:
#            subprocess.Popen(['xdg-open', url])
#        except OSError:
#            addDebugInfo('Link failed. Try again at: '+url)              #webbrowser.open("http://meatspin.com/")
            
#def addDebugInfo(toLog):
#    cont = bge.logic.getCurrentController()
#    own = cont.owner
#    scene=GameLogic.getCurrentScene()
#    #currentText=own['debugTextObject']['Text'].split('\n')
#    scene.objects['debugText']['Text']= (str)(toLog)
            
def obScaler(direction,OBnamestring,dispOBJ=None,dispText=None):
    cont = bge.logic.getCurrentController()
    own = cont.owner
    amount=0.01*direction
    scene=GameLogic.getCurrentScene()
    scaleOB = GameLogic.getCurrentScene().objects[OBnamestring]
    
    scaleOB.localScale=Vector([scaleOB.localScale.x+amount,scaleOB.localScale.y+amount,scaleOB.localScale.z+amount])
    
    if dispOBJ!=None:
        GameLogic.getCurrentScene().objects[dispOBJ]['Text']=dispText+(str)("{0:.2f}".format(scaleOB.localScale.x))

   
def breastScaler(direction):
    cont = bge.logic.getCurrentController()
    own = cont.owner
    amount=0.01*direction
    scene=GameLogic.getCurrentScene()
    breastScaler = GameLogic.getCurrentScene().objects['BreastScale']
    
    #scene.objects['BreastPhysR'].setCollisionMargin(.01)
    #scene.objects['BreastPhysR'].reinstancePhysicsMesh()
    #scene.objects['BreastPhysL'].localScale=Vector([breastScaler.localScale.x+amount,breastScaler.localScale.y+amount,breastScaler.localScale.z+amount])
    breastScaler.localScale=Vector([breastScaler.localScale.x+amount,breastScaler.localScale.y+amount,breastScaler.localScale.z+amount])
    scene.objects['breastScaleDisp']['Text']="Breast Scale - "+(str)("{0:.2f}".format(breastScaler.localScale.x))


def nonvrFOV(direction):
    cont = bge.logic.getCurrentController()
    own = cont.owner
    amount=0.3*direction
    scene=GameLogic.getCurrentScene()
    nonVRcam=GameLogic.getCurrentScene().objects['nonVrCamera']
    nonVRcam.fov=nonVRcam.fov+amount  

    GameLogic.getCurrentScene().objects['FOVindicator']['Text']="FOV - "+ (str)("{0:.1f}".format(nonVRcam.fov))
    uiscale=nonVRcam.fov*.006
    own.localScale=Vector([uiscale,uiscale,own.localScale.z])
    
def resetButtonScale():
    
    cont = bge.logic.getCurrentController()
    own = cont.owner
    for obj in own["buttonOBJs"]:
        obj.localScale=Vector([obj.localScale.x,obj.localScale.y,1])
def mouseCursor():
    
    cont = bge.logic.getCurrentController()
    own = cont.owner
    if(own['UIenabled']): #own['UIenabled']
        mpos=own['mouseOver'].position
    ##print(mpos)
        correct=0.2
        
        own['CURSOR'].localPosition=Vector([mpos[0]/bge.render.getWindowWidth(),-mpos[1]/bge.render.getWindowWidth(),0])
    
    
def createTexture(objectName,materialName,textureStoreName,resx,resy,sourceCamera,slot):
    
    cont = bge.logic.getCurrentController()
    own = cont.owner
    
    scene=GameLogic.getCurrentScene()
    obj=scene.objects[objectName]
    matID = bge.texture.materialID(obj, "MA"+materialName)
    texture = bge.texture.Texture(obj, matID, slot)
    
    obj[textureStoreName+"temp"] = bge.render.offScreenCreate(resx,resy,0,bge.render.RAS_OFS_RENDER_TEXTURE)
    texture.source = bge.texture.ImageRender(GameLogic.getCurrentScene(), scene.objects[sourceCamera], obj[textureStoreName+"temp"])
    obj[textureStoreName] = texture
    
def renderTextureInit():
    
    cont = bge.logic.getCurrentController()
    own = cont.owner
    
    scene=GameLogic.getCurrentScene()
    
    matID = bge.texture.materialID(own, "MAMaterial.009")
    texture = bge.texture.Texture(own, matID, 0)
    own["leftEyeRenderTexture"] = bge.render.offScreenCreate(1920,1080,0,bge.render.RAS_OFS_RENDER_TEXTURE)
    texture.source = bge.texture.ImageRender(GameLogic.getCurrentScene(), scene.objects["UICAM"], own["leftEyeRenderTexture"])
    own["Texture"] = texture
    
def renderTextureRefresh(TextureName,ObjectName):    
    cont = bge.logic.getCurrentController()
    #own = cont.owner
    scene=GameLogic.getCurrentScene()
    SceneLogicOB=scene.objects[ObjectName]
    SceneLogicOB[TextureName].refresh(True)
  
def vrScale(direction):
    cont = bge.logic.getCurrentController()
    own = cont.owner
    amount=0.0001*direction
    scene=GameLogic.getCurrentScene()
    cam1=GameLogic.getCurrentScene().objects['Camera.002']
    cam2=GameLogic.getCurrentScene().objects['Camera']
    
    cam1.localPosition=Vector([cam1.localPosition.x+amount,cam1.localPosition.y,cam1.localPosition.z])
    cam2.localPosition=Vector([cam2.localPosition.x-amount,cam2.localPosition.y,cam2.localPosition.z])
    eyeSeparation=cam1.getDistanceTo(cam2)
    GameLogic.getCurrentScene().objects['eyeSepDisp']['Text']="separation - "+ (str)("{0:.3f}".format(eyeSeparation))
            
def VRstarter():
        
    cont = bge.logic.getCurrentController()
    own = cont.owner
    scene=GameLogic.getCurrentScene()
    
    
    #print('starting VR')
    
    resetVRpos()
    own.localScale=Vector([2,2,2])
    blenderVR.init(scene.objects['SceneLogic'])
    own['buttonAction']=""
    own.removeParent()
    setVRUITransform()
    GameLogic.getCurrentScene().objects['VRButton'].endObject()
    GameLogic.getCurrentScene().objects['nonVRscaler'].endObject()
    
    relistButtons()
    
    
def setVRUITransform():
    
    cont = bge.logic.getCurrentController()
    own = cont.owner
    own.position=own["nonVrCamera"].position
    own.orientation=own["nonVrCamera"].orientation
    
def clothHider():#veryyy suspect
    
    cont = bge.logic.getCurrentController()
    own = cont.owner
    
    
    if (own['leftClick'].status==3):
        lookfortype=own['buttonAction'].replace("Cloth-Check","")
        #print('remove or add')
        for obj in GameLogic.getCurrentScene().objects:
            if "Cloth" in obj:
                if obj["Cloth"]==lookfortype:
                    if obj.visible:
                        if (obj["Cloth"]=='top'):
                            breastConfine(False)
                        obj.visible=False
                        #obj.endObject()
                    else:
                        if (obj["Cloth"]=='top'):
                            breastConfine(True)
                        obj.visible=True
    
def breastConfine(confined=True):
    
    cont = bge.logic.getCurrentController()
    own = cont.owner
    
    scene=GameLogic.getCurrentScene()
    ArmatureOB = scene.objects['Armature']
    braAct=cont.actuators['Action']
    own['lastAnimFrame']=ArmatureOB["AnimFrame"]
    
    
    
    
    if (confined):
        braAct.action="BraSettingIn"

        
    else:
        braAct.action="BraSettingOut"
    own['braCounter']=1
    
def setSexAnim():
    
    cont = bge.logic.getCurrentController()
    own = cont.owner
    if (own['leftClick'].status==3):
        GameLogic.getCurrentScene().objects['Armature']['CurrentAction']=int(own['buttonAction'].replace("SEX",""))
    #own['buttonAction']=""
                       
def togglePoseButtons():
    cont = bge.logic.getCurrentController()
    own = cont.owner
    
    if (own['leftClick'].status==3):
    
        moveButtonsOffscreen('tmpanimBUTTON')
    #print(own['animButtonsHidden'])
    own['buttonAction']=""
    
def moveButtonsOffscreen(typeOfButton):
    scene=GameLogic.getCurrentScene()
    cont = bge.logic.getCurrentController()
    own = cont.owner
    
    for obj in scene.objects:
        if typeOfButton in obj:
        
        
            if(obj[typeOfButton]==False):
                obj.localPosition=obj.localPosition+Vector([-10,0,0])
            if(obj[typeOfButton]==True):
                obj.localPosition=obj.localPosition+Vector([10,0,0]) 
            obj[typeOfButton]= not obj[typeOfButton]

            
            
def addListButtons(list,tmpButtonName,offset):
    offset=offset*0.75
    cont = bge.logic.getCurrentController()
    own = cont.owner
    scene=GameLogic.getCurrentScene()
    zButtonOffset=0
    buttonIndex=0
    buttonSpace=.2
 
    list.sort()
  
    for item in list:
        #print(item)
        lastButton = scene.addObject('animButton','buttonRef',0)
        lastButton.setParent(own['animButtonAdder'])
        lastButton[tmpButtonName]=True
        lastButton['BUTTON']=tmpButtonName+item
        lastButton.children[0]['Text']=item.replace("_Cloth-LP-mesh","")
        parentPos=own['animButtonAdder'].position
        lastButton.localPosition=Vector([offset.x,zButtonOffset+offset.y,.5+offset.z])
        zButtonOffset+=buttonSpace
        buttonIndex+=1
def addAnimButtons():
    cont = bge.logic.getCurrentController()
    own = cont.owner
    
    scene=GameLogic.getCurrentScene()
    sexlist = [# all actions are titled SEX1,SEX2,SEX3 etc. description index below correlate to SEXnumber
        'Default',
        'Legs Spread',
        'Cowgirl',
        'Missionary',
        'Doggy',
        'Huddled',
        'Masturbate',
        'Head Spinner',
        'Cowgirl',
        'Sideways',
        'On Knees',
        'Fingering',
        'Blowjob1',
        'Countertop',
        'Legs Spread',
        'Grind',
        'sideFuck',
        'Handjob',
        'Blowjob2',
        'on Machine',
        'Cowgirl2',
        'Leg Up on Counter',
        'missionary2',
        '69',
        'test'
    ]
    zButtonOffset=0
    buttonIndex=0
    buttonSpace=.2
    for sexPos in sexlist:
        lastButton = scene.addObject('animButton','buttonRef',0)
        
        lastButton.setParent(own['animButtonAdder'])
        lastButton['tmpanimBUTTON']=True
        lastButton['BUTTON']="SEX"+str(buttonIndex)
        lastButton.children[0]['Text']=sexPos
        parentPos=own['animButtonAdder'].position
        lastButton.localPosition=Vector([1.5,parentPos.z+zButtonOffset+2.5,.75])
        zButtonOffset+=buttonSpace
        buttonIndex+=1
    relistButtons()
    own['animButtonsHidden']=False
    
def relistButtons():
    
    scene=GameLogic.getCurrentScene()
    cont = bge.logic.getCurrentController()
    own = cont.owner
    
    buttonOBJs = []    
    for obj in scene.objects:
        if "BUTTON" in obj:
            buttonOBJs.append(obj)  
    own["buttonOBJs"]=buttonOBJs    
    

    for obj in scene.objects:
        if "Text" in obj:
            
            obj.resolution=5.0
    
def adjustAnimSpeed(ray):
    
    cont = bge.logic.getCurrentController()
    own = cont.owner
    scene=GameLogic.getCurrentScene()
    
    ray[0].localScale=Vector([ray[0].localScale.x,ray[0].localScale.y,1])
    
    max=10
    mpos=((own['mouseOver'].position[0]/bge.render.getWindowWidth())*6)-.4

    
    scene.objects['speedSliderNob'].localPosition=Vector([mpos,0,0])
    #print(scene.objects['speedSliderNob'].localPosition)
    
    speed =scene.objects['speedSliderNob'].localPosition.x
    
    scene.objects['Armature']['AnimSpeed']=speed*1.4
    own['buttonAction']=""
    
    
def endScene():
    
 
    cont = bge.logic.getCurrentController()
    own = cont.owner
    scene=GameLogic.getCurrentScene()
    if (own['UIenabled']==True):
        halfW=bge.render.getWindowWidth()//2
        halfH=bge.render.getWindowHeight()//2
        bge.render.setMousePosition(halfW,halfH)
        own.visible=False
        own['CURSOR'].localPosition=Vector([own['CURSOR'].localPosition.x,0,0])
        

        scene=GameLogic.getCurrentScene()
        
      
        scene.objects['SceneLogic']['mouseLock']=True
        own['UIenabled']=False
        
        #bge.render.showMouse(False)
    else:
        if(scene.objects['SceneLogic']['startedVR']==1):
            setVRUITransform()
        own['UIenabled']=True
        own.visible=True
        cont = bge.logic.getCurrentController()
        own = cont.owner
        
        scene.objects['SceneLogic']['mouseLock']=False
    own['buttonAction']=""
 
    
    