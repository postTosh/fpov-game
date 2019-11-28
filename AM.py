import GameLogic
import bge
import aud
import os
import random
from mathutils import Vector
from mathutils import Euler

cont = bge.logic.getCurrentController()
own = cont.owner

bge.render.setFullScreen(True)
bge.render.setVsync(bge.render.VSYNC_OFF)

def playSound(soundfilepath,playFromObject,randpitchmin,randpitchmax,randvolmin,randvolmax,stopAudioBeforeContinue,device = aud.device()):
    
    if randpitchmax<=randpitchmin:
        randpitchmax=randpitchmin+1
    if randvolmax<=randvolmin:
        randvolmax=randvolmin+1

    if 'moan' in soundfilepath:
        #if(own['currentMoan']<own['maxfilesmoan']):
            #own['currentMoan']+=1
        #else:
        #    own['currentMoan']=0
        #soundfilepath = own['soundpath'] + 'female moans\\cleaned\\'+str(own['currentMoan'])+'.mp3'
        #own['facimation']=own['currentMoan']
        addBreath(0.005)
        browLerperStart(random.uniform(-0.001,0.002),random.uniform(0.2,1.0),random.uniform(0.2,1.0))
        #own['camShakeIntensity']=own['camShakeIntensity']+0.002
        
        if(random.randrange(0,6)<1):
           own['panting']=True
        addDebugInfo(soundfilepath)
        #if(random.randrange(0,10)<1):#chance to make no sound
        #    return

            
    #device
    sound = aud.Factory.file(soundfilepath)    
    
    randpitch = random.randrange(randpitchmin,randpitchmax)
    
    sound = sound.pitch(float(randpitch)*.02)

    #device.stopAll()
    randvol = random.randrange(randvolmin,randvolmax)
    
    
    #Set the distance model (the default one does not work)
    device.distance_model = aud.AUD_DISTANCE_MODEL_LINEAR_CLAMPED
    
    #Set the listener position
    device.listener_location = own['Viewer'].worldPosition
    
    #Set the listener orientation
    device.listener_orientation = own['Viewer'].worldOrientation.to_quaternion()
    

    soundHand = device.play(sound)
    #hand.volume=randvol*.01

    
    
    if 'moan' in soundfilepath:
        if 'voiceAudioHandle' in own:
            own['voiceAudioHandle'].stop()
        own['voiceAudioHandle']=soundHand


    
    
    #Set sound to 'not relative'
    soundHand.relative = False
    
    #Set Sound source position & Orientation
    soundHand.location = playFromObject.worldPosition
    soundHand.orientation = playFromObject.worldOrientation.to_quaternion()
    
    #Setting other values to make the sound 'fade away'
    soundHand.distance_maximum = 5
    soundHand.distance_reference= 0
    #print(type(soundHand).__name__)
    return soundHand



def init():
    
    own['faceAnimDebugCount']=0
    if own['starter']==False:
        
        #GameLogic.setLogicTicRate(75)
        own['headTrackTimeout']=0
        own['cont']=cont
        own['CharacterOBJs'] = []
        for OBJ in GameLogic.getCurrentScene().objects:
            if 'characterOBJ' in OBJ:
                own['CharacterOBJs'].append(OBJ)
        own['randomMoanNum']=1  
        own['randomStop']=1.0
        own['cameraDistance']=-0.0
        own['changetrackeranimationbuffertime']=0
        own['CameraDolly']= GameLogic.getCurrentScene().objects['CameraDolly']
        own['posOBJ'] = GameLogic.getCurrentScene().objects['headtrackpos']
        own['rotOBJ'] = GameLogic.getCurrentScene().objects['headtrackrot']
        own['HeadLockCheck'] = GameLogic.getCurrentScene().objects['HeadLockCheck']
        #own['Cumdrop'] = GameLogic.getCurrentScene().objects['Cumdrop']
        #own['Cumtrail'] = GameLogic.getCurrentScene().objects['Cumtrail']
        own['HeadLockCheckTarget'] = GameLogic.getCurrentScene().objects['HeadLockCheckTarget']
        own['shoulderPhysicsPoint'] = GameLogic.getCurrentScene().objects['shoulderPhysicsPoint']
        own['pelvisPhysicsPoint'] = GameLogic.getCurrentScene().objects['pelvisPhysicsPoint']
        own['gagTarget'] = GameLogic.getCurrentScene().objects['gagTarget']
        own['cockTarget'] = GameLogic.getCurrentScene().objects['cockTarget']
        own['cockBase'] = GameLogic.getCurrentScene().objects['cockBase']
        own['sceneact'] = cont.actuators['Scene']
        own['panting']=False
        own['animationSet']=False
        own['debugTextObject']=GameLogic.getCurrentScene().objects['debugText']
        own['randomvoicePitch']=1.0
        own['randomVoiceVolume']=1.0
        own['randomvoicePitchActual']=1.0
        own['randomVoiceVolumeActual']=1.0
        own['randomvoicePitchSpeed']=.1
        own['randomVoiceVolumeSpeed']=.1
        
        own['sexcharacterhead']=GameLogic.getCurrentScene().objects['FOVEYES']

        eyeCauseOBJs = []
        for OBJ in GameLogic.getCurrentScene().objects:
            if 'eyeCausticParent' in OBJ:
                eyeCauseOBJs.append(OBJ)        
        own['causticMans']=eyeCauseOBJs
        
        own['screeninterface']=GameLogic.getCurrentScene().objects['screenInterface']
        own['lastSoundHandle']=''
        own['FaceAnimations']=own.actuators['FaceAnimations']
        own['breathAnimations']=own.actuators['breathAnimations']
        own['eyeScale']=1.0
        own['Arousal']= 0.5
        own['voiceAudioDevice'] = device = aud.device()
        own['Keys'] = Keys = cont.sensors['Keyboard']
        own['Viewer'] = GameLogic.getCurrentScene().objects['Viewerpoint']
        OrgasmOBJs = []
        for OBJ in GameLogic.getCurrentScene().objects:
            if 'OrgasmControl' in OBJ:
                OBJ['OrgasmOffsetVector']= Vector([0,0,0])
                OrgasmOBJs.append(OBJ)
        own['OrgasmOBJs'] = OrgasmOBJs
        own['Quiver']=0.0
        ##Arm controls
        #own['BOT'] = GameLogic.getCurrentScene().objects['BOT']
        own['RightHandJiggler'] = GameLogic.getCurrentScene().objects['RightHandJiggler']
        own['LeftHandJiggler'] = GameLogic.getCurrentScene().objects['LeftHandJiggler']
        own['PlayerWaistL'] = GameLogic.getCurrentScene().objects['PlayerWaistL']
        own['PlayerWaistR'] = GameLogic.getCurrentScene().objects['PlayerWaistR']       
        own['ellbowR'] = GameLogic.getCurrentScene().objects['ellbowR']
        own['ellbowL'] = GameLogic.getCurrentScene().objects['ellbowL'] 
        own['ShoulderHugPosR'] = GameLogic.getCurrentScene().objects['ShoulderHugPosR']
        own['ShoulderHugPosL'] = GameLogic.getCurrentScene().objects['ShoulderHugPosL']
           
        EyeControls = []
        for OBJ in GameLogic.getCurrentScene().objects:
            if 'blinkSpeed' in OBJ:
                EyeControls.append(OBJ)
        own['EyeControls'] = EyeControls
        own['controlBreath'] = GameLogic.getCurrentScene().objects['controlBreath']
        
        own['QuiverSubtract']=0.0
        
        
        own['LowerTeeth'] = GameLogic.getCurrentScene().objects['LowerTeeth']
        own['TeethTop'] = GameLogic.getCurrentScene().objects['TeethTop']
        
        own['cockTargetReturn'] = GameLogic.getCurrentScene().objects['cockTargetReturn']

        
        own['Vagina'] = GameLogic.getCurrentScene().objects['VaginaCone']
        own['Mouth'] = GameLogic.getCurrentScene().objects['Headpoint']
        own['obinsert'] = GameLogic.getCurrentScene().objects['insert']
        own['obinsert2'] = GameLogic.getCurrentScene().objects['insert2']
        own['obinserter'] = GameLogic.getCurrentScene().objects['inserter']
        own['obslosh'] = GameLogic.getCurrentScene().objects['slosh']
        own['obrub'] = GameLogic.getCurrentScene().objects['rub']
        own['obsuck'] = GameLogic.getCurrentScene().objects['suck']
        own['obHeadTrackerAnim'] = GameLogic.getCurrentScene().objects['HeadTrackerAnim']
        
        own['oldHeadVector'] = own['obHeadTrackerAnim'].position
        own['obHeadposition'] = GameLogic.getCurrentScene().objects['Cube.041']
        
        own['obFOVHEAD'] = GameLogic.getCurrentScene().objects['FOVHEAD']
        own['obFOVEYES'] = GameLogic.getCurrentScene().objects['FOVEYES']  
        own['obEyeTrack'] = GameLogic.getCurrentScene().objects['EyeTrack']
        
        own['baseLocalViewerPos']=own['CameraDolly'].localPosition
        own['PreviousViewerRotation']=own['Viewer'].orientation
        own['PreviousViewerPosition']=own['Viewer'].position
        
        own['soundpath'] = os.path.dirname(os.path.realpath(__file__)) + '\\sound\\sexSounds\\' 
        
        own['maxfilesvoicetexture'] = len(os.listdir(own['soundpath'] + 'voiceTextures\\'))+1
        own['maxfilesmoan'] = len(os.listdir(own['soundpath'] + 'female moans\\cleaned\\'))+1
        own['maxfilesbed'] = len(os.listdir(own['soundpath'] + 'bed\\'))+1
        own['maxfilesbrush'] = len(os.listdir(own['soundpath'] + 'brush\\'))+1
        own['maxfilesplop'] = len(os.listdir(own['soundpath'] + '\\ploppyslap\\'))+1
        own['maxfilespump'] = len(os.listdir(own['soundpath'] + 'pumps\\'))+1
        own['maxfilespant'] = len(os.listdir(own['soundpath'] + 'pants\\cleaned\\'))+1
        own['maxfilesrub'] = len(os.listdir(own['soundpath'] + 'rubs\\'))+1
        own['maxfilesgag'] = len(os.listdir(own['soundpath'] + 'gags\\'))+1
        own['maxfilesexhale'] = len(os.listdir(own['soundpath'] + 'breaths\\exhale\\'))+1
        own['maxfilesinhale'] = len(os.listdir(own['soundpath'] + 'breaths\\inhale\\'))+1
        own['maxfilesdrips'] = len(os.listdir(own['soundpath'] + 'drips\\'))+1
        
        own['currentMoan']=random.randrange(0,own['maxfilesmoan'])
        
        
        
        own['nonVrCamera']=GameLogic.getCurrentScene().objects['nonVrCamera']
        own['act'] = cont.actuators['Action']
        #own['cameraSmoothHelper']=GameLogic.getCurrentScene().objects['cameraSmoothHelper']
        
        #own['camShakeIntensity']=1
        own['randomCamPos']=Vector([0,0,0])
        own['randomCamOri']=Euler((1.5708, 0.0, 1.5708), 'XYZ')


        own['starter']=True
        
        
        
#def camShake(shakeamount,FallOffRefOBJ):
#    
#    maxDist=1.3
#    amplitude = (numpy.clip((FallOffRefOBJ.getDistanceTo(own['Viewer'])+0.0001)/maxDist,0,1)-1)*-1

#    own['camShakeIntensity']=own['camShakeIntensity']+(shakeamount*amplitude)
    
def interp(value,goal,speed):   
    result = value+((goal-value)*speed)
    return result
    
def voiceProcedurals():#voice processing
    #exhalesound=own['exhalesound']
    #soundHandle=own['voiceAudioDevice']

    
    #if voiceStarted():
     
    #own['randomvoicePitchSpeed']=.1
    #own['randomVoiceVolumeSpeed']=.1
     

    if 'voiceAudioHandle' in own and own['voiceAudioHandle'].pitch!=0:
        own['randomvoicePitchActual']=interp(own['randomvoicePitchActual'],own['randomvoicePitch'],own['randomvoicePitchSpeed'])
        own['randomVoiceVolumeActual']=interp(own['randomVoiceVolumeActual'],own['randomVoiceVolume'],own['randomVoiceVolumeSpeed'])
        
        own['voiceAudioHandle'].pitch=own['randomvoicePitchActual']
        own['voiceAudioHandle'].volume=own['randomVoiceVolumeActual']
        if random.randrange(0,20)<2:

            #if random.randrange(0,5)<2:

            #$soundhand = playSound(own['exhalesound'],own['Mouth'],30,50,40,40,False)
            #soundhand.volume=random.uniform(.9,1.2)
            #soundhand.pitch=random.uniform(1.5,3.2)

            own['randomvoicePitch']=random.uniform(1.0,1.05)
            own['randomVoiceVolume']=random.uniform(.1,1.2)
            own['randomvoicePitchSpeed']=random.uniform(0.0,0.2)
            own['randomVoiceVolumeSpeed']=random.uniform(0.0,0.2)
        if random.randrange(0,50)<2:
            own['randomVoiceVolume']=0
            own['randomVoiceVolumeSpeed']=random.uniform(0.0,0.2)
        if random.randrange(0,10)<8:
            own['voiceAudioHandle'].resume()
            #if random.randrange(0,10)<5:
            #only once!    playSound(own['moansound'],own['Mouth'],49,50,70,80,True,own['voiceAudioDevice'])
            
#def voiceStarted():
    #voicestatus=
    
def randomEyeScale():
    
    own['eyeScale']=random.uniform(0.5,2.00)  
    if random.randrange(0,100)<2:
        own['eyeScale']=random.uniform(0,1) 
def blink(blinkspd=0.2,blinkGoal=0.05,blinkReturnSpd=random.uniform(0,0.4),returnZGoal=0.00, type = 'both'):
    if(random.randrange(0,100)<25):
        blinkGoal=0.03
        blinkReturnSpd=0.03
    if(random.randrange(0,100)<10):
        type='bottom'
        blinkGoal=blinkGoal*2.0
    #addDebugInfo('Blink Goal is '+(str)(blinkGoal))
    for OBJ in own['EyeControls']: 
        OBJ['Blinking']=True
        if type=='both':
   
            
            OBJ['ZGoal']=blinkGoal
            OBJ['blinkSpeed']=blinkspd
            OBJ['returnBlinkSpeed']=blinkReturnSpd
            OBJ['returnZGoal']=returnZGoal
        
        
        if (type =='bottom'):
            OBJ['ZGoal']=returnZGoal
            if 'bottomBlink' in OBJ:

                OBJ['ZGoal']=blinkGoal
                OBJ['blinkSpeed']=blinkspd
                OBJ['returnBlinkSpeed']=blinkReturnSpd
                OBJ['returnZGoal']=returnZGoal

        
def randomEyeLidHeight(blinkReturnSpd,returnGoal):
    
    for OBJ in own['EyeControls']: 
        OBJ['returnBlinkSpeed']=blinkReturnSpd
        
        OBJ['returnZGoal']=returnGoal
def browLerperStart(zGoal=0,speedL=1.0,speedR=1.0):
    
    if(zGoal<0.001):
        blink(random.uniform(.01,.4),random.uniform(.03,.05),random.uniform(0.01,0.5),random.uniform(0.00,0.02))

    scene=GameLogic.getCurrentScene()
    cont = bge.logic.getCurrentController()
    own = cont.owner
    leftBrow=scene.objects['ControlBrowsLeft']
    rightBrow=scene.objects['ControlBrowsRight']
    leftBrow['zGoal']=zGoal
    rightBrow['zGoal']=zGoal
    leftBrow['speed']=speedL
    rightBrow['speed']=speedR 
    jawOffset=scene.objects['ControlBrowsRight']
    
    if random.randrange(0,10)<7:#randchin
        jawOffset['xGoal']=random.uniform(-0.000451,0.000451)
    
    if random.randrange(0,10)<3:#randombrow
        leftBrow['zGoal']=random.uniform(-0.001,0.001)
    if random.randrange(0,10)<3:#randombrow
        rightBrow['zGoal']=random.uniform(-0.001,0.001)
def browLerper():
    max=0.002
    min=-0.003
    scene=GameLogic.getCurrentScene()
    cont = bge.logic.getCurrentController()
    own = cont.owner
    eyeBrowControls=[scene.objects['ControlBrowsLeft'],scene.objects['ControlBrowsRight']]
    
    jawOffset=scene.objects['ControlBrowsRight']
    jawOffset['xGoal']=jawOffset['xGoal']*.995
    JawVelo=(jawOffset['xGoal']-jawOffset.position.x*0.051)#multiply this by the distance or something
    jawOffset.position=jawOffset.position+Vector([JawVelo,0,0]) 

    for eyeBrow in eyeBrowControls:
        velocity=(eyeBrow['zGoal']-eyeBrow.position.z*0.1)*eyeBrow['speed']#multiply this by the distance or something
        eyeBrow.position=eyeBrow.position+Vector([0,0,velocity])   
def breathLoops(exhale,inhale): #suspect
    
    decline=.98
    maxSpeed=0.005
    amplitude=(own['controlBreath']['breathSpeed']+.0000001)/maxSpeed
    zGoal=(0.05*amplitude)+0.02
    zStart=0.00
    target=(0.00071*amplitude)+0.0003  #breathSpeed
    fastestBreathRate=0.005
    
    own['controlBreath']['breathSpeed']=own['controlBreath']['breathSpeed']*decline
    prespeed=target+(own['controlBreath']['breathSpeed']*0.1)

    incr=150*prespeed
    
    if own['controlBreath']['breathSpeed']>fastestBreathRate:
        own['controlBreath']['breathSpeed']=fastestBreathRate
    
    
    if own['controlBreath'].position.z<zStart:
        own['controlBreath']['direction']=True
        if own['controlBreath']['directionChangeTrack']!=own['controlBreath']['direction']:
            own['breathAnimations'].action='NoDeform'
            own['breathAnimations'].layer=9

            if  own['panting']:
                inhalehandle=playSound(inhale,own['Mouth'],49,50,int(float(49)*amplitude),int(float(50)*amplitude),True)
                inhalehandle.volume=amplitude
                addBreath(0.005)
                own['breathAnimations'].action='BreathMouthDeform'
                own['FaceAnimations'].blendIn=50
   

    if own['controlBreath'].position.z>zGoal:
        own['controlBreath']['direction']=False
        if own['controlBreath']['directionChangeTrack']!=own['controlBreath']['direction']:

            if  own['panting']:
                exhalehandle=playSound(exhale,own['Mouth'],49,50,int(float(49)*amplitude),int(float(50)*amplitude),True)
                exhalehandle.volume=amplitude*0.5
                if 'voiceAudioHandle' in own:
                    if(own['voiceAudioHandle'].status):
                        exhalehandle.volume=0
                own['FaceAnimations'].blendIn=50
                #own['breathAnimations'].frame=1
                own['breathAnimations'].action='BreathMouthDeform'
                
           

    if own['controlBreath']['direction']==False:
        #inhale
        if own['controlBreath']['inverter']>-1.0:
            own['controlBreath']['inverter']=own['controlBreath']['inverter']-incr
        speed=prespeed*+own['controlBreath']['inverter'] 
        

    if own['controlBreath']['direction']==True:
        #exhale
        if own['controlBreath']['inverter']<1.0:
            own['controlBreath']['inverter']=own['controlBreath']['inverter']+incr
        speed=prespeed*+own['controlBreath']['inverter']    
        

    own['controlBreath']['directionChangeTrack']=own['controlBreath']['direction']
    
    own['controlBreath'].position = own['controlBreath'].position+Vector([0,0,speed])

    stomachsize = 1+(own['controlBreath'].position.z*5)
    own['controlBreath'].localScale = Vector([stomachsize,stomachsize,stomachsize])
def addBreath(amount):
    
    own['controlBreath']['breathSpeed']=own['controlBreath']['breathSpeed']+amount
def lidLoops():#suspect
    
    maxBlink = .05

    
    for OBJ in own['EyeControls']:  
    
        if OBJ['Blinking']: 
            if OBJ['ZGoal']-OBJ.position.z<0.01:
                OBJ['Blinking']=False

            lerpSpd=OBJ.position.z+((OBJ['ZGoal']-OBJ.position.z)*OBJ['blinkSpeed'])         
            
            OBJ.position = Vector([0,0,lerpSpd])
            OBJ['LastZPosition']=OBJ.position.z
            #OBJ.position = Vector([0,0,0])
            
        else:  

            lerpSpd=OBJ.position.z+((OBJ['returnZGoal']-OBJ.position.z)*OBJ['returnBlinkSpeed'])         
            

            OBJ.position = Vector([0,0,lerpSpd])
            OBJ['LastZPosition']=OBJ.position.z
def adjustEyeScale():#suspect
    
    scale=own['eyeScale']
    actualScale=own['obinsert'].worldScale.x
    steps=0.0051
    if own['obinsert'].worldScale.x>scale:
        own['obinsert'].worldScale=Vector([actualScale-steps,actualScale-steps,actualScale-steps])
    if own['obinsert'].worldScale.x<scale:
        own['obinsert'].worldScale=Vector([actualScale+steps,actualScale+steps,actualScale+steps])
def quivergasm():
    own['QuiverSubtract']=random.uniform(0.02,0.05)
    own['Quiver']=1.0
    
def quivergasmLoop(): 
    
    if own['Quiver']>0:
        
        if random.randrange(0,52)<2 or own['Quiver']==1.0:
            #if random.randrange(0,15)<2:
            #    squirt(own['Vagina'])
            for OBJ in own['OrgasmOBJs']:
                quiverRange=2.5*OBJ['OrgasmControl']*own['Quiver']
                randomVec= Vector([random.uniform(quiverRange*-1,quiverRange),random.uniform(quiverRange*-1,quiverRange),random.uniform(quiverRange*-1,quiverRange)])
                OBJ['OrgasmOffsetVector']= randomVec
                
                #OBJ.position=OBJ.position+randomVec
        own['Quiver']-=own['QuiverSubtract']
def calcMags(Number):
    finalNumber=(int)((float)(own['FinalAnimSpeed'])*(float)(Number))

    return finalNumber        
def focusSwitcher(OBJ, focusToThisOBJ):
    OBJ['Track']=focusToThisOBJ        
def OBJLerper(currentlyControlling):#suspect
    
    TrackedObjectOfInterest = GameLogic.getCurrentScene().objects[currentlyControlling['Track']] 
    VectorBearing=(TrackedObjectOfInterest.position-currentlyControlling.position)*currentlyControlling['trackSpeed']    
    currentlyControlling.position=currentlyControlling.position+VectorBearing
def HoldPlayer():
    
    armspeed=10
    if own['Viewer'].getDistanceTo(own['obFOVHEAD'])<0.0:
        
        own['RightHandJiggler']['speed']=armspeed
        own['LeftHandJiggler']['speed']=armspeed
        own['ellbowR']['speed']=armspeed
        own['ellbowL']['speed']=armspeed
        
        focusSwitcher(own['RightHandJiggler'],own['PlayerWaistR'])
        focusSwitcher(own['LeftHandJiggler'],own['PlayerWaistL'])
        focusSwitcher(own['ellbowR'],own['ShoulderHugPosR'])
        focusSwitcher(own['ellbowL'],own['ShoulderHugPosL'])

        
    else:#suspect
        
        focusSwitcher(own['RightHandJiggler'],own['RightHandJiggler']['Parent'])
        focusSwitcher(own['LeftHandJiggler'],own['LeftHandJiggler']['Parent'])
        focusSwitcher(own['ellbowR'],own['ellbowR']['Parent'])
        focusSwitcher(own['ellbowL'],own['ellbowL']['Parent'])    
def adjustHair():
    
    armspeed=5
    if own['Viewer'].getDistanceTo(own['obFOVHEAD'])<0.0:
        
        own['RightHandJiggler']['speed']=armspeed
        own['LeftHandJiggler']['speed']=armspeed
        own['ellbowR']['speed']=armspeed
        own['ellbowL']['speed']=armspeed
        
        focusSwitcher(own['RightHandJiggler'],own['PlayerWaistR'])
        focusSwitcher(own['LeftHandJiggler'],own['PlayerWaistL'])
        focusSwitcher(own['ellbowR'],own['ShoulderHugPosR'])
        focusSwitcher(own['ellbowL'],own['ShoulderHugPosL'])

        
    else:#suspect
        
        focusSwitcher(own['RightHandJiggler'],own['RightHandJiggler']['Parent'])
        focusSwitcher(own['LeftHandJiggler'],own['LeftHandJiggler']['Parent'])
        focusSwitcher(own['ellbowR'],own['ellbowR']['Parent'])
        focusSwitcher(own['ellbowL'],own['ellbowL']['Parent'])      
def FocusSystem():#suspect but probably needed
    eyeheadtrackspeedmin=0.03
    eyetrackspeedmax=0.2
    headtrackspeedmin=0.0081
    headtrackspeedmax=0.02
    
    #bge.render.drawLine( own['obFOVHEAD'].position+own['obFOVHEAD'].getAxisVect([0.0, -.20, 0.0]),own['Viewer'].position, [255,255,255])
    OBJLerper(own['obEyeTrack'])
    OBJLerper(own['obHeadposition'])
    maxheadtrackloss=200
    chanceofloss=2000
    KeepEyeContactAtDist=0.5
    ##eye switches

    if own['headTrackTimeout']>maxheadtrackloss:
        if random.randrange(0,500)<2:
            focusSwitcher(own['obHeadposition'],'Camera') 
            own['obEyeTrack']['trackSpeed']=random.uniform(eyeheadtrackspeedmin,eyetrackspeedmax)
            if random.randrange(0,100)<50:
                #if isInFront(own['obFOVHEAD'],own['Viewer']):
                focusSwitcher(own['obEyeTrack'],'Camera')
            else:
            
                #if isInFront(own['obFOVHEAD'],own['Viewer']):
                focusSwitcher(own['obEyeTrack'],'Camera.002')   
                if random.randrange(0,100)<75: 
                    focusSwitcher(own['obEyeTrack'],'dickpos')   
                

    ##HeadTracks and random attention loss
    own['headTrackTimeout']+=1
    
    if random.randrange(0,chanceofloss)<2 and own['Viewer'].getDistanceTo(own['obFOVEYES'].position)>KeepEyeContactAtDist:
        own['headTrackTimeout']=random.randrange(0,maxheadtrackloss)##random amount of time before she can look at you again
        objectlist = []
        for OB in GameLogic.getCurrentScene().objects:
            if 'POI' in OB:
                if isInFront(own['obFOVHEAD'],OB):
                    objectlist.append(OB)

        randomPOI = objectlist[random.randrange(0,len(objectlist))]

        own['obEyeTrack']['trackSpeed']=random.uniform(eyeheadtrackspeedmin,eyetrackspeedmax)
        own['obHeadposition']['trackSpeed']=random.uniform(headtrackspeedmin,headtrackspeedmax)
        if isInFront(own['obFOVEYES'],randomPOI):
            focusSwitcher(own['obEyeTrack'],randomPOI.name)
        if random.randrange(0,60)<50:## chance for head to track too
            focusSwitcher(own['obHeadposition'],randomPOI.name)   



            
def isInFront(referenceOB,targetOB):
    
    hit = referenceOB.rayCast(referenceOB, targetOB,0.0, referenceOB['limitType'],1,1,0) 

    if hit[0] != None:
        return False
    else:
        return True
def LerpCamera():#susppect. Does this need to run during VR?

        
    #factor = 1#how much to interpolate rotation frames
    own['Viewer'].orientation = own['rotOBJ'].orientation
    #own['Viewer'].position = ((own['rotOBJ'].position*factor) + own['PreviousViewerPosition'])*(1.0/(factor+1.0))
    
    #own['Viewer'].orientation = 
    
    #own['cameraDistance']=1
    #own['PreviousViewerRotation']=own['Viewer'].orientation
    #own['PreviousViewerPosition']=own['Viewer'].positio

    scene = GameLogic.getCurrentScene()
    obj=scene.objects

    if own['POVLock']==True:
        #helperPos = GameLogic.getCurrentScene().objects['GIRLOBJECT-LP.002'].position
        own['Viewer'].position=own['sexcharacterhead'].position
        own['nonVrCamera'].near = 0.12
        
        
        #hiding everything

        obj['fronthairClothManager'].visible=False
        obj['backhairClothManager'].visible=False
        obj['TeethTop'].visible=False
        obj['LowerTeeth'].visible=False
        obj['EyeBrows-LP'].visible=False

    else:  
        own['nonVrCamera'].near = 0.02

        own['Viewer'].position = own['rotOBJ'].position
        obj['fronthairClothManager'].visible=True
        obj['backhairClothManager'].visible=True
        obj['TeethTop'].visible=True
        obj['LowerTeeth'].visible=True
        obj['EyeBrows-LP'].visible=True

    
    
def TrackHeadBoolPhys(mindist):  
    
    if own['HeadLockCheck'].getDistanceTo(own['HeadLockCheckTarget'])>mindist:
        #own['obHeadTrackerAnim'].restoreDynamics()
        #own['shoulderPhysicsPoint'].restoreDynamics()
        #own['pelvisPhysicsPoint'].restoreDynamics()
        return
    else:
        
        own['panting']=False
def TrackHeadBool(mindist):
    


    if own['HeadLockCheck'].getDistanceTo(own['HeadLockCheckTarget'])>mindist:
        own['obHeadTrackerAnim'].position=own['oldHeadVector']
        own['oldHeadVector'] = own['obHeadTrackerAnim'].position
        vectorHead = (own['obHeadposition'].position - own['obHeadTrackerAnim'].position)*0.1
        own['obHeadTrackerAnim'].position = own['obHeadTrackerAnim'].position + vectorHead#track to player camaera
        
    else:
    
        own['obHeadTrackerAnim'].position=own['obHeadTrackerAnim']['Parent'].position
        own['shoulderPhysicsPoint'].position=own['shoulderPhysicsPoint']['Parent'].position
        own['pelvisPhysicsPoint'].position=own['pelvisPhysicsPoint']['Parent'].position
def moanimations():    
    randfadein = random.randrange(5,12)
    minDistCheck=0.05

    soundMult=0.1
    TrackHeadBool(minDistCheck)

    moanedstore = own['Moaned']        
    if own['obinserter'].getDistanceTo(own['obinsert'])<minDistCheck or own['obinserter'].getDistanceTo(own['obslosh'])<minDistCheck or own['obinserter'].getDistanceTo(own['obrub'])<minDistCheck or own['obinserter'].getDistanceTo(own['obsuck'])<minDistCheck or own['obinserter'].getDistanceTo(own['obinsert2'])<minDistCheck or own['obinserter'].getDistanceTo(own['gagTarget'])<minDistCheck:

        own['inserted']=True
        
    else:
        own['inserted']=False

    
    if 'exhalesound' in own:
        breathLoops(own['exhalesound'],own['inhalesound'])
    
    changed = False  
    if own['insertedcheck'] != own['inserted']:
        own['insertedcheck']=own['inserted']
        changed=True
    
    voicePlayingAlready = False
    if 'voiceAudioHandle' in own:
        voicePlayingAlready =own['voiceAudioHandle'].status
        
        
        
    if changed and own['inserted']:   
        type = ''
        addBreath(.003)
        if(own['obinserter'].getDistanceTo(own['obinsert'])<minDistCheck):#############################################################################################################
            type = 'insert'
            #soundhand = playSound(own['exhalesound'],own['Mouth'],30,50,40,40,False)
            
            playSound(own['plopsound'],own['Vagina'],49,80,calcMags(49),calcMags(50)+1,False).volume=calcMags(6)*soundMult
            playSound(own['pumpsound'],own['Vagina'],49,80,calcMags(25),calcMags(30)+1,False).volume=calcMags(10)*soundMult
            playSound(own['brushsound'],own['Vagina'],80,90,calcMags(40),calcMags(50)+1,False).volume=calcMags(8)*soundMult
            squirt(own['Vagina'],[0,0,0],3)

            if random.randrange(0,12)<2 and voicePlayingAlready==False:
                randomEyeScale()
                if random.randrange(0,100)<95:                
                    blink(random.uniform(.01,.4),random.uniform(.05,.05),random.uniform(.01,.1),random.uniform(0,.04))
                
                quivergasm()
                own['FaceAnimations'].useContinue=False
                own['FaceAnimations'].blendIn = randfadein
                playSound(own['moansound'],own['Mouth'],49,50,70,80,True,own['voiceAudioDevice'])
                
                own['FaceAnimations'].action = 'moan'+str(own['facimation'])

                own['FaceAnimations'].frame = 0
                own['Moaned']=True
            else:
                own['Moaned']=False            
                #playSound(pantsound,own['Mouth'],55,57,70,75,False)
            #playSound(bedsound,own['Vagina'],calcMags(40),calcMags(60),calcMags(60),calcMags(100),False)
            
        if(own['obinserter'].getDistanceTo(own['obrub'])<minDistCheck): ## rubbing pussy##############################################################################################
            type = 'rub' 
            
            playSound(own['rubsound'],own['Vagina'],40,61,calcMags(75),calcMags(100),False).volume=calcMags(55)*soundMult
            playSound(own['brushsound'],own['Vagina'],50,60,calcMags(10),calcMags(10),False).volume=calcMags(8)*soundMult

            
            if random.randrange(0,12)<2 and voicePlayingAlready==False:
                quivergasm()
                randomEyeScale()
                own['FaceAnimations'].useContinue=False
                own['FaceAnimations'].blendIn = randfadein
                playSound(own['moansound'],own['Mouth'],49,50,70,80,True,own['voiceAudioDevice'])
                if random.randrange(0,100)<95:                
                    blink(random.uniform(.01,.4),random.uniform(.05,.05),random.uniform(.01,.1),random.uniform(0.005,.04))
                
                own['FaceAnimations'].action = 'moan'+str(own['facimation'])
                own['FaceAnimations'].frame = 0
                own['Moaned']=True
            else:
                own['Moaned']=False            
                #playSound(pantsound,own['Mouth'],55,57,70,75,False)
            #playSound(bedsound,own['Vagina'],calcMags(40),calcMags(60),calcMags(60),calcMags(100),False)
        
        if own['obinserter'].getDistanceTo(own['gagTarget'])<minDistCheck: ## gag sound ##############################################################################################
            type = 'gag'
           #camShake(0.00002,own['Mouth'])
            
            playSound(own['gagsound'],own['Mouth'],43,48,calcMags(50),calcMags(50),False).volume=calcMags(50)*soundMult
            playSound(own['rubsound'],own['Mouth'],40,41,calcMags(75),calcMags(78),False).volume=calcMags(50)*soundMult
            #if random.randrange(0,10)<2:
            #    playSound(brushsound,own['Vagina'],50,60,calcMags(10),calcMags(10),False)
            #
                #playSound(brushsound,own['Mouth'],49,60,calcMags(1),calcMags(2),False)
            if random.randrange(0,3)<2:
                
                if random.randrange(0,100)<25:    
                    browLerperStart(random.uniform(-0.002,0.001),random.uniform(0.2,1.0),random.uniform(0.2,1.0))
                    blink(random.uniform(.01,.4),random.uniform(.05,.07),random.uniform(.00,.02),random.uniform(0.02,.05))
                squirt(own['LowerTeeth'],[0,-50,0],2)
                randomEyeScale()
                own['FaceAnimations'].useContinue=False
                own['FaceAnimations'].blendIn = randfadein
                #playSound(moansound,own['Mouth'],49,50,70,80,True,own['voiceAudioDevice'])
                own['FaceAnimations'].action = 'moan'+str(own['facimation'])
                own['FaceAnimations'].frame = 0
                own['Moaned']=True
            else:
                own['Moaned']=False  
            
            
        if own['obinserter'].getDistanceTo(own['obinsert2'])<minDistCheck: ##pumping sound##############################################################################################
            #camShake(0.00002,own['Mouth'])
            type = 'insert2'
            if random.randrange(0,20)<2 and voicePlayingAlready==False:
                quivergasm()
                randomEyeScale()
                own['FaceAnimations'].useContinue=False
                own['FaceAnimations'].blendIn = randfadein
                playSound(own['moansound'],own['Mouth'],49,50,70,80,True,own['voiceAudioDevice'])
                if random.randrange(0,100)<95:                
                    blink(random.uniform(.01,.4),random.uniform(.05,.04),random.uniform(.01,.1),random.uniform(0,.05))
                
                own['FaceAnimations'].action = 'moan'+str(own['facimation'])
                own['FaceAnimations'].frame = 0
                own['Moaned']=True
            else:
                own['Moaned']=False   
            playSound(own['brushsound'],own['Vagina'],70,calcMags(75),calcMags(20),calcMags(30)+1,False).volume=calcMags(20)*soundMult
            playSound(own['rubsound'],own['Vagina'],49,calcMags(80),calcMags(50),calcMags(70),False).volume=calcMags(50)*soundMult

            #if random.randrange(0,2)<2:
            #    playSound(bedsound,Vagina,50,60,calcMags(10),calcMags(11),False)
            if random.randrange(0,5)<2:
                playSound(own['pumpsound'],own['Vagina'],49,80,calcMags(20),calcMags(30),False).volume=calcMags(30)*soundMult
            #if random.randrange(0,5)<2:
            #    playSound(plopsound,Vagina,50,80,calcMags(10),calcMags(30),False)                
            

      
 

          
        if own['obinserter'].getDistanceTo(own['obslosh'])<minDistCheck: ## sloppy sound ##############################################################################################
            type = 'slosh'
            blink(random.uniform(.01,.4),random.uniform(.01,.03),random.uniform(.01,.1),random.uniform(0,.05))
            #camShake(0.0002,own['Mouth'])
            playSound(own['pumpsound'],own['Vagina'],49,80,calcMags(2),calcMags(3),False).volume=calcMags(5)*soundMult
            #print('this')
            soundhand = playSound(own['exhalesound'],own['Mouth'],50,50,10,10,True)
            soundhand.volume=.2
            playSound(own['rubsound'],own['Vagina'],49,80,calcMags(50),calcMags(70),False).volume=calcMags(5)*soundMult
            
            if random.randrange(0,12)<2 and voicePlayingAlready==False:
                quivergasm()
                randomEyeScale()
                own['FaceAnimations'].useContinue=False
                own['FaceAnimations'].blendIn = randfadein
                playSound(own['moansound'],own['Mouth'],49,50,70,80,True,own['voiceAudioDevice'])
                if random.randrange(0,100)<95:                
                    blink(random.uniform(.01,.4),random.uniform(.05,.05),random.uniform(.01,.1),random.uniform(0,.05))
                
                own['FaceAnimations'].action = 'moan'+str(own['facimation'])
                own['FaceAnimations'].frame = 0
                own['Moaned']=True
            else:
                own['Moaned']=False            
            #if random.randrange(0,50)<2:
            #    playSound(bedsound,own['Vagina'],50,60,5,6,False)
 
        #addDebugInfo('insert type: '+type)        
        #print(own['voiceAudioHandle'].status)
        if moanedstore != own['Moaned'] and own['Moaned']==False:
            own['FaceAnimations'].blendIn = random.randrange(50,200)
            own['FaceAnimations'].useContinue=True
            
            own['FaceAnimations'].action = 'FaceexpSexFace'
            own['FaceAnimations'].frame = random.randrange(1,20000)
def squirt(originObject,initVector=[0,-100,-248],amount=-1):
    scene = GameLogic.getCurrentScene()
    currentCumOB=scene.addObject('Cumtrail',originObject,50)
    localVector = originObject.worldPosition + originObject.worldOrientation*Vector(initVector)
    firstCumForce=localVector*random.uniform(.5,1)
    currentCumOB.applyForce(firstCumForce)
    currentCumOB['initialVelocity']=firstCumForce
    currentCumOB['trackToOB']=originObject
    currentCumOB['rootOB']=originObject
    currentCumOB['collided']=False
    currentCumOB['trailCount']=random.randrange(amount,4)#max of 5. Use negatives otherwise
def addSquirtLoop():#for trail
    
    maxAdd=5
    
    cumCont = bge.logic.getCurrentController()
    cumOwn = cumCont.owner
    if(cumOwn['collided']==False):
        if(cumCont.sensors['Collision'].positive):
            
            scene = GameLogic.getCurrentScene()
            wetSpot=scene.addObject('wetSpot',cumOwn,5000)
            wetSpot['wetCount']=30
            spotScale=cumOwn['trailCount']*.3
            wetSpot.localScale=Vector([spotScale,spotScale,1])
            
            for wetOBJ in scene.objects:
                if 'wetCount' in wetOBJ:
                    wetOBJ['wetCount']=wetOBJ['wetCount']-1
                    wetOBJ.localScale=wetOBJ.localScale*.95
                    if wetOBJ['wetCount']<0:
                        wetOBJ.endObject()
            
            eulOri=Euler([0,0,0])
            wetSpot.orientation=eulOri
            dripsound = own['soundpath'] + 'drips\\'+str(random.randrange(1,own['maxfilesdrips']))+'.mp3'
            playSound(dripsound,cumOwn,49,50,int(float(-59)),int(float(0)),True,own['voiceAudioDevice'])
            cumOwn['collided']=True
            cumOwn.visible=False
        
    cumOwn.applyForce([0,0,-10])
    
    cumDirection = cumOwn.getVectTo(cumOwn['trackToOB'])        
    cumOwn.alignAxisToVect(cumDirection[1],1,1)
    cumLength=cumOwn.getDistanceTo(cumOwn['trackToOB'])*33
    cumOwn.localScale=Vector([1,cumLength,1])
    
    
    
    #trackToAct = cumCont.actuators['trackTo']

    
    
    


    if(cumOwn['init']==False):
        force=20.0
        randomX=random.randrange(force*-1,force)
        randomY=random.randrange(force*-1,force)
        randomZ=random.randrange(force*-1,force)
        
        cumOwn.applyForce([randomX,randomY,randomZ])
    if(cumOwn['trailCount']<maxAdd):
        #cumOwn.applyForce(cumDirection[1]*.01)
        if(cumOwn['addCounter']==1):
            
            scene = GameLogic.getCurrentScene()
            currentCumTrail=scene.addObject('Cumtrail',cumOwn,50)
            currentCumTrail['trackToOB']=cumOwn['trackToOB']
            cumOwn['trackToOB']=currentCumTrail
            currentCumTrail['rootOB']=cumOwn['rootOB']
            currentCumTrail.position=currentCumTrail['rootOB'].position
            currentCumTrail['trailCount']=cumOwn['trailCount']+1
            currentCumTrail['collided']=False
            currentCumTrail['initialVelocity']=cumOwn['initialVelocity']*.8
            currentCumTrail.applyForce(currentCumTrail['initialVelocity'])

    if(cumOwn['trailCount']<maxAdd):
        cumDirection = cumOwn.getVectTo(cumOwn['trackToOB'])

    else:
        cumOwn.localScale=Vector([1,.1,1])
    cumOwn['addCounter']+=1
    cumOwn['init']=True
def addDebugInfo(toLog):

    #currentText=own['debugTextObject']['Text'].split('\n')
    maxRecords=8
    
    own['debugTextObject']['Text']= (str)(toLog)+'\n'+own['debugTextObject']['Text']
    
    recorded=own['debugTextObject']['Text'].split('\n')
    
    if len(recorded)>maxRecords:
        own['debugTextObject']['Text']=''
        for x in range (0,maxRecords):
            own['debugTextObject']['Text']=own['debugTextObject']['Text']+recorded[x]+'\n'
    if own['screeninterface']['UIenabled']==True: 
        import overlayUiGame

        overlayUiGame.renderTextureRefresh('Texture','screenInterface')
    
            
def addSquirtTest():
    squirt(own['Vagina'],[0,-100,-248],-7)
def visibilityToggle():
    addDebugInfo('hiding')
    visibilityCont = bge.logic.getCurrentController()
    visOwn = visibilityCont.owner

    if(visibilityCont.sensors[0].positive):

        if('visible' not in visOwn):
            visOwn['visible']=False
            visOwn.visible=False
            return
        if(visOwn['visible']==True):
            visOwn.visible=False
            visOwn['visible']=False
            return
        if(visOwn['visible']==False):
            visOwn.visible=True
            visOwn['visible']=True   
            return
def penisTargetingComputer():
    
    lockDistance = 0.2#distance to start locking penis to closest target
    if(own['cockBase'].getDistanceTo(own['TeethTop'])<lockDistance):
        own['cockTarget'].worldPosition=own['TeethTop'].worldPosition
    if(own['cockBase'].getDistanceTo(own['Vagina'])<lockDistance):
        own['cockTarget'].worldPosition=own['Vagina'].worldPosition    
def runLowPriority():
    cont = bge.logic.getCurrentController()
    own = cont.owner
    
    if random.randrange(0,50)<2:
        own['panting']=True
    if random.randrange(0,50)<2:
        own['panting']=False
    if own['AnimRandonSpeed']<own['AnimRandonSpeedTarget']:
        own['AnimRandonSpeed']=own['AnimRandonSpeed']+0.1
    if own['AnimRandonSpeed']>own['AnimRandonSpeedTarget']:
        own['AnimRandonSpeed']=own['AnimRandonSpeed']-0.1
    
    if random.randrange(0,150)<2:
        blink(random.uniform(.01,.4),random.uniform(.03,.05),random.uniform(0.01,0.5),random.uniform(0.00,0.02))

    if random.randrange(0,80)<2:
        randomEyeScale()

    own['pumpsound'] = own['soundpath'] + 'pumps\\'+str(random.randrange(1,own['maxfilespump']))+'.mp3'
    #own['moansound'] = own['soundpath'] + 'female moans\\cleaned\\'+str(own['facimation'])+'.mp3'
    own['randomMoanNum']=random.randrange(1,own['maxfilesmoan'])
    
    own['moansound'] = own['soundpath'] + 'female moans\\cleaned\\'+str(own['randomMoanNum'])+'.mp3'
    own['facimation'] = own['randomMoanNum']
    own['voicetexturesound'] = own['soundpath'] + 'voiceTextures\\'+str(random.randrange(1,own['maxfilesvoicetexture']))+'.mp3'

    own['bedsound'] = own['soundpath'] + 'bed\\'+str(random.randrange(1,own['maxfilesbed']))+'.mp3'
    own['brushsound'] = own['soundpath'] + 'brush\\'+str(random.randrange(1,own['maxfilesbrush']))+'.mp3'
    own['plopsound'] = own['soundpath'] + '\\ploppyslap\\'+str(random.randrange(1,own['maxfilesplop']))+'.mp3'
    own['pantsound'] = own['soundpath'] + 'pants\\cleaned\\'+str(random.randrange(1,own['maxfilespant']))+'.mp3'
    own['rubsound'] = own['soundpath'] + 'rubs\\'+str(random.randrange(1,own['maxfilesrub']))+'.mp3'
    own['gagsound'] = own['soundpath'] + 'gags\\'+str(random.randrange(1,own['maxfilesgag']))+'.mp3'
    own['inhalesound'] = own['soundpath'] + 'breaths\\inhale\\'+str(random.randrange(1,own['maxfilesinhale']))+'.mp3'
    own['exhalesound'] = own['soundpath'] + 'breaths\\exhale\\'+str(random.randrange(1,own['maxfilesexhale']))+'.mp3'
    
    
    
    if(random.randrange(0,20)<1):
        browLerperStart(random.uniform(0.00,0.002),random.uniform(0.1,0.30),random.uniform(0.2,0.30))
        
    if(random.randrange(0,20)<1):
        browLerperStart(random.uniform(-0.0001,0.0001),random.uniform(0.1,.3),random.uniform(0.1,.3))
    randomanimrange = 10
    
    if(random.randrange(0,6)<1):
        own['AnimRandonSpeedTarget']=(float)((random.randrange(randomanimrange*-1,randomanimrange))*0.01)

    if(random.randrange(0,60)<1):
        own['randomStop']=random.uniform(0.7,1.0)
        
    if(random.randrange(0,30)<1):
        own['randomStop']=1.0
    
    own['FinalAnimSpeed']=(own['AnimSpeed']+own['AnimRandonSpeed'])*own['randomStop']
    
    if own['Counter']<6:#tied to chainphys script

        own['Counter']+=1
        #own['AnimSpeed']=1.0
    if own['ChangeTracker']!=own['ChangeTrackerChild']:
        own['Counter']=0
        own['ChangeTrackerChild']=own['ChangeTracker']
        
        
        own['FaceAnimations'].blendIn = random.randrange(50,200)
        own['FaceAnimations'].useContinue=True
        
        own['FaceAnimations'].action = 'FaceexpSexFace'
        own['FaceAnimations'].frame = random.randrange(1,20000)
        own['FaceAnimations'].frame = random.randrange(1,20000)
def keyBoardManager():
    for key,status in own['Keys'].events:
            # key[0] == bge.events.keycode, key[1] = status
        if status == 3:

            if key == bge.events.XKEY:
                own['CurrentAction']+=1
            if key == bge.events.ZKEY:
                own['CurrentAction']-=1
            if key == bge.events.BKEY:
                own['AnimSpeed']-=0.1   
            if key == bge.events.NKEY:
                own['AnimSpeed']+=0.1   
            if key == bge.events.ENTERKEY:
                
                squirt(GameLogic.getCurrentScene().objects['CumFactory'])     

def eyeCausticLoops():    
    for eye in own['causticMans']:
        lamp = eye.children[0]
        #print(lamp.localPosition)
        lamp.localPosition=Vector([.0050,0.0,0])
        #print(dir(lamp))
        lamp.energy=10.0

        #print(lamp.energy)
        #print(lamp.distance)
        
        

def run():
    cont = bge.logic.getCurrentController()
    own = cont.owner
    LerpCamera()
    own['AnimFrame']=own['AnimFrame']+own['FinalAnimSpeed']
    
    moanimations()
    voiceProcedurals()
    LerpCamera()
    voiceProcedurals()
    browLerper()
    #CamShakeLoop()
    penisTargetingComputer()
    quivergasmLoop()
    FocusSystem()
    HoldPlayer()
    adjustEyeScale()
    lidLoops()
    #eyeCausticLoops()
    #print(GameLogic.getLogicTicRate())
    action = own['CurrentAction']

    if own['ChangeTracker']==own['CurrentAction'] and own['animationSet']==False:
        try:
            own['act'].action = 'SEX'+(str)(action)
            scene = GameLogic.getCurrentScene()
            scene.objects['ActionTracker']['Text']='Action-'+(str)(action)
            addDebugInfo('test')
        except:
            own['act'].action = 'missinganim' 
        
        for OBJ in own['CharacterOBJs']:
            OBJ.visible=True
        own['animationSet']=True
    own['track']=action  
    TrackHeadBoolPhys(0.05)
    if own['ChangeTracker']!=own['CurrentAction']:
        own['animationSet']=False
        own['act'].action = 'SEX0'#reset sex bones  
        own['changetrackeranimationbuffertime']=own['changetrackeranimationbuffertime']+1
        for OBJ in own['CharacterOBJs']:
            OBJ.visible=False
        if own['changetrackeranimationbuffertime']>10:
            own['ChangeTracker']=own['CurrentAction']
            own['changetrackeranimationbuffertime']=0