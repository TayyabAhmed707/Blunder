import numpy as np
import pygame
import math


#initialize pygame
pygame.init()

WIDTH = 1600
HEIGHT = 800
FPS = 60
WHITE = (255,255,255)

origin = (WIDTH/2,HEIGHT/2)

triangles = np.array([
    [0,1,2],
    [0,2,3],
    [4,5,6],
    [4,6,7],
    [1,5,6],
    [1,6,2],
    [4,5,1],
    [4,1,0],
    [4,0,3],
    [4,3,7],
    [7,6,3],
    [6,2,3]

])

normals = np.zeros_like(triangles)
for triangle in triangles:
    pass

#constants
window_size = (WIDTH, HEIGHT)
object_color = (255, 255, 255)
bg_color = (0, 0, 0)



points =np.array([
    [-70,-70,70],
    [70,-70,70],
    [70,70,70],
    [-70,70,70],
    [-70,-70,-70],
    [70,-70,-70],
    [70,70,-70],
    [-70,70,-70]
])
normals = np.cross(points[triangles[:, 1]] - points[triangles[:, 0]] , points[triangles[:, 2]] - points[triangles[:, 1]])
light_vector = np.array([-1,-1,-1])
light_magnitude =np.sqrt(light_vector.dot(light_vector))

print("normals")
print(normals)
print("angles")
#print(angles)
projection_mat = np.array([
    [1,0,0],
    [0,1,0]
])



projected_points =np.zeros((8,2))
temp_points =np.zeros_like(points)

#create window
window = pygame.display.set_mode(window_size)
pygame.display.set_caption("Blunder")

def screen_coordinates(pos):
    return pos - origin

#the main function containing the gameloop
def main():
    running = True
    while running:
        # capping the fps
        #pygame.clock.tick(FPS)
        # stoping the loop if quit
        for event in pygame.event.get():
            if event.type==pygame.QUIT:
                running = False

        #calling update and draws functions
        draw()
        update()
        

angle = 0.0
    
def update():
    global projected_points
    global angle 
    global temp_points
    global angles
    global normals

    
    angle = (angle + 0.001) % 360
        
    #normals = np.cross(points[triangles[:, 1]] - points[triangles[:, 0]],points[triangles[:, 2]] - points[triangles[:, ]])

    #angles = np.arccos(np.inner(light_vector, normals[:])/(light_magnitude * np.linalg.norm(normals[:])))

    rot_X = np.array([
        [1,0,0],
        [0,math.cos(angle), -math.sin(angle)],
        [0,math.sin(angle), math.cos(angle)]
    ])
    rot_Y = np.array([
        [math.cos(angle),0,-math.sin(angle)],
        [0,1,0],
        [math.sin(angle),0, math.cos(angle)]
    ])
    rot_Z = np.array([
        [math.cos(angle), -math.sin(angle), 0],
        [math.sin(angle), math.cos(angle), 0],
        [0,0,1]
    ])
    
    temp_points = np.dot(points,rot_X )

   
    temp_points = np.dot(temp_points,rot_Y)

    projected_points = np.dot(temp_points, np.transpose(projection_mat))

    projected_points = projected_points[:] + origin

    pygame.display.update()


def draw():
    window.fill((0,0,0))
    for i in range(len(triangles)):
        pygame.draw.polygon(window,WHITE,[projected_points[triangles[i,0]],projected_points[triangles[i,1]],projected_points[triangles[i,2]]])
        

    

if __name__ == "__main__":
    main()