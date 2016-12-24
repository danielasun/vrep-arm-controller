# Copyright 2006-2016 Coppelia Robotics GmbH. All rights reserved. 
# marc@coppeliarobotics.com
# www.coppeliarobotics.com
# 
# -------------------------------------------------------------------
# THIS FILE IS DISTRIBUTED "AS IS", WITHOUT ANY EXPRESS OR IMPLIED
# WARRANTY. THE USER WILL USE IT AT HIS/HER OWN RISK. THE ORIGINAL
# AUTHORS AND COPPELIA ROBOTICS GMBH WILL NOT BE LIABLE FOR DATA LOSS,
# DAMAGES, LOSS OF PROFITS OR ANY OTHER KIND OF LOSS WHILE USING OR
# MISUSING THIS SOFTWARE.
# 
# You are free to use/modify/distribute this file for whatever purpose!
# -------------------------------------------------------------------
#
# This file was automatically created for V-REP release V3.3.2 on August 29th 2016

# Make sure to have the server side running in V-REP: 
# in a child script of a V-REP scene, add following command
# to be executed just once, at simulation start:
#
# simExtRemoteApiStart(19999)
#
# then start simulation, and run this program.
#
# IMPORTANT: for each successful call to simxStart, there
# should be a corresponding call to simxFinish at the end!

try:
    import vrep
except:
    print ('--------------------------------------------------------------')
    print ('"vrep.py" could not be imported. This means very probably that')
    print ('either "vrep.py" or the remoteApi library could not be found.')
    print ('Make sure both are in the same folder as this file,')
    print ('or appropriately adjust the file "vrep.py"')
    print ('--------------------------------------------------------------')
    print ('')

import time
import pygame

# Define some colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

# joystick parameters
js_scale_factor = .1
js_dead_zone = .15


pygame.init()

# Loop until the user clicks the close button.
done = False

# Initialize the joysticks
pygame.joystick.init()


print ('Program started')
vrep.simxFinish(-1) # just in case, close all opened connections
clientID=vrep.simxStart('127.0.0.1',80000,True,True,5000,5) # Connect to V-REP
if clientID!=-1:
    print ('Connected to remote API server')

    # Now try to retrieve data in a blocking fashion (i.e. a service call):
    res,objs=vrep.simxGetObjects(clientID,vrep.sim_handle_all,vrep.simx_opmode_blocking)
    if res==vrep.simx_return_ok:
        print ('Number of objects in the scene: ',len(objs))
    else:
        print ('Remote API function call returned with error code: ',res)

    time.sleep(2)
    vrep.simxGetPingTime(clientID)
    # Now retrieve streaming data (i.e. in a non-blocking fashion):
    startTime=time.time()
    vrep.simxGetIntegerParameter(clientID,vrep.sim_intparam_mouse_x,vrep.simx_opmode_streaming) # Initialize streaming

    returnCode, target_handle = vrep.simxGetObjectHandle(clientID, "redundantRob_target", vrep.simx_opmode_blocking)
    print("returnCode = " + str(returnCode))
    print("target handle is : " + str(target_handle))

    print(vrep.simx_return_ok)

    returnCode, target_pos = vrep.simxGetObjectPosition(clientID, target_handle, -1, vrep.simx_opmode_streaming + 50)

    js_axis_vals = [0,0,0,0,0,0]

    while done==False:
        # EVENT PROCESSING STEP
        for event in pygame.event.get():  # User did something
            if event.type == pygame.QUIT:  # If user clicked close
                done = True  # Flag that we are done so we exit this loop

            # Possible joystick actions: JOYAXISMOTION JOYBALLMOTION JOYBUTTONDOWN JOYBUTTONUP JOYHATMOTION
            if event.type == pygame.JOYBUTTONDOWN:
                print("Joystick button pressed.")
            if event.type == pygame.JOYBUTTONUP:
                print("Joystick button released.")

        # Get count of joysticks
        joystick_count = pygame.joystick.get_count()

        # For each joystick:
        for i in range(joystick_count):
            joystick = pygame.joystick.Joystick(i)
            joystick.init()

            # Get the name from the OS for the controller/joystick
            name = joystick.get_name()

            # Usually axis run in pairs, up/down for one, and left/right for
            # the other.
            axes = joystick.get_numaxes()

            axisVal = joystick.get_axis(i)
            print("This is the value for axis 0: " + str(axisVal))

            for i in range(axes):
                axis = joystick.get_axis(i)
                if abs(axis) < js_dead_zone:
                    # print("DEAD_ZONE")
                    axis = 0
                js_axis_vals[i] = axis



            buttons = joystick.get_numbuttons()

            for i in range(buttons):
                button = joystick.get_button(i)

            # Hat switch. All or nothing for direction, not like joysticks.
            # Value comes back in an array.
            hats = joystick.get_numhats()

            for i in range(hats):
                hat = joystick.get_hat(i)


        # Sending command to VREP
        returnCode, target_pos = vrep.simxGetObjectPosition(clientID, target_handle, -1, vrep.simx_opmode_buffer) # Try to retrieve the streamed data
        if returnCode==vrep.simx_return_ok: # After initialization of streaming, it will take a few ms before the first value arrives, so check the return code
            # print(target_pos)
            target_pos[0] = target_pos[0] + js_scale_factor*js_axis_vals[0]
            target_pos[1] = target_pos[1] - js_scale_factor*js_axis_vals[1]
            target_pos[2] = target_pos[2] + js_scale_factor/2*(js_axis_vals[2] - js_axis_vals[5])
            vrep.simxSetObjectPosition(clientID,target_handle,-1,target_pos,vrep.simx_opmode_oneshot)
        time.sleep(0.005)

    # Now send some data to V-REP in a non-blocking fashion:
    vrep.simxAddStatusbarMessage(clientID,'Hello V-REP! Whats up dude',vrep.simx_opmode_oneshot)

    # Before closing the connection to V-REP, make sure that the last command sent out had time to arrive. You can guarantee this with (for example):
    vrep.simxGetPingTime(clientID)

    # Now close the connection to V-REP:
    vrep.simxFinish(clientID)
else:
    print ('Failed connecting to remote API server')
print ('Program ended')
