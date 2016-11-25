import pygame
import numpy as np
import math
import bisect

# 3D engine

# Guided by pseudocode from this tutorial:
# https://gamedevelopment.tutsplus.com/tutorials/lets-build-a-3d-graphics-engine-points-vectors-and-basic-concepts--gamedev-8143
# Additional info about 3D engines from:
# https://www.youtube.com/watch?v=g4E9iq0BixA

#Customized 3D engine for my project

minZ = 250

class Point(object):

    def __init__(self, x, y, z, surface):
        self.x = x
        self.y = y
        self.z = z
        self.surface = surface
        self.screenHeight = surface.get_height()

        # have (0,0) point be in the middle
        self.cX = int(surface.get_width() / 2)
        self.cY = int(surface.get_height() / 2)

        self.updateDrawCoord()

    def convertTo3D(self,coord,center):
        # Adding Distortion for z coordinate to be drawn
        # Larger z towards center
        # z best works from range 100 to 300
        try: return int(coord * ((self.screenHeight / 2) / self.z) + center)
        except:
            return int(coord * ((self.screenHeight / 2) / (self.z+1)) + center)

    def updateDrawCoord(self):
        self.drawX = self.convertTo3D(self.x,self.cX)
        self.drawY = self.convertTo3D(self.y,self.cY)

    def drawPoint(self):
        pygame.draw.circle(
            self.surface,
            (255,0,0),
            (self.drawX,self.drawY),
            20
        )

class Cube(object):
    def __init__(self,x,y,z,length,surface):
        centerX = x
        centerY = y
        centerZ = z
        side = length/2
        # z dimension is half of the x and y dimensions
        zSide = length/4
        # points of the cube
        self.points = [
         Point(centerX - side, centerY - side, centerZ - zSide + minZ, surface),
         Point(centerX + side, centerY - side, centerZ - zSide + minZ, surface),
         Point(centerX + side, centerY + side, centerZ - zSide + minZ, surface),
         Point(centerX - side, centerY + side, centerZ - zSide + minZ, surface),
         Point(centerX - side, centerY - side, centerZ + zSide + minZ, surface),
         Point(centerX + side, centerY - side, centerZ + zSide + minZ, surface),
         Point(centerX + side, centerY + side, centerZ + zSide + minZ, surface),
         Point(centerX - side, centerY + side, centerZ + zSide + minZ, surface)
         ]
        # edges of the cube (point1 index, point2 index)
        self.edges = [
                (0,1),(1,2),(2,3),(3,0),
                (4,5),(5,6),(6,7),(7,4),
                (0,4),(1,5),(2,6),(3,7)
                ]
        # faces of the cube (point1 index, point2 index, point3 index,
        # point4 index)
        self.faces = [
                (0,1,2,3),
                (4,5,6,7),
                (2,3,7,6),
                (0,1,5,4),
                (1,2,6,5),
                (0,3,7,4)
                ]

    def draw(self, surface):
        # Draw points
        for point in self.points:
            point.drawPoint()
        # Draw edges
        for edge in self.edges:
            point1Index, point2Index = edge[0], edge[1]
            point1, point2 = self.points[point1Index], self.points[point2Index]
            pygame.draw.line(
                surface,
                (255,0,0),
                (point1.drawX, point1.drawY),
                (point2.drawX, point2.drawY),
                20
                )
        self.drawFaces(surface)

    def drawFaces(self,surface):
        # Draw faces
        # Sort faces first so only visible faces are shown
        indicies = self.sortFacesByZ()
        for faceIndex in indicies:
            face = self.faces[faceIndex]
            pointList = []
            for pointIndex in face:
                point = self.points[pointIndex]
                pointList.append((point.drawX, point.drawY))
            pygame.draw.polygon(
            surface,
            (0, 0, 200),
            pointList
        )


    def sortFacesByZ(self):
        # Sort the faces by their average Z value
        # High Z values are at the front, low z values at the back
        zValues = []
        zSortedIndices = []
        for faceIndex in range(len(self.faces)):
            face = self.faces[faceIndex]
            point1,point2 = self.points[face[0]],self.points[face[1]]
            point3,point4 = self.points[face[2]],self.points[face[3]]
            faceZ = (point1.z + point2.z + point3.z + point4.z) / 4
            # Use bisect to determine where to place the new value of Z
            index = bisect.bisect(zValues, faceZ)
            # Place value and index to corresponding list
            zValues.insert(index, faceZ)
            zSortedIndices.insert(index, faceIndex)
        return zSortedIndices

class Body(object):
    def __init__(self,x,y,z,length,surface):
        centerX = x
        centerY = y
        centerZ = z
        side = length/2
        # z dimension is half of the x and y dimensions
        zSide = length/4
        # points of the cube
        self.points = [
         Point(centerX - side, centerY - side, centerZ - zSide + minZ, surface),
         Point(centerX + side, centerY - side, centerZ - zSide + minZ, surface),
         Point(centerX + side, centerY + side, centerZ - zSide + minZ, surface),
         Point(centerX - side, centerY + side, centerZ - zSide + minZ, surface),
         Point(centerX - side, centerY - side, centerZ + zSide + minZ, surface),
         Point(centerX + side, centerY - side, centerZ + zSide + minZ, surface),
         Point(centerX + side, centerY + side, centerZ + zSide + minZ, surface),
         Point(centerX - side, centerY + side, centerZ + zSide + minZ, surface)
         ]
        # edges of the cube (point1, point2)
        self.edges = [
                (0,1),(1,2),(2,3),(3,0),
                (4,5),(5,6),(6,7),(7,4),
                (0,4),(1,5),(2,6),(3,7)
                ]

        def draw(self, surface):
            # draws points
            for point in self.points:
                point.drawPoint()
            # draws edges
            for edge in self.edges:
                point1Index, point2Index = edge[0], edge[1]
                point1, point2 = self.points[point1Index], self.points[point2Index]

                pygame.draw.line(
                    surface,
                    (255,0,0),
                    (point1.drawX, point1.drawY),
                    (point2.drawX, point2.drawY),
                    20
                    )

class Model(object):
    def __init__(self, surface):
        self.shapes = [Cube(0, 0, 0, 200, surface),
                      Cube(300, 150, 0, 100, surface)]
        self.surface = surface
        self.cam = Camera(self.shapes)

    def draw(self):
        for shape in self.shapes:
            shape.draw(self.surface)

class Camera(object):
    def __init__(self,shapes):
        self.shapes = shapes

    def keyPressed(self, key, model):
        # moves camera and changes view of the objects
        self.dX, self.dY, self.dZ = 0, 0, 0
        self.rotXY, self.rotXZ = 0,0
        step = 5
        radStep = .05
        # process keypresses
        if key[pygame.K_w]: self.dY -= step
        if key[pygame.K_s]: self.dY += step
        if key[pygame.K_a]: self.dX -= step
        if key[pygame.K_d]: self.dX += step
        if key[pygame.K_z]: self.dZ += step
        if key[pygame.K_x]: self.dZ -= step

        if key[pygame.K_o]: self.rotXY += radStep
        if key[pygame.K_p]: self.rotXY -= radStep

        if key[pygame.K_k]: self.rotXZ += radStep
        if key[pygame.K_l]: self.rotXZ -= radStep


        for shape in self.shapes:
           for point in shape.points:
                point.x += self.dX
                point.y += self.dY
                point.z += self.dZ
                (point.x, point.y, point.z) = self.rotate(
                    point.x, point.y, point.z,
                    self.rotXY,
                    "XY"
                    )
                (point.x, point.y, point.z) = self.rotate(
                    point.x, point.y, point.z,
                    self.rotXZ,
                    "XZ"
                    )
                point.updateDrawCoord()


    def rotate(self, x, y, z, radians, plane):
        orig = [x, y, z]
        c = math.cos(radians)
        s = math.sin(radians)

        # Rotation Matrices info is from:
        # https://gamedevelopment.tutsplus.com/tutorials/lets-build-a-3d-graphics-engine-linear-transformations--gamedev-7716
        # https://en.wikipedia.org/wiki/Rotation_matrix

        if plane == "XY":
            # Matrix for transformation in XY plane
            rotMatrix = [
                [c, -s, 0],
                [s,  c, 0],
                [0,  0, 1]
                ]
        elif plane == "XZ":
            # Matrix for transformation in XZ plane
            rotMatrix = [
                [c,  0, s],
                [0,  1, 0],
                [-s, 0, c]
                ]
        return np.dot(orig,rotMatrix)
