#!/usr/bin/python3

# import avango-guacamole libraries
import avango
import avango.daemon
import avango.gua
from avango.script import field_has_changed

# import python libraries
import math
import time
from numpy.linalg import inv
# constant size of the window on the monitor in meters
# YOUR CODE - BEGIN (Exercise 2.0 - Screen Size)
SCREEN_SIZE = avango.gua.Vec2(0.64, 0.40)
# YOUR CODE - END (Exercise 2.0 - Screen Size)

# appends a camera node, screen node, and navigation capabilities to the scenegraph
class DesktopViewingSetup(avango.script.Script):

    # input fields
    sf_visibility_toggle = avango.SFBool()
    sf_visibility_toggle.value = False

    sf_left_arrow_key = avango.SFBool()
    sf_left_arrow_key.value = False

    sf_right_arrow_key = avango.SFBool()
    sf_right_arrow_key.value = False

    # YOUR CODE - BEGIN (Exercise 2.7 - Fields for Up and Down Arrow Keys)
    sf_up_arrow_key = avango.SFBool()
    sf_up_arrow_key.value = False

    sf_down_arrow_key = avango.SFBool()
    sf_down_arrow_key.value = False
    # YOUR CODE - END (Exercise 2.7 - Fields for Up and Down Arrow Keys)

    def __init__(self):
        self.super(DesktopViewingSetup).__init__()

    # creates and appends the viewing setup to the scenegraph
    def create(self, scenegraph):
        self.scenegraph = scenegraph
        self.time_before_frame=0
        self.current_time=time.time()
        # static transform node
        self.static_transform = avango.gua.nodes.TransformNode(Name='static_transform')
        self.static_transform.Transform.value = avango.gua.make_trans_mat(-25.0, 1.5, 0.0) * \
                                                avango.gua.make_rot_mat(-60, 0, 1, 0) * \
                                                avango.gua.make_trans_mat(8.0, 0.0, -5.0)
        self.scenegraph.Root.value.Children.value.append(self.static_transform)

        # additional transformation nodes
        # YOUR CODE - BEGIN (Exercises 2.3, 2.5, 2.6, 2.7 - Node Structures)
        self.bird_transform=self.scenegraph['/bird_rot_animation/bird_transform']
        self.setup_back = avango.gua.nodes.TransformNode(Name='Setup_Translate')
        self.setup_back.Transform.value = avango.gua.make_trans_mat(0.0, 0.0, 5.0)
        self.setup_back_rot = avango.gua.nodes.TransformNode(Name='Rightleft_Rot_back')
        self.setup_back_rot.Transform.value = avango.gua.make_rot_mat(0.0,0.0,0.0,0.0)
        self.upDown_back_rot = avango.gua.nodes.TransformNode(Name='UPDOWN_Rot_back')
        self.upDown_back_rot.Transform.value = avango.gua.make_rot_mat(0.0,0.0,0.0,0.0)
        # YOUR CODE - END (Exercises 2.3, 2.5, 2.6, 2.7 - Node Structures)
        # screen node
        self.screen_dimensions = SCREEN_SIZE
        self.screen_node = avango.gua.nodes.ScreenNode(Name='screen_node')
        self.screen_node.Width.value = self.screen_dimensions.x
        self.screen_node.Height.value = self.screen_dimensions.y
        self.screen_node.Transform.value = avango.gua.make_trans_mat(
            0.0, 0.0, -0.6)

        # YOUR CODE - BEGIN (Exercises 2.3, 2.5, 2.6, 2.7 - Attach Screen Node)
        
        matCamera = avango.gua.Mat4()
        matCamera.set_element(2,3,5)
        #matCamera.set_element(2,2,-5)
        #self.screen_node.Transform.value = matCamera
        #print('_____________________', self.screen_node.Transform.value)
        self.bird_transform.Children.value.append(self.upDown_back_rot)
        self.upDown_back_rot.Children.value.append(self.setup_back)
        self.setup_back.Children.value.append(self.setup_back_rot)
        self.setup_back_rot.Children.value.append(self.screen_node)
        
        #self.screen_node.Transform.value = matCamera
        # YOUR CODE - END (Exercises 2.3, 2.5, 2.6, 2.7 - Attach Screen Node)

        # camera node (head)
        self.camera_node = avango.gua.nodes.CameraNode(Name='camera_node')
        self.camera_node.SceneGraph.value = self.scenegraph.Name.value
        self.camera_node.LeftScreenPath.value = self.screen_node.Path.value
        # YOUR CODE - BEGIN (Exercise 2.4 - Set Blacklist on Camera)
        self.sf_visibility_toggle_changed()
        self.changed=True
        #print('Tag List',bird_geometry_node.Tags.value)
        
        # YOUR CODE - END (Exercise 2.4 - Set Blacklist on Camera)

        # YOUR CODE - BEGIN (Exercises 2.3, 2.5, 2.6, 2.7 - Attach Camera Node)
        
        matCamera = avango.gua.Mat4()
        matCamera.set_element(2,3,5)
        #matCamera.set_element(2,2,5)
        #self.camera_node.Transform.value = matCamera
        self.setup_back_rot.Children.value.append(self.camera_node)
        
        #self.camera_node.Transform.value = matCamera
        # YOUR CODE - END (Exercises 2.3, 2.5, 2.6, 2.7 - Attach Camera Node)

        # create keyboard sensor and connect fields
        self.device_service = avango.daemon.DeviceService()
        self.keyboard_sensor = avango.daemon.nodes.DeviceSensor(
            DeviceService=self.device_service)
        self.keyboard_sensor.Station.value = 'gua-device-keyboard'
        self.sf_left_arrow_key.connect_from(self.keyboard_sensor.Button5)
        self.sf_right_arrow_key.connect_from(self.keyboard_sensor.Button6)
        self.sf_visibility_toggle.connect_from(self.keyboard_sensor.Button7)
        # YOUR CODE - BEGIN (Exercise 2.7 - Connect Up and Down Arrow Keys)
        self.sf_up_arrow_key.connect_from(self.keyboard_sensor.Button8)
        self.sf_down_arrow_key.connect_from(self.keyboard_sensor.Button9)
        # YOUR CODE - END (Exercise 2.7 - Connect Up and Down Arrow Keys)

        # compute and set field-of-view (used to check Exercises 2.1 and 2.2)
        print("The camera's field of view is initially: " +
              str(round(self.compute_fov_in_deg(), 3)) + " deg")
        self.set_fov_in_deg(45)
        print("After set_fov_in_deg, the camera's field of view is: " +
             str(round(self.compute_fov_in_deg(), 3)) + " deg")

        # compute model-view transform of bird (used to check Exercise 2.9)
        bird_geometry_node = self.scenegraph['/bird_rot_animation/bird_transform/bird_model']
        print()
        print("The initial model-view transformation of the bird model is:")
        print(self.compute_model_view_transform(bird_geometry_node))
        print()

        self.always_evaluate(True)

    # called every frame because of self.always_evaluate(True)
    def evaluate(self):
        rotation_speed = 60.0  # deg/s
        
        # YOUR CODE - BEGIN (Exercise 2.8 - Frame-Rate Independent Mapping of Camera Controls)
        #print(self.current_time-self.time_before_frame)
        self.rotp=0.1 if self.current_time-self.time_before_frame < 0.006 else 1.25
        self.rotn=-0.1 if self.current_time-self.time_before_frame < 0.006 else -1.25
        # YOUR CODE - BEGIN (Exercise 2.6 - Map Left and Right Arrow Keys)
        if(self.sf_left_arrow_key.value):
            self.setup_back_rot.Transform.value = avango.gua.make_rot_mat(self.rotp, 0, 1, 0) * avango.gua.make_rot_mat(0.1, 0, 1, 0) *  self.setup_back_rot.Transform.value
        if(self.sf_right_arrow_key.value):
            self.setup_back_rot.Transform.value = avango.gua.make_rot_mat(self.rotn, 0, 1, 0) * avango.gua.make_rot_mat(-0.1, 0, 1, 0) *  self.setup_back_rot.Transform.value
        #self.setup_back_rot.Transform.value = avango.gua.make_rot_mat(0.1, 0, 1, 0) *  self.setup_back_rot.Transform.value

        # YOUR CODE - END (Exercise 2.6 - Map Left and Right Arrow Keys)

        # YOUR CODE - BEGIN (Exercise 2.7 - Map Up and Down Arrow Keys)
        if(self.sf_up_arrow_key.value):
            self.upDown_back_rot.Transform.value = avango.gua.make_rot_mat(self.rotp, 1, 0, 0) * avango.gua.make_rot_mat(0.1, 1, 0, 0) *  self.upDown_back_rot.Transform.value
        if(self.sf_down_arrow_key.value):
            self.upDown_back_rot.Transform.value = avango.gua.make_rot_mat(self.rotn, 1, 0, 0) * avango.gua.make_rot_mat(-0.1, 1, 0, 0) *  self.upDown_back_rot.Transform.value
        # YOUR CODE - END (Exercise 2.7 - Map Up and Down Arrow Keys)
        self.time_before_frame=self.current_time
        self.current_time=time.time()
        # YOUR CODE - END (Exercise 2.8 - Frame-Rate Independent Mapping of Camera Controls)

    # called whenever sf_visibility_toggle_changes
    @field_has_changed(sf_visibility_toggle)
    def sf_visibility_toggle_changed(self):

        if self.sf_visibility_toggle.value:
            node_to_toggle = self.scenegraph['/bird_rot_animation/bird_transform/bird_model']
            # YOUR CODE - BEGIN (Exercise 2.4 - Toggle Tag to Match or Unmatch Blacklist)
            node_to_toggle.Tags.value= ['alt_toggle']
            if(self.changed):
                self.camera_node.BlackList.value = node_to_toggle.Tags.value
                self.changed=False
            else:
                self.camera_node.BlackList.value = []
                self.changed=True
            # YOUR CODE - END (Exercise 2.4 - Toggle Tag to Match or Unmatch Blacklist)

    # computes the field-of-view of the viewing setup and returns the result in degrees
    def compute_fov_in_deg(self):
        # YOUR CODE - BEGIN (Exercise 2.1 - Compute FOV from Camera-Screen Relation)
        return 2*math.degrees(math.atan((SCREEN_SIZE.x/2)/(self.screen_node.Width.value)))
        # YOUR CODE - BEGIN (Exercise 2.1 - Compute FOV from Camera-Screen Relation)

    # sets the field-of-view of the viewing setup to the specified amount of degrees
    def set_fov_in_deg(self, degrees):
        # YOUR CODE - BEGIN (Exercise 2.2 - Set desired FOV)
        self.screen_node.Width.value=(SCREEN_SIZE.x/2)/(math.tan(math.radians(degrees/2)))
        
        # YOUR CODE - END (Exercise 2.2 - Set desired FOV)

    # computes the model-view transformation of a given node
    def compute_model_view_transform(self, node):
        # YOUR CODE - BEGIN (Exercise 2.9 - Model-View Transformation)
        currentNode = node


        worldMatrix = currentNode.Transform.value
        while currentNode.Parent.value is not None:
            worldMatrix =  currentNode.Parent.value.Transform.value * worldMatrix
            currentNode = currentNode.Parent.value
        Screein=avango.gua.make_inverse_mat(self.screen_node.Transform.value)
        RLin=avango.gua.make_inverse_mat(self.setup_back_rot.Transform.value)
        SPTin=avango.gua.make_inverse_mat(self.setup_back.Transform.value)
        UDin=avango.gua.make_inverse_mat(self.upDown_back_rot.Transform.value)

        return Screein*RLin*SPTin*UDin*worldMatrix
        # YOUR CODE - END (Exercise 2.9 - Model-View Transformation)

    # registers a window created in the class Renderer with the camera node
    def register_window(self, window):
        self.camera_node.OutputWindowName.value = window.Title.value
        self.camera_node.Resolution.value = window.Size.value
        avango.gua.register_window(window.Title.value, window)

    # registers a pipeline description in the class Renderer with the camera node
    def register_pipeline_description(self, pipeline_description):
        self.camera_node.PipelineDescription.value = pipeline_description
