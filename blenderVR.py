from bge import logic as g
import mathutils
import math
from numpy import *
import bge
import sys
import time
import openvr
import os
import GameLogic
#import ctypes




def init(own=bge.logic.getCurrentController().owner):
    
    scene = bge.logic.getCurrentScene()
    own['startedVR']=0
    scene['startedVR']=0
    print(own.actuators)
    try:
        own['startedVR']=1
        scene['startedVR']=1
        #scene.active_camera=scene.cameras['Camera'] ##The active camera can't be used for offscreen rendering
        print("start ran fine")
        own["posOBJ"] = g.getCurrentScene().objects['headtrackpos']
        own["rotOBJ"] = g.getCurrentScene().objects['headtrackrot']
        own["Camera"] = g.getCurrentScene().objects['Camera']
        scene["CameraLeft"] = g.getCurrentScene().objects['Camera']
        scene["CameraRight"] = g.getCurrentScene().objects['Camera.002']
        scene["CameraLeft"].near = 0.26
        scene["CameraRight"].near = 0.26
        
        #own["junkCamera"] = g.getCurrentScene().objects['junkCamera']
        scene.active_camera=g.getCurrentScene().objects['UICAM.001']
        #time.sleep(1.5)
        openvr.init(openvr.VRApplication_Scene)

        
        size = openvr.VRSystem().getRecommendedRenderTargetSize()
        width = size[0]
        height = size[1]    
        
        #own["nonVrCamera"].useViewport=False
        
        scene["leftEyeRenderTexture"] = bge.render.offScreenCreate(width,height,0,bge.render.RAS_OFS_RENDER_TEXTURE)
        scene["leftEyeSource"] = bge.texture.ImageRender(g.getCurrentScene(), scene["CameraLeft"], scene["leftEyeRenderTexture"])
        
        scene["rightEyeRenderTexture"] = bge.render.offScreenCreate(width,height,0,bge.render.RAS_OFS_RENDER_TEXTURE)
        scene["rightEyeSource"] = bge.texture.ImageRender(g.getCurrentScene(), scene["CameraRight"], scene["rightEyeRenderTexture"])
        #g.getCurrentScene()['__main__'] = [main]
    except Exception as e:
        scene.objects['debugText']['Text']=e
        
def main():
    scene = g.getCurrentScene()
    cont = bge.logic.getCurrentController()
    own = cont.owner
    #while not exitrequested:
    if own['startedVR']:
        poses_t = openvr.TrackedDevicePose_t * openvr.k_unMaxTrackedDeviceCount
        poses = poses_t()
        openvr.VRCompositor().waitGetPoses(poses, len(poses), None, 0)
        hmd_pose = poses[openvr.k_unTrackedDeviceIndex_Hmd]
        #controller_pose = poses[openvr.nControllerDeviceIndex]
        #print(hmd_pose.mDeviceToAbsoluteTracking)
        #trackMatrixCont = controller_pose.mDeviceToAbsoluteTracking
        trackMatrix = hmd_pose.mDeviceToAbsoluteTracking
        
        q = [0,0,0,0]
        
        q[0] = sqrt(fmax(0, 1 + trackMatrix[0][0] + trackMatrix[1][1]+ trackMatrix[2][2])) / 2;
        q[1] = sqrt(fmax(0, 1 + trackMatrix[0][0] - trackMatrix[1][1] - trackMatrix[2][2])) / 2;
        q[2] = sqrt(fmax(0, 1 - trackMatrix[0][0] + trackMatrix[1][1] - trackMatrix[2][2])) / 2;
        q[3] = sqrt(fmax(0, 1 - trackMatrix[0][0] - trackMatrix[1][1] + trackMatrix[2][2])) / 2;
        q[1] = copysign(q[1], trackMatrix[2][1] - trackMatrix[1][2]);
        q[2] = copysign(q[2], trackMatrix[0][2] - trackMatrix[2][0]);
        q[3] = copysign(q[3], trackMatrix[1][0] - trackMatrix[0][1]);
                    
        multiplier=1
        QuatCorrect=[1,0,0,0]

        newpos=[trackMatrix[0][3]*multiplier,trackMatrix[2][3]*multiplier,trackMatrix[1][3]*multiplier]
        newpos=[newpos[1],newpos[0],newpos[2]]
        
        scene.objects['headtrackpos'].position=newpos# + scene.objects['Armature']['posoffs']
        scene.objects['headtrackrot'].orientation=q# + scene.objects['Armature']['rotoffs']
        #if 'posoffs' in scene.objects['Armature']:
        #    scene.objects['headtrackpos'].position=newpos + scene.objects['Armature']['posoffs']
        #    scene.objects['headtrackrot'].orientation=q + scene.objects['Armature']['rotoffs']
            
        leftCamera = scene.objects['Camera']
        rightCamera = scene.objects['Camera.002']

        leftCamera.projection_matrix = openvr.VRSystem().getProjectionMatrix(openvr.Eye_Left, leftCamera.near, leftCamera.far, 0)
        rightCamera.projection_matrix = openvr.VRSystem().getProjectionMatrix(openvr.Eye_Right, rightCamera.near, rightCamera.far, 0)
        
        #TODO: Adjust camera position relative to head based on openvr.VRSystem().getEyeToHeadTransform()

        
        exitrequested = g.NextFrame()
        
        leftEyeSource = scene["leftEyeSource"]
        leftEyeSource.refresh()
        leftEyeTextureT = openvr.Texture_t(scene["leftEyeRenderTexture"].color, openvr.API_OpenGL, openvr.ColorSpace_Gamma)
        openvr.VRCompositor().submit(openvr.Eye_Left, leftEyeTextureT)
        
        rightEyeSource = scene["rightEyeSource"]
        rightEyeSource.refresh()
        rightEyeTextureT = openvr.Texture_t(scene["rightEyeRenderTexture"].color, openvr.API_OpenGL, openvr.ColorSpace_Gamma)
        openvr.VRCompositor().submit(openvr.Eye_Right, rightEyeTextureT)
        
    else:
        #just call NextFrame
        exitrequested = g.NextFrame()
    #sexcharacterhead=scene.objects['sexcharacterhead']//handled in AM.py
    #viewerpoint=scene.objects['viewerpoint']
    #if viewerpoint['lockPOV']==True:
    #    viewerpoint.position=sexcharacterhead.position
def quit():
    cont = bge.logic.getCurrentController()
    own = cont.owner
    if own["startedVR"] == 1:
        openvr.shutdown()
        
    bge.logic.endGame()
    
    
    
    