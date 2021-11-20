import numpy as np
import pygame
import math

#initialize pygame
pygame.init()

#constants
window_size = (1600, 800)

object_color = (255, 255, 255)
bg_color = (0, 0, 0)

#create window
window = pygame.display.set_mode(window_size)
pygame.display.set_caption("SKTATW")

#Item class
class Item:
    def __init__(self, position, dimensions, color):
        
        self.center = position
        self.A = (-dimensions[0] / 2, -dimensions[1] / 2)
        self.B = (dimensions[0] / 2, -dimensions[1] / 2)
        self.C = (dimensions[0] / 2, dimensions[1] / 2)
        self.D = (-dimensions[0] / 2, dimensions[1] / 2)
        
        self.dimensions = dimensions
        self.cursor_pos = (0, 0)
        self.color = color
        self.drag = False
        self.rotate = False

    def draw(self):
        pygame.draw.line(window, self.color, (self.center[0] + self.A[0], self.center[1] + self.A[1]), (self.center[0] + self.B[0], self.center[1] + self.B[1]))
        pygame.draw.line(window, self.color, (self.center[0] + self.B[0], self.center[1] + self.B[1]), (self.center[0] + self.C[0], self.center[1] + self.C[1]))
        pygame.draw.line(window, self.color, (self.center[0] + self.C[0], self.center[1] + self.C[1]), (self.center[0] + self.D[0], self.center[1] + self.D[1]))
        pygame.draw.line(window, self.color, (self.center[0] + self.D[0], self.center[1] + self.D[1]), (self.center[0] + self.A[0], self.center[1] + self.A[1]))


    def update_pos(self, position):
        self.center = position

    def update_relative_vectors(self, A, B, C, D):
        self.A = A
        self.B = B
        self.C = C
        self.D = D
        

    def update_cursor_pos(self, position):
        self.cursor_pos = position

running = True

sq = Item((400, 250), (500, 300), object_color)

#game loop
while running:

    #event handling
    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.MOUSEBUTTONDOWN:
            position = pygame.mouse.get_pos()

            if position[0] >= sq.center[0] + sq.A[0] and position[0] <= sq.center[0] + sq.B[0] and position[1] >= sq.center[1] + sq.A[1] and position[1] <= sq.center[1] + sq.C[1]:

                if event.button == 1 and not sq.rotate:
                    sq.drag = True
                    sq.update_cursor_pos((position[0] - sq.center[0], position[1] - sq.center[1]))

                elif event.button == 3 and not sq.drag:
                    sq.rotate = True
                    sq.update_cursor_pos((position[0] - sq.center[0], position[1] - sq.center[1]))

        elif event.type == pygame.MOUSEBUTTONUP:

            if event.button == 1:
                sq.drag = False
                sq.update_cursor_pos((0, 0))
            elif event.button == 3:
                sq.rotate = False

    #draw things
    window.fill(bg_color)

    #draw grid
    #pygame.draw.line(window, object_color, (window_size[0] / 2, 0), (window_size[0] / 2, window_size[1]))
    #pygame.draw.line(window, object_color, (0, window_size[1] / 2), (window_size[0], window_size[1] / 2))

    #draw objects
    if sq.drag:
        position = pygame.mouse.get_pos()
        sq.update_pos((position[0] - sq.cursor_pos[0], position[1] - sq.cursor_pos[1]))

    elif sq.rotate:
        
        #find out angle of rotation
        position = pygame.mouse.get_pos()
        position = (position[0] - sq.center[0], position[1] - sq.center[1])
        angle_ratio = np.dot(position, sq.cursor_pos) / (np.linalg.norm(sq.cursor_pos) * np.linalg.norm(position))
        angle_ratio = 1 - math.pow(angle_ratio, 2)
        angle_ratio = math.pow(angle_ratio, 0.5)

        #create rotation matrix
        rotation_matrix = np.zeros((2, 2))
        rotation_matrix[0][1] = angle_ratio
        rotation_matrix[1][0] = -angle_ratio

        #rotate matrix edges
        A = np.matmul(rotation_matrix, sq.A)
        B = np.matmul(rotation_matrix, sq.B)
        C = np.matmul(rotation_matrix, sq.C)
        D = np.matmul(rotation_matrix, sq.D)

        print(A)
        print(B)
        print(C)
        print(D)
        print('\n')

        #update object vectors
        #sq.update_relative_vectors(A, B, C, D)
        #sq.update_cursor_pos((position[0] - sq.center[0], position[1] - sq.center[1]))



    sq.draw()
    pygame.display.update()