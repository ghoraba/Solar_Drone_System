import rospy
from geographic_msgs.msg import GeoPointStamped

def set_home_position(latitude, longitude, altitude):
    print("before node started")
    rospy.init_node('set_home_position', anonymous=True)
    pub = rospy.Publisher('/mavros/global_position/global', GeoPointStamped, queue_size=10)
    print("after node started")
    
    geo_point_stamped = GeoPointStamped()
    geo_point_stamped.header.stamp = rospy.Time.now()
    geo_point_stamped.position.latitude = latitude
    geo_point_stamped.position.longitude = longitude
    geo_point_stamped.position.altitude = altitude
    print("created message")

    rate = rospy.Rate(10)  # 10hz
    while not rospy.is_shutdown():
        print(f"geo_point_stamped: {geo_point_stamped}")
        pub.publish(geo_point_stamped)
        rate.sleep()

if __name__ == '__main__':
    try:
        set_home_position(51.5074, -0.1278, 0)  # Example for London, UK
    except rospy.ROSInterruptException:
        pass
