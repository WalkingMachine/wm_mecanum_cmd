#!/usr/bin/env python

# Mecanum wheels command
# input: geometry_msgs/Twist
# output: roboteq_msgs/Command

# FLW = Front Left Wheel
# FRW = Front Right Wheel
# RLW = Rear Left Wheel
# RRW = Rear Right Wheel

import rospy
from roboteq_msgs.msg import Feedback
from geometry_msgs.msg import Twist
from math import pi, sin, cos, sqrt, atan2


class MecanumCmd:

    def __init__(self):

        self.sub = rospy.Subscriber('cmd_vel', Twist, self.callback)

        self.pubFLW = rospy.Publisher('roboteq_driver_FLW/feedback', Feedback, queue_size=1)
        self.pubFRW = rospy.Publisher('roboteq_driver_FRW/feedback', Feedback, queue_size=1)
        self.pubRLW = rospy.Publisher('roboteq_driver_RLW/feedback', Feedback, queue_size=1)
        self.pubRRW = rospy.Publisher('roboteq_driver_RRW/feedback', Feedback, queue_size=1)

        self.radius = 0.15 / 2      # wheel radius, in meter

        # x axis distance between wheel axis and the robot's centroid
        self.alpha = 0.31      # in meter

        # y axis distance between wheel radial median and the robot'S centroid
        self.beta = 0.3       # in meter

        self.maxLinearVelocity = 1   # m/s
        self.maxAngularVelocity = pi/6  # rad/s

    def callback(self, twist):

        FLW_cmd = Feedback()
        FRW_cmd = Feedback()
        RLW_cmd = Feedback()
        RRW_cmd = Feedback()

        # linear velocity
        vLinear = sqrt(twist.linear.x**2 + twist.linear.y**2)

        if vLinear > self.maxLinearVelocity:
            vLinear = self.maxLinearVelocity

        # movement orientation
        Heading = atan2(twist.linear.y, twist.linear.x)

        # x axis linear velocity
        xVel = vLinear * cos(Heading)
        # y axis linear velocity
        yVel = vLinear * sin(Heading)

        # YAW axis rotational velocity
        yawVel = twist.angular.z

        if yawVel**2 > self.maxAngularVelocity**2:
            yawVel = self.maxAngularVelocity * yawVel / abs(yawVel)

        w = self.InverseKinematics(xVel, yVel, yawVel)

        FLW_cmd.measured_velocity = w[0]
        FRW_cmd.measured_velocity = w[1]
        RLW_cmd.measured_velocity = w[2]
        RRW_cmd.measured_velocity = w[3]

        self.pubFLW.publish(FLW_cmd)
        self.pubFRW.publish(FRW_cmd)
        self.pubRLW.publish(RLW_cmd)
        self.pubRRW.publish(RRW_cmd)

    def InverseKinematics(self,xVel, yVel, yawVel):

        # Reference:
        # Maulana, E.; Muslim, M.A.; Hendrayawan, V.,
        # "Inverse kinematic implementation of four-wheels mecanum drive mobile robot using stepper motors,"
        #  in Intelligent Technology and Its Applications (ISITIA), 2015 International Seminar on ,
        # vol., no., pp.51-56, 20-21 May 2015

        # Inverse Kinematics matrix
        J = [[1, -1, -1*(self.alpha + self.beta)],
             [1, 1, (self.alpha + self.beta)],
             [1, 1, -1*(self.alpha + self.beta)],
             [1, -1, (self.alpha + self.beta)]]

        # wheel angular velocity, in rad/s
        w = [0., 0., 0., 0.]

        for k in range(len(w)):
            w[k] = ((-1)**k) * (1/self.radius) * (J[k][0]*xVel + J[k][1]*yVel + J[k][2]*yawVel)

        return w


if __name__ == '__main__':

    try:
        rospy.init_node('wm_mecanum_cmd_node')

        MecanumCmd()

        rospy.spin()

    except rospy.ROSInterruptException:
        pass
