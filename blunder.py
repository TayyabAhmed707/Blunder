import numpy as np
import pygame
import math

#git test 2
#initialize pygame

class object_3d:
    def __init__(self):
        
        #   3_______2
        #  /|      /|
        # 4−−−−−−−1 |
        # | |     | |
        # | 7−−−−−−−6
        # |/      |/
        # 8−−−−−−−5

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
            [4,5,2,0],
            [7,3,2,6],
            [3,7,4,0],
            [2,1,5,6]
        ])

        self.projected_points =np.zeros((self.points.shape[0],2))

    def project_to_2d(self, origin):
        projection_mat = np.array([
            [1,0,0],
            [0,1,0]
            ])
        self.projected_points = np.dot(self.points, np.transpose(projection_mat))
        self.projected_points = self.projected_points[:] + origin


    def get_rotation_matrix(self, angle, axis):
        if axis == 'x':
            return np.array([
                [1,0,0],
                [0,math.cos(angle), -math.sin(angle)],
                [0,math.sin(angle), math.cos(angle)]
            ])
        elif axis == 'y':
            return np.array([
                [math.cos(angle),0,-math.sin(angle)],
                [0,1,0],
                [math.sin(angle),0, math.cos(angle)]
            ])
        elif axis == 'z':
            return np.array([
                [math.cos(angle), -math.sin(angle), 0],
                [math.sin(angle), math.cos(angle), 0],
                [0,0,1]
            ])
        
    # apply=True if you want to update the object coordinates to the calculated coordinates
    def rotate(self, angle, axis, apply=False):
        
        temp_points = np.dot(self.points,self.get_rotation_matrix(angle,axis))

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


class surface_2d:
    def __init__(self,points,color):
        self.points = points
        self.color = color
        
class camera:
    def __init__(self, window):
        
        self.window = window
        self.canvas = window.window
        self.position = np.array([0,0,100])
        self.objects = [object_3d()]
        self.surfaces = []
        self.camera =  object_3d()
        self.camera.quads = None
        self.camera.points = np.array([
            [1,0,0],
            [0,1,0],
            [0,0,1]
        ])
        self.origin = np.array([window.width/2, window.height/2])

    
    def covert_to_camera_coords(self, object):
        pass

    def game_loop(self):
        running = True 
        while running:
            # capping the fps
            #pygame.clock.tick(FPS)
            # stoping the loop if quit
            for event in pygame.event.get():
                if event.type==pygame.QUIT:
                    running = False

            #calling update and draws functions
            self.draw()
            self.update()

    def update(self):
        self.objects[0].rotate(0.001,'x',True)
        self.objects[0].rotate(0.001,'y',True)
        for obj in self.objects:
            obj.project_to_2d(self.origin)
        
        
    def draw(self):
        self.canvas.fill((0,0,0))

        for obj in self.objects:
            for quad in obj.quads:
                pygame.draw.polygon(self.canvas,(255,255,255),[obj.projected_points[quad[0]], obj.projected_points[quad[1]], obj.projected_points[quad[2]], obj.projected_points[quad[3]]])
        pygame.display.update()


class Window:
    def __init__(self, width, height, fps):
        self.width = width
        self.height = height
        self.fps = 60
        self.origin = (width/2,height/2)
        pygame.init()
        self.window = pygame.display.set_mode((width,height))
        self.camera = camera(self)
        pygame.display.set_caption("Blunder")

    def main(self):
        self.camera.game_loop()
        


if __name__ == "__main__":
    Window(1600,1200, 60).main()
    
