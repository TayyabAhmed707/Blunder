import numpy as np
from numpy.linalg import norm
import pygame
import math

#git test 2
#initialize pygame

class object_3d:

    def __init__(self):
        
        #   2_______1
        #  /|      /|
        # 3−−−−−−−0 |
        # | |     | |
        # | 6−−−−−−−5
        # |/      |/
        # 7−−−−−−−4
        
        self.points = np.array([
            [50,50,50],
            [50,-50,50],
            [-50,-50,50],
            [-50,50,50],
            [50,50,-50],
            [50,-50,-50],
            [-50,-50,-50],
            [-50,50,-50]
            ])

        self.untransformed_points = np.array(self.points)

        self.quads = np.array([
            [0,1,2,3],
            [4,7,6,5],
            [4,5,1,0],
            [7,3,2,6],
            [3,7,4,0],
            [2,1,5,6]
        ])
        self.is_selected = True
        self.camera_coorinates = np.zeros_like(self.points)
        self.projected_points = np.zeros((self.points.shape[0],2))
        self.normals = np.zeros((self.quads.shape[0],1))
        self.shades = np.zeros((self.quads.shape[0],1))
        self.selected_quads = []
        self.calculate_shades()
        self.selected_quads_history=[]

    def take_snapshot(self):
        self.untransformed_points = np.array(self.points)
        self.quad_history = np.array(self.quads)
        self.selected_quads_history = self.selected_quads.copy()
    
    def revert_snapshot(self):
        self.points = np.array(self.untransformed_points)
        self.quads = np.array(self.quad_history)
        self.selected_quads = self.selected_quads_history

    def project_to_2d(self, origin, camera_axis):
        projection_mat = np.array([
            [1,0,0],
            [0,1,0]
            ])
            
        self.camera_coorinates = np.dot(self.points,camera_axis)
        z = self.camera_coorinates[:,[2]]
        self.projected_points = np.dot(self.camera_coorinates, np.transpose(projection_mat))
        self.projected_points = self.projected_points
    
        self.projected_points = self.projected_points + origin

    def calculate_shades(self):
        v1 = self.camera_coorinates[self.quads[:,1]]-self.camera_coorinates[self.quads[:,0]]
        v2 = self.camera_coorinates[self.quads[:,2]]-self.camera_coorinates[self.quads[:,1]]
        self.normals = np.cross(v1,v2)
        self.normals = self.normals/ np.linalg.norm(self.normals[:])

        light = np.array([[1,-1, 2]])
        
        inner = np.inner(light,self.normals)
        norms = np.linalg.norm(self.normals[:]) * np.linalg.norm(light)
        cos = inner / norms
        rad = np.arccos(np.clip(cos, -1.0, 1.0))
        deg = np.rad2deg(rad)
        deg = deg - deg.min()
        deg = 200* deg/deg.max() + 55
        self.shades= np.tile((deg).transpose(), (1, 3)).astype("uint8")
    
    def sort_quads(self):
        cam_coords = self.camera_coorinates
        quad_midpoints = (cam_coords[self.quads[:,0]]+cam_coords[self.quads[:,1]]+cam_coords[self.quads[:,2]]+cam_coords[self.quads[:,3]])/4
        quad_z = quad_midpoints[:,2]
        sorted_quads = np.argsort(quad_z.astype('int16'))
        return sorted_quads

    def get_rotation_matrix(self, angles):
        z = angles[0]
        y = angles[1]
        x = angles[2]

        return np.array([
            [math.cos(x)*math.cos(y),   math.cos(x)*math.sin(y)*math.sin(z) - math.sin(x)*math.cos(z),  math.cos(x)*math.sin(y)*math.cos(z) + math.sin(x)*math.sin(z)],
            [math.sin(x)*math.cos(y),   math.sin(x)*math.sin(y)*math.sin(z) + math.cos(x)*math.cos(z),  math.sin(x)*math.sin(y)*math.cos(z) - math.cos(x)*math.sin(z)],
            [-math.sin(y),  math.cos(y)*math.sin(z),    math.cos(y)*math.cos(z)]
        ])
        # apply=True if you want to update the object coordinates to the calculated coordinates
   
    def rotate(self, angles):
        self.points = np.dot(self.points,self.get_rotation_matrix(angles))

    def translate(self, displacement):
        self.points = self.points + displacement

    def scale(self,size):
        for i in range(3):
            if size[i] == 0:
                size[i] = 1  
        
        scale_mat = np.array([
            [size[0],0,0],
            [0,size[1],0],
            [0,0,size[2]]
        ])
        self.points = np.dot(self.points,scale_mat)
    
    def rotate_quads(self, angles):
        if not self.selected_quads:
            return
        selected_points = self.points[np.unique(self.quads[self.selected_quads])]
        selected_mp = selected_points.sum(axis=0)/selected_points.shape[0]
        selected_points = selected_points - selected_mp
        selected_points = np.dot(selected_points,self.get_rotation_matrix(angles))
        selected_points = selected_points + selected_mp
        self.points[np.unique(self.quads[self.selected_quads])] = selected_points
    
    def translate_quads(self, displacement):
        if not self.selected_quads:
            return
        self.points[np.unique(self.quads[self.selected_quads])] = self.points[np.unique(self.quads[self.selected_quads])] +displacement

    def scale_quads(self, size):
        if not self.selected_quads:
            return
        for i in range(3):
            if size[i] == 0:
                size[i] = 1  
        
        scale_mat = np.array([
            [size[0],0,0],
            [0,size[1],0],
            [0,0,size[2]]
        ])

        self.quads[self.selected_quads]
        selected_points = self.points[np.unique(self.quads[self.selected_quads])]
        selected_mp = selected_points.sum(axis=0)/selected_points.shape[0]
        selected_points = selected_points - selected_mp
        selected_points = np.dot(selected_points,scale_mat)
        selected_points = selected_points + selected_mp
        self.points[np.unique(self.quads[self.selected_quads])] = selected_points
    
    def extrude(self):
        
        #   2_______1
        #  /|      /
        # 3−−−−−−−0 
        #   2_______1
        #  /|      /|
        # 3−−−−−−−0 |
        # | |     | |
        # | 6−−−−−−−5
        # |/      |/
        # 7−−−−−−−4
        if not self.selected_quads:
            return
       
        new_index = self.points.shape[0]
        old_quad = self.quads[self.selected_quads[0]]
        new_points = self.points[old_quad]
        new_points_indexes = range(new_index,new_index + 4)
        new_quad = [new_points_indexes[0],new_points_indexes[1],new_points_indexes[2],new_points_indexes[3]]
        new_quads = [new_quad]
        for i in range(4):
            new_quads.append([new_quad[i%4],old_quad[i%4],old_quad[(i+1)%4],new_quad[(i+1)%4]])

        self.selected_quads = [self.quads.shape[0]]
        self.points = np.append(self.points, new_points, axis=0)
        self.quads = np.append(self.quads, new_quads, axis=0)
        print(self.points)
        
        normal = np.cross(self.points[new_quad[2]]-self.points[new_quad[1]], self.points[new_quad[0]]-self.points[new_quad[1]])

        normal = normal/np.linalg.norm(normal)
        normal[0] = -normal[0]
        normal[2] = -normal[2]
        return normal


        
    def check_for_collisions(self, pos, deselect=True):
        sorted_quads = self.sort_quads()
        if deselect:
            self.selected_quads = []
        for i in reversed(sorted_quads):
            points = self.projected_points[self.quads[i]]
            max_x = points[:,0].max()
            max_y = points[:,1].max()
            min_x = points[:,0].min()
            min_y = points[:,1].min()
            
            if pos[0] > min_x and pos[0] < max_x and pos[1] > min_y and pos[1] < max_y:
                self.selected_quads.append(i)
                print('working')
                return

        self.selected_quads = []


class Camera:
    def __init__(self):
        self.position = np.array([0,0,0])
        self.rotation = np.array([0,0,0])
        self.tranform = np.array([
            [1,0,0],
            [0,1,0],
            [0,0,1]
        ])
        self.zoom = 1

    def get_camera_tranform(self):
        # https://en.wikipedia.org/wiki/Rotation_matrix
        
        z = self.rotation[0]
        y = self.rotation[1]
        x = self.rotation[2]
        self.tranform = np.array([
            [math.cos(x)*math.cos(y),   math.cos(x)*math.sin(y)*math.sin(z) - math.sin(x)*math.cos(z),  math.cos(x)*math.sin(y)*math.cos(z) + math.sin(x)*math.sin(z)],
            [math.sin(x)*math.cos(y),   math.sin(x)*math.sin(y)*math.sin(z) + math.cos(x)*math.cos(z),  math.sin(x)*math.sin(y)*math.cos(z) - math.cos(x)*math.sin(z)],
            [-math.sin(y),  math.cos(y)*math.sin(z), math.cos(y)*math.cos(z)]
        ])

        zoom = np.array([
            [self.zoom,0,0],
            [0,self.zoom,0],
            [0,0,self.zoom]
        ])

        self.tranform = np.dot(zoom,self.tranform)

        return self.tranform


    def zoom_in(self):
        self.zoom += 0.1

    def zoom_out(self):
        if(self.zoom > 0.2):
            self.zoom -= 0.05

    def rotate(self, angles):
        self.rotation[1] = (self.rotation[1] + angles[1]) % (2 * math.pi)
        self.rotation = self.rotation + angles
        if self.rotation[0] > math.pi/2:
            self.rotation[0] =  math.pi/2
        if self.rotation[0] < -math.pi/2:
            self.rotation[0] = -math.pi/2


        

class Window:
    def __init__(self, width, height, fps):
        self.running = True
        self.width = width
        self.height = height
        self.fps = 60
        self.mouse_last_pos = None
        self.origin = (width/2,height/2)
        self.mode = ['object','none']
        self.active_axis = np.array([1,1,1])
        pygame.init()
        self.font = pygame.font.Font("comforta.ttf", 24)
        self.window = pygame.display.set_mode((width,height))
        self.origin = np.array([width/2, height/2])
        self.colors =(np.random.rand(10,3)*255).astype('uint8')
        pygame.display.set_caption("Blunder")
        self.objects = np.array([object_3d()])
        self.selected_objects = [0]
        self.active_object = self.objects[0]
        self.camera = Camera()
        self.camera.rotate([0.7,0.7,0])
        self.message = self.font.render('Welcome to Blunder',True,(255,255,255),(50,50,50))
        self.left_click_down = False
        self.right_click_down = False
        self.extruded = False

        self.drag_vector = None
        

    def main(self):
        clock = pygame.time.Clock()
        while self.running:
            # capping the fps

            clock.tick(self.fps)
        
            self.event_handler()

            #calling update and draws functions
            self.update()
            self.draw()
            
    
    def event_handler(self):
        for event in pygame.event.get():
                if event.type==pygame.QUIT:
                    self.running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    #1 - left click,    2 - middle click    3 - right click     4 - scroll up      5 - scroll down
                    
                    if event.button == 1:
                        self.left_click_down = True
                        self.left_click_start_pos = self.get_mouse_pos()

                        if self.mode[1] != 'none':
                            if self.mode[1] == 'extrude':
                                self.extruded = False
                            self.mode[1] = 'none'
                            self.active_axis = np.array([1,1,1])
                            self.update_message('')
                        

                        if self.mode[0] == 'edit':
                            if pygame.key.get_pressed()[pygame.K_LSHIFT]:
                                self.active_object.check_for_collisions(self.get_mouse_pos()+self.origin, False)

                            else:
                                self.active_object.check_for_collisions(self.get_mouse_pos()+self.origin)
                        else:
                            if pygame.key.get_pressed()[pygame.K_LSHIFT]:
                                self.select_object(self.get_mouse_pos()+self.origin, False)
                            else:
                                self.select_object(self.get_mouse_pos()+self.origin)
                                
                    elif event.button == 3:
                        self.right_click_down = True
                        self.right_click_start_pos = self.get_mouse_pos()
                        if self.mode[1] != 'none':
                            if self.mode[1] == 'extrude':
                                self.extruded = False
                            for obj in self.objects[self.selected_objects]:
                                obj.revert_snapshot()
                                self.active_axis = np.array([1,1,1])
                                self.mode[1] = 'none'
                                self.update_message('')

                    elif event.button == 4:
                        self.camera.zoom_in()
                    elif event.button == 5:
                        self.camera.zoom_out()
        
    
                elif event.type == pygame.MOUSEBUTTONUP:
                
                    if event.button == 1:
                        self.left_click_down = False
                    elif event.button == 3:
                        self.right_click_down = False

                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_s:
                        self.update_message('Scaling in all directions, press x, y or z for a specific axis')
                        self.mode[1] = 'scale'
                        self.mouse_last_pos = self.get_mouse_pos()
                        for obj in self.objects[self.selected_objects]:
                            obj.take_snapshot()

                    elif event.key == pygame.K_r:
                        self.update_message('Press x, y or z for a specific axis For rotation')
                        self.active_axis = np.array([0,1,0])
                        self.mode[1] = 'rotate'
                        self.mouse_last_pos = self.get_mouse_pos()
                        for obj in self.objects[self.selected_objects]:
                            obj.take_snapshot()

                    elif event.key == pygame.K_t:
                        self.update_message('Press x, y or z for a specific axis For Translation')
                        self.active_axis = np.array([0,1,0])
                        self.mode[1] = 'translate'
                        self.mouse_last_pos = self.get_mouse_pos()
                        for obj in self.objects[self.selected_objects]:
                            obj.take_snapshot()
                    
                    elif event.key == pygame.K_e:
                        if self.mode[0] == 'edit':
                            self.mode[1] = 'extrude'
                        self.mouse_last_pos = self.get_mouse_pos()
                        for obj in self.objects[self.selected_objects]:
                            obj.take_snapshot()

                    elif event.key == pygame.K_i:
                        if self.mode[0] == 'edit':
                            self.mode[1] = 'inset'
                        self.mouse_last_pos = self.get_mouse_pos()
                        for obj in self.objects[self.selected_objects]:
                            obj.take_snapshot()

                    elif event.key == pygame.K_x:
                        if self.mode[1] != 'none':
                            self.active_axis = np.array([1,0,0])
                            for obj in self.objects[self.selected_objects]:
                                obj.revert_snapshot()
                            self.update_message('along x-axis')
                    elif event.key == pygame.K_y:
                        if self.mode[1] != 'none':
                            self.active_axis = np.array([0,1,0])
                            for obj in self.objects[self.selected_objects]:
                                obj.revert_snapshot()
                            self.update_message('along y-axis')

                    elif event.key == pygame.K_z:
                         if self.mode[1] != 'none':
                            self.active_axis = np.array([0,0,1])
                            for obj in self.objects[self.selected_objects]:
                                obj.revert_snapshot()
                            self.update_message('along z-axis')

                    elif event.key == pygame.K_n:
                        if pygame.key.get_pressed()[pygame.K_LSHIFT]:
                            self.active_object = object_3d()
                            self.selected_objects = [len(self.selected_objects)]
                            self.objects = np.append(self.objects,self.active_object)


                    elif event.key == pygame.K_TAB:
                        if self.mode[0] == 'object':
                            self.mode[0] = 'edit'
                            self.mode[1] = 'none'
                            self.active_object =self.objects[self.selected_objects[-1]]

                        else:
                            self.mode[0] = 'object'
                            self.mode[1] = 'none'
                            print(self.mode)

                    
    def draw_axis(self, bases):
        projection_mat = np.array([
            [1,0,0],
            [0,1,0]
            ])
        pos = self.origin - np.dot(bases * 7000, np.transpose(projection_mat))
        neg =self.origin - np.dot(bases * (-7000), np.transpose(projection_mat))
    
        axis_colors = [
            [224, 25, 71],
            [31, 255, 90],
            [25, 108, 224]
        ]

        for i in range(3):
            pygame.draw.line(self.window  ,axis_colors[i],pos[i], neg[i],width=2)

    def draw_message_window(self):
        pygame.draw.rect(self.window,(50, 50, 50),[[0,0],[self.width,30]])
        textRect = self.message.get_rect()
        textRect.center = (self.width // 2, 15)
        self.window.blit(self.message, textRect)

    def update_message(self, message):
        
        self.message =self.font.render(message,True,(255,255,255),(50,50,50))

    def draw(self):
        self.window.fill((30,30,30))
        self.draw_axis(self.camera.get_camera_tranform())

        
        for obj in self.objects:
            obj.calculate_shades()
            sorted_quads = obj.sort_quads()

            if self.mode[0] =='object' and obj.is_selected:
                for i in sorted_quads:
                    pygame.draw.polygon(self.window,(255, 167, 66),np.array([obj.projected_points[obj.quads[i,0]], obj.projected_points[obj.quads[i,1]], obj.projected_points[obj.quads[i,2]], obj.projected_points[obj.quads[i,3]]]),width=5) 
            for i in sorted_quads:
                pygame.draw.polygon(self.window,obj.shades[i],[obj.projected_points[obj.quads[i,0]], obj.projected_points[obj.quads[i,1]], obj.projected_points[obj.quads[i,2]], obj.projected_points[obj.quads[i,3]]])

            if self.mode[0] =='edit':
                for i in obj.selected_quads:
                    pygame.draw.polygon(self.window,(255, 167, 66),np.array([obj.projected_points[obj.quads[i,0]], obj.projected_points[obj.quads[i,1]], obj.projected_points[obj.quads[i,2]], obj.projected_points[obj.quads[i,3]]]),width=2) 


        self.draw_message_window()
        pygame.display.update()
    
    def get_mouse_pos(self):
        pos = pygame.mouse.get_pos() - self.origin
        return pos
    

    def select_object(self,pos ,clear=True):
        if clear:
            for obj in self.objects:
                obj.is_selected = False
            self.selected_objects = []
        
        for i in range(self.objects.shape[0]):
            points = self.objects[i].projected_points
            max_x = points[:,0].max()
            max_y = points[:,1].max()
            min_x = points[:,0].min()
            min_y = points[:,1].min()
            print(pos)
            print("max_x "+str(max_x))
            print("min_x "+str(min_x))
            print("max_y "+str(max_y))
            print("min_y "+str(min_y))
            if pos[0] > min_x and pos[0] < max_x and pos[1] > min_y and pos[1] < max_y:
                self.selected_objects.append(i)
                self.active_object = self.objects[i]
                self.objects[i].is_selected = True

                return

        self.selected_objects = []




    def get_tranform_magnitute(self):
        drag_vector = self.get_mouse_pos() - self.mouse_last_pos 
        drag_magnitude = np.linalg.norm(drag_vector)
        self.mouse_last_pos = self.get_mouse_pos()
        cos = drag_vector[0]/drag_magnitude
        rad = np.arccos(np.clip(cos, -1.0, 1.0))
        deg = np.rad2deg(rad)
        if drag_vector[1] > 0:
            deg=-deg
       
        drag_magnitude = round(drag_magnitude*0.01, 4)

        return drag_magnitude, deg
        
    
    def update(self):

        self.camera_control()
        if self.mode[1] == 'scale':
            
            drag_magnitude, deg = self.get_tranform_magnitute()
            if deg > -45 and deg < 135:
                for obj in self.objects[self.selected_objects]:
                    if self.mode[0] =='object':
                        obj.scale(self.active_axis*(1+drag_magnitude))
                    else:
                        obj.scale_quads(self.active_axis*(1+drag_magnitude))
            else:
                for obj in self.objects[self.selected_objects]:
                    if self.mode[0] =='object':
                        obj.scale(self.active_axis/(1+drag_magnitude))
                    else:
                        obj.scale_quads(self.active_axis/(1+drag_magnitude))
        
        if self.mode[1] == 'rotate':
            drag_magnitude, deg = self.get_tranform_magnitute()
            
            if deg > -45 and deg < 135:
                drag_magnitude = -drag_magnitude

            for obj in self.objects[self.selected_objects]:
                    if self.mode[0] =='object':
                        obj.rotate(self.active_axis*(-drag_magnitude))
                    else:
                        obj.rotate_quads(self.active_axis*(-drag_magnitude))
    
        if self.mode[1] == 'translate':
            drag_magnitude, deg = self.get_tranform_magnitute()   
            camera_rot = np.rad2deg(self.camera.rotation[1])
            axis = self.active_axis
            
            if camera_rot < 45 or camera_rot>270:
                axis = axis * [-1,1,1]

            if camera_rot > 180:
                axis = axis * [1,1,-1]
            
            if deg > -45 and deg < 135:
                for obj in self.objects[self.selected_objects]:
                    if self.mode[0] =='object':
                        obj.translate(-100*drag_magnitude*axis)
                    else:
                        obj.translate_quads(-100*drag_magnitude*axis)
            else:
                for obj in self.objects[self.selected_objects]:
                    if self.mode[0] =='object':
                        obj.translate(100*drag_magnitude*axis)
                    else:
                        obj.translate_quads(100*drag_magnitude*axis)

        if self.mode[1] == 'extrude':
            
            self.active_axis = self.active_object.extrude()
            self.mode[1] = 'translate'

        
        if self.mode[1] == 'inset':
            self.active_object.extrude()
            self.active_object.scale_quads(self.active_axis*0.5)
            self.mode[1] = 'scale'

        for obj in self.objects:
            obj.project_to_2d(self.origin, self.camera.get_camera_tranform())

    def camera_control(self):
        if self.right_click_down:
            self.drag_vector = self.get_mouse_pos() - self.right_click_start_pos
            if np.abs(self.drag_vector[0]) <  np.abs(self.drag_vector[1]):
                #Y rotation
                self.camera.rotate((0.00005*self.drag_vector[1],0,0))
            else:
                #X rotation
                self.camera.rotate((0,-0.00005*self.drag_vector[0],0))

if __name__ == "__main__":
    Window(900,600, 60).main()
    
