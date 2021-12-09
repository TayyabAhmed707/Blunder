import numpy as np
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

       
        self.quads = np.array([
            [0,1,2,3],
            [4,7,6,5],
            [4,5,1,0],
            [7,3,2,6],
            [3,7,4,0],
            [2,1,5,6]
        ])
        #self.calculate_midpoints()
        self.camera_coorinates = np.zeros_like(self.points)
        self.projected_points = np.zeros((self.points.shape[0],2))
        self.normals = np.zeros((self.quads.shape[0],1))
        self.shades = np.zeros((self.quads.shape[0],1))
        self.calculate_shades()
        

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
    def rotate(self, angles, apply=False):
        
        temp_points = np.dot(self.points,self.get_rotation_matrix(angles))

        if apply:
            self.points = temp_points
        
        return temp_points

    
    # apply=True if you want to update the object coordinates to the calculated coordinates
    def translate(self, distance, points_to_transform, along_axis, apply=False):
        temp_points = np.array(self.points)
        temp_points[points_to_transform][along_axis] += distance
        
        if apply:
            self.points = temp_points
        
        return temp_points

        
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
        self.origin = (width/2,height/2)
        pygame.init()
        self.window = pygame.display.set_mode((width,height))
        self.origin = np.array([width/2, height/2])
        self.colors =(np.random.rand(10,3)*255).astype('uint8')
        pygame.display.set_caption("Blunder")
        self.objects = [object_3d()]
        self.camera = Camera()
        self.camera.rotate([0.7,0.7,0])

        self.left_click_down = False
        self.right_click_down = False

        self.drag_vector = None
        

    def main(self):
        
        while self.running:
            # capping the fps
            #pygame.clock.tick(FPS)k
        
            self.event_handler()

            #calling update and draws functions
            self.draw()
            self.update()
    
    def event_handler(self):
        for event in pygame.event.get():
                if event.type==pygame.QUIT:
                    self.running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    #1 - left click,    2 - middle click    3 - right click     4 - scroll up      5 - scroll down
                    
                    if event.button == 1:
                        self.left_click_down = True
                        self.left_click_start_pos = self.get_mouse_pos()
                    elif event.button == 3:
                        self.right_click_down = True
                        self.right_click_start_pos = self.get_mouse_pos()

                    elif event.button == 4:
                        self.camera.zoom_in()
                    elif event.button == 5:
                        self.camera.zoom_out()
        
    
                elif event.type == pygame.MOUSEBUTTONUP:
                
                    if event.button == 1:
                        self.left_click_down = False
                    elif event.button == 3:
                        self.right_click_down = False
    
        
    def draw_axis(self, bases):
        projection_mat = np.array([
            [1,0,0],
            [0,1,0]
            ])
        pos = self.origin - np.dot(bases * 5000, np.transpose(projection_mat))
        neg =self.origin - np.dot(bases * (-5000), np.transpose(projection_mat))
    
        axis_colors = [
            [224, 25, 71],
            [31, 255, 90],
            [25, 108, 224]
        ]

        #for i in range(-20,20):
        #    pygame.draw.line(self.window  ,(100,100,100), pos[2]+i*50, neg[2]+i*50)

        for i in range(3):
            pygame.draw.line(self.window  ,axis_colors[i],pos[i], neg[i],width=2)
        

    def draw(self):
        self.window.fill((30,30,30))
        self.draw_axis(self.camera.get_camera_tranform())

       
        for obj in self.objects:
            obj.calculate_shades()
            sorted_quads = obj.sort_quads()
            for i in sorted_quads:
                pygame.draw.polygon(self.window,obj.shades[i],[obj.projected_points[obj.quads[i,0]], obj.projected_points[obj.quads[i,1]], obj.projected_points[obj.quads[i,2]], obj.projected_points[obj.quads[i,3]]])
        pygame.display.update()
    
    def get_mouse_pos(self):
        pos = pygame.mouse.get_pos() - self.origin
        pos[1] = pos[1]
        return pos
 
    def update(self):

        self.camera_control()

        for obj in self.objects:
            obj.project_to_2d(self.origin, self.camera.get_camera_tranform())

    def camera_control(self):
        if self.right_click_down:
            self.drag_vector = self.get_mouse_pos() - self.right_click_start_pos
            #### TODO: BETTER ABS
            if np.abs(self.drag_vector[0]) <  np.abs(self.drag_vector[1]):
                #Y rotation
                self.camera.rotate((0.00001*self.drag_vector[1],0,0))
            else:
                #X rotation
                self.camera.rotate((0,-0.00001*self.drag_vector[0],0))

if __name__ == "__main__":
    Window(800,600, 60).main()
    
