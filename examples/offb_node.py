#! /usr/bin/env python

import rospy
from geometry_msgs.msg import PoseStamped
from mavros_msgs.msg import State
from mavros_msgs.srv import CommandBool, CommandBoolRequest, SetMode, SetModeRequest

current_state = State()
current_pose = PoseStamped()
start_pose = None 

def state_cb(msg):
    global current_state
    current_state = msg

def local_pos(pose):
    global current_pose
    current_pose = pose
    global start_pose
    if start_pose is None:
        start_pose = current_pose
        #start_pose.pose.position.z = start_alt

if __name__ == "__main__":
    rospy.init_node("offb_node_py")

    state_sub = rospy.Subscriber("mavros/state", State, callback = state_cb)
    local_pos_sub = rospy.Subscriber('/mavros/local_position/pose',
                                     PoseStamped, local_pos, queue_size=10)
    local_pos_pub = rospy.Publisher("mavros/setpoint_position/local", PoseStamped, queue_size=10)

    rospy.wait_for_service("/mavros/cmd/arming")
    arming_client = rospy.ServiceProxy("mavros/cmd/arming", CommandBool)

    rospy.wait_for_service("/mavros/set_mode")
    set_mode_client = rospy.ServiceProxy("mavros/set_mode", SetMode)


    # Setpoint publishing MUST be faster than 2Hz
    rate = rospy.Rate(20)

    # Wait for Flight Controller connection
    while(not rospy.is_shutdown() and not current_state.connected):
        rate.sleep()

    pose = PoseStamped()

    pose.pose.position.x = current_pose.pose.position.x
    pose.pose.position.y = current_pose.pose.position.y
    pose.pose.position.z = current_pose.pose.position.z+2

    # Send a few setpoints before starting
    for i in range(100):
        if(rospy.is_shutdown()):
            break

        local_pos_pub.publish(pose)
        rate.sleep()

    offb_set_mode = SetModeRequest()
    offb_set_mode.custom_mode = 'OFFBOARD'

    arm_cmd = CommandBoolRequest()
    arm_cmd.value = True

    last_req = rospy.Time.now()

    while((not rospy.is_shutdown()) and abs(current_pose.pose.position.z - pose.pose.position.z) > 0.1):
        if(current_state.mode != "OFFBOARD" and (rospy.Time.now() - last_req) > rospy.Duration(5.0)):
            if(set_mode_client.call(offb_set_mode).mode_sent == True):
                rospy.loginfo("OFFBOARD enabled")

            last_req = rospy.Time.now()
        else:
            if(not current_state.armed and (rospy.Time.now() - last_req) > rospy.Duration(5.0)):
                if(arming_client.call(arm_cmd).success == True):
                    rospy.loginfo("Vehicle armed")

                last_req = rospy.Time.now()
	
        local_pos_pub.publish(pose)
    
    rospy.sleep(5.0)    
    last_req = rospy.Time.now()   
    pos_set_mode = SetModeRequest()
    pos_set_mode.custom_mode = 'POSCTL'
    while(not rospy.is_shutdown()):
        if(current_state.mode != "POSCTL" and (rospy.Time.now() - last_req) > rospy.Duration(5.0)):
            if(set_mode_client.call(pos_set_mode).mode_sent == True):
                rospy.loginfo("POSCTL enabled")
                rospy.signal_shutdown("POSCTL mode enabled")
                
                

            last_req = rospy.Time.now()
        

        rate.sleep()


