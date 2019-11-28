from bge import logic
import openvr
import mathutils
import math
from numpy import *

def main():
    scene = logic.getCurrentScene()
    scene['startedVR']=False
    exitrequested = False
    while not exitrequested:
        if scene['startedVR']:
            poses_t = openvr.TrackedDevicePose_t * openvr.k_unMaxTrackedDeviceCount
            poses = poses_t()
            openvr.VRCompositor().waitGetPoses(poses, len(poses), None, 0)
            hmd_pose = poses[openvr.k_unTrackedDeviceIndex_Hmd]
            #controller_pose = poses[openvr.nControllerDeviceIndex]
            ##print(hmd_pose.mDeviceToAbsoluteTracking)
            #trackMatrixCont = controller_pose.mDeviceToAbsoluteTracking
            trackMatrix = hmd_pose.mDeviceToAbsoluteTracking
            
            q = [0,0,0,0]
            
            q[0] = sqrt(fmax(0, 1 + trackMatrix[0][0] + trackMatrix[1][1]+ trackMatrix[2][2])) / 2
            q[1] = sqrt(fmax(0, 1 + trackMatrix[0][0] - trackMatrix[1][1] - trackMatrix[2][2])) / 2
            q[2] = sqrt(fmax(0, 1 - trackMatrix[0][0] + trackMatrix[1][1] - trackMatrix[2][2])) / 2
            q[3] = sqrt(fmax(0, 1 - trackMatrix[0][0] - trackMatrix[1][1] + trackMatrix[2][2])) / 2
            q[1] = copysign(q[1], trackMatrix[2][1] - trackMatrix[1][2])
            q[2] = copysign(q[2], trackMatrix[0][2] - trackMatrix[2][0])
            q[3] = copysign(q[3], trackMatrix[1][0] - trackMatrix[0][1])
                        
            multiplier=1
            QuatCorrect=[1,0,0,0]

            newpos=[trackMatrix[0][3]*multiplier,trackMatrix[2][3]*multiplier,trackMatrix[1][3]*multiplier]
            newpos=[newpos[1],newpos[0],newpos[2]]
            
            scene.objects['headtrackpos'].position=newpos# + scene.objects['Armature']['posoffs']
            scene.objects['headtrackrot'].orientation=q# + scene.objects['Armature']['rotoffs']
            if 'posoffs' in scene.objects['Armature']:
                posvect=scene.objects['Armature']['posoffs']
                scene.objects['headtrackpos'].position=newpos + [posvect.x,posvect.y,posvect.z]
                #scene.objects['headtrackrot'].orientation=Vector(q) + scene.objects['Armature']['rotoffs']
                #print("eh")
            leftCamera = scene.objects['Camera']
            rightCamera = scene.objects['Camera.002']
    
            leftCamera.projection_matrix = openvr.VRSystem().getProjectionMatrix(openvr.Eye_Left, leftCamera.near, leftCamera.far, 0)
            rightCamera.projection_matrix = openvr.VRSystem().getProjectionMatrix(openvr.Eye_Right, rightCamera.near, rightCamera.far, 0)
            
            #TODO: Adjust camera position relative to head based on openvr.VRSystem().getEyeToHeadTransform()

            
            exitrequested = logic.NextFrame()
            
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
            exitrequested = logic.NextFrame()
    #sexcharacterhead=scene.objects['sexcharacterhead']//handled in AM.py
    #viewerpoint=scene.objects['viewerpoint']
    #if viewerpoint['lockPOV']==True:
    #    viewerpoint.position=sexcharacterhead.position
    
main()
