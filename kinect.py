from pykinect2 import PyKinectV2, PyKinectRuntime
from pykinect2.PyKinectV2 import *

import ctypes
import _ctypes
import pygame
import sys
import math

from Engine3D import *

# Kinect Runner

# Guided by Kinect Workshop and FlapPyKinect
# https://onedrive.live.com/?authkey=%21AMWDgqPgtkPzsAM&id=ED75CBDC5E4AB0FE%211096749&cid=ED75CBDC5E4AB0FE

class Game(object):
    def __init__(self):
        pygame.init()
        self.initScreenVar()
        # screen updates
        self.clock = pygame.time.Clock()
        # set the width and height of the window to fit in screen
        self.screen = pygame.display.set_mode(
            (960, 540),
            pygame.HWSURFACE | pygame.DOUBLEBUF,
            32
        )
        # exit game
        self.done = False
        # color and body frames from kinect runtime object
        self.kinect = PyKinectRuntime.PyKinectRuntime(
            PyKinectV2.FrameSourceTypes_Color | PyKinectV2.FrameSourceTypes_Body
        )

        self.bodies = None
        self.frameSurface = pygame.Surface(
            (
                self.kinect.color_frame_desc.Width,
                self.kinect.color_frame_desc.Height
            ),
            0,
            32
        )
        self.initBodyVar()
        self.model = Model(
                        self.frameSurface,
                        [
                        shirt(0, 0, 0, self.frameSurface,
                            [(43, 156, 54),(200,0,0),(61, 187, 198)])
                        ])
        self.initPics()
        self.initGUIVars()

    def initGUIVars(self):
        self.MENU = 1
        self.CLOSET = 2
        self.DESIGN = 3
        self.CAMERA = 4
        self.DESIGNFRONT = 5
        self.DESIGNSIDES = 6
        self.DESIGNSLEEVES = 7
        self.mode = self.MENU
        self.nextColors = [(43, 156, 54),(200,0,0),(61, 187, 198)]
        self.frontColor = [50,50,50]
        self.nextMode = None
        self.lock = False
        self.sign = 1
        self.flipLock = False

    def initPics(self):
        self.menu = pygame.image.load("menu.png")
        self.design = pygame.image.load("design.png")

    def initScreenVar(self):
        # screen variables
        self.screenWidth = 1920
        self.screenHeight = 1080
        self.sensorScreenHeight = 1.2
        self.sensorScreenWidth = 3
        self.cornerToMiddleConstant = 1000
        self.shirtCompensationHeight = 50
        self.shirtCompensationWidth = 0
        self.modelAngle = 20

    def initBodyVar(self):
        # body variables
        self.initShoulderHip()
        self.initArm()

    def initShoulderHip(self):
        self.yLeftShoulder = 0
        self.xLeftShoulder = 0
        self.zLeftShoulder = 0
        self.xRightShoulder = 0
        self.yRightShoulder = 0
        self.zRightShoulder = 0
        self.xLeftHip = 0
        self.yLeftHip = 0
        self.zLeftHip = 0
        self.xRightHip = 0
        self.yRightHip = 0
        self.zRightHip = 0


    def initArm(self):
        self.xLeftElbow = 1
        self.yLeftElbow = 1
        self.xRightElbow = 1
        self.yRightElbow = 1
        self.leftArmAngle = 0
        self.rightArmAngle = 0
        self.xRightHand = 0
        self.yRightHand = 0
        self.xLeftHand = 0
        self.yLeftHand = 0

    # Function from Kinect Workshop
    def drawColorFrame(self, frame, target_surface):
        target_surface.lock()
        address = self.kinect.surface_as_array(target_surface.get_buffer())
        ctypes.memmove(address, frame.ctypes.data, frame.size)
        del address
        target_surface.unlock()

    def sensorToScreenX(self, sensorPosX):
        screenX = (
            sensorPosX * (self.screenWidth / 3) +
            self.cornerToMiddleConstant +
            self.shirtCompensationWidth
        )
        return screenX

    def sensorToScreenY(self, sensorPosY):
        screenY = (
            -1 *
            (sensorPosY - self.sensorScreenHeight / 2) *
            (self.screenHeight / self.sensorScreenHeight)
        )
        return screenY

    def data(self, joints, type, z=False):
        ret = joints[getattr(PyKinectV2, "JointType_" + type)].Position
        if z: return (ret.x,ret.y,ret.z)
        return (ret.x, ret.y)

    def updateBody(self, joints):
        # Update body trackers
        (self.xLeftHip,
        self.yLeftHip,
        self.zLeftHip) = self.data(joints, "HipLeft", True)
        (self.xRightHip,
        self.yRightHip,
        self.zRightHip) = self.data(joints, "HipRight", True)
        (self.xLeftShoulder,
        self.yLeftShoulder,
        self.zLeftShoulder) = self.data(joints, "ShoulderLeft", True)
        (self.xRightShoulder,
        self.yRightShoulder,
        self.zRightShoulder) = self.data(joints, "ShoulderRight", True)

        self.updateBodyVars()

    def updateBodyVars(self):
        # XYZ movement calculations
        rightPart = (self.xRightShoulder + self.xRightHip) / 2
        leftPart = (self.xLeftShoulder + self.xLeftHip) / 2
        upPart = (self.yRightShoulder + self.yLeftShoulder) / 2
        downPart = (self.yRightHip + self.yLeftHip) / 2
        zAvg = (self.zRightShoulder + self.zLeftShoulder
                + self.zRightHip + self.zLeftHip) / 4
        # Converts sensor coords to pygame screen coords
        bodyX1 = self.sensorToScreenX(rightPart) + 50
        bodyY1 = self.sensorToScreenY(upPart)
        bodyX2 = self.sensorToScreenX(leftPart) - 50
        bodyY2 = self.sensorToScreenY(downPart) - self.shirtCompensationHeight
        bodyZ = zAvg * 600/1.47
        #bodyZ = 600

        bodyCenterX = ((bodyX1 + bodyX2) / 2) - 960
        bodyCenterY = ((bodyY1 + bodyY2) / 2) - 540
        bodyWidth = bodyX2 - bodyX1
        bodyHeight = -1 * (bodyY1 - bodyY2)
        # Rotation calculations
        angleXZ = 3.8/5 * self.getAngleXZ()
        # Update body shape in model
        self.model.shapes[0].update(bodyCenterX,bodyCenterY,
                                    bodyWidth,bodyHeight,
                                    angleXZ,
                                    self.leftArmAngle,
                                    self.rightArmAngle,
                                    bodyZ)

    def getAngleXZ(self):
        # Compares shoulder width difference and depth differences to get angle
        # Convert to degrees for debugging and testing readibility
        return (math.atan2(self.zRightShoulder - self.zLeftShoulder,
                          self.xRightShoulder - self.xLeftShoulder)
                           * 180.0/math.pi)

    def updateArms(self, joints):
        # Updates arm variables
        self.xLeftElbow, self.yLeftElbow = self.data(joints, "ElbowLeft")
        self.xRightElbow, self.yRightElbow = self.data(joints, "ElbowRight")
        self.updateLeftArm()
        self.updateRightArm()

    def updateLeftArm(self):
        # left arm
        xShould = self.sensorToScreenX(self.xLeftShoulder)
        yShould = self.sensorToScreenY(self.yLeftShoulder) + 40
        xElb = self.sensorToScreenX(self.xLeftElbow)
        yElb = self.sensorToScreenY(self.yLeftElbow)

        try:
            theta = math.atan((yShould - yElb)/(xElb - xShould))
        except:
            theta = math.atan((yShould - yElb)/(xElb - xShould + 1))
        thetaPrime = math.pi - math.pi/2 - theta

        self.leftArmAngle = theta

    def updateRightArm(self):
        # right arm
        xShould = self.sensorToScreenX(self.xRightShoulder)
        yShould = self.sensorToScreenY(self.yRightShoulder) + 40
        xElb = self.sensorToScreenX(self.xRightElbow)
        yElb = self.sensorToScreenY(self.yRightElbow)
        try:
            theta = -1 * math.atan((yShould - yElb)/(xElb - xShould))
        except:
            theta = -1 * math.atan((yShould - yElb)/(xElb - xShould + 1))
        thetaPrime = math.pi - math.pi/2 - theta

        self.rightArmAngle = theta

    def updateHands(self, joints):
        self.xRightHand, self.yRightHand = self.data(joints, "HandRight")
        self.xLeftHand, self.yLeftHand = self.data(joints, "HandLeft")

    def updateGUI(self):
        rHandX = self.sensorToScreenX(self.xRightHand)
        rHandY = self.sensorToScreenY(self.yRightHand)
        lHandX = self.sensorToScreenX(self.xLeftHand)
        lHandY = self.sensorToScreenY(self.yLeftHand)

        # Draw Hands
        # pygame.draw.rect(
        #     self.frameSurface,
        #     (0,0,200),
        #     (rHandX, rHandY, 100, 100)
        # )
        # pygame.draw.rect(
        #     self.frameSurface,
        #     (200,200,0),
        #     (lHandX, lHandY, 100, 100)
        # )

        # Exit Button
        if lHandX < 200 and lHandY < 200:
            self.done = True
        # Back to menu, gesture
        elif abs(lHandX-rHandX) <= 30 and abs(lHandY-rHandY) <= 30 and rHandY > 30:
            if self.mode == self.CLOSET:
                self.model.shapes.pop()
                self.model.shapes.pop()
                self.model.shapes.pop()
            self.mode = self.MENU
        # Update all modes
        if self.mode == self.MENU: self.updateMenu(rHandX,rHandY)
        elif self.mode == self.CLOSET: self.updateCloset(rHandX, rHandY, lHandY)
        elif self.mode == self.DESIGN: self.updateDesign(rHandX,rHandY,lHandY)
        elif self.mode == self.DESIGNFRONT: self.updateFront(rHandX,rHandY,lHandY)

    def updateMenu(self,rHandX,rHandY):
        # Menu processing
        # Right Panel
        if rHandX >= 1520:
            if rHandY <= 360:
                self.mode = self.CLOSET
                self.model.shapes.extend(
                    [
                    shirt(800, -400, 0, self.frameSurface,
                        [(43, 156, 54),(200,0,0),(61, 187, 198)],
                        60,100,10),
                    shirt(800, 0, 0, self.frameSurface,
                        [(200,0,0),(61, 187, 198),(43, 156, 54)],
                        60,100,10),
                    shirt(800, 400, 0, self.frameSurface,
                        [(61, 187, 198),(43, 156, 54),(200,0,0)],
                        60,100,10)
                    ])

            elif rHandY > 360 and rHandY < 720: self.mode = self.DESIGN
            elif rHandY < 1080: self.mode = self.CAMERA

    def updateCloset(self,rHandX,rHandY,lHandY):
        # Right Panel
        if rHandX >= 1520:
            if rHandY <= 360:
                self.nextColors = [(43, 156, 54),(200,0,0),(61, 187, 198)]
            elif rHandY > 360 and rHandY < 720:
                self.nextColors = [(200,0,0),(61, 187, 198),(43, 156, 54)]
            elif rHandY < 1080:
                self.nextColors = [(61, 187, 198),(43, 156, 54),(200,0,0)]
        # Change Colors
        if rHandY < 30 and lHandY < 30:
            self.model.shapes[0].colors = self.nextColors

                # self.modelAngle += 1
        # for i in range(len(self.model.shapes)):
        #     if i == 0: pass
        #     else:
        #         shirt = self.model.shapes[i]
        #         shirt.update(shirt.initX,shirt.initY,100,150,self.modelAngle,60,60)

    def updateDesign(self, rHandX, rHandY, lHandY):
        # Right Panel
        if rHandX >= 1520:
            if rHandY <= 360:
                self.nextMode = self.DESIGNFRONT
            elif rHandY > 360 and rHandY < 720:
                self.nextMode = self.DESIGNSIDES
            elif rHandY < 1080:
                self.nextMode = self.DESIGNSLEEVES
        if rHandX < 1300 and self.nextMode != None:
            self.mode = self.nextMode

    def updateFront(self, rHandX, rHandY, lHandY):
        # Flip sign gesture
        if abs(rHandY-lHandY) >= 800 and self.flipLock == False:
            print('flip')
            self.sign *= -1
            self.flipLock = True
        if abs(rHandY-lHandY) <= 500 and self.flipLock == True:
            self.flipLock = False
        # Right Panel
        if rHandX >= 1520:
            if not self.lock:
                if rHandY <= 360:
                    self.frontColor[0] += 20 * self.sign
                elif rHandY > 360 and rHandY < 720:
                    self.frontColor[1] += 20 * self.sign
                elif rHandY < 1080:
                    self.frontColor[2] += 20 * self.sign
            self.lock = True
        if rHandX <= 1400:
            self.lock = False
        self.frontColor[0] = min(255, self.frontColor[0])
        self.frontColor[1] = min(255, self.frontColor[1])
        self.frontColor[2] = min(255, self.frontColor[2])
        self.frontColor[0] = max(0, self.frontColor[0])
        self.frontColor[1] = max(0, self.frontColor[1])
        self.frontColor[2] = max(0, self.frontColor[2])

        self.model.shapes[0].colors[1] = tuple(self.frontColor)

    def drawGUI(self):
        # Exit
        pygame.draw.rect(
            self.frameSurface,
            (250,0,0),
            (0, 0, 200, 200)
        )
        pygame.draw.lines(
            self.frameSurface,
            (255,255,255),
            False,
            ([(170,30),(30,30),(30,100),(170,100),(30,100),(30,170),(170,170)]),
            10
            )

        # Menu
        # pygame.draw.line(
        #     self.frameSurface,
        #     (255,255,255),
        #     (1520,0),(1520,1080),
        #     20
        #     )

        # Design Front
        if self.mode == self.DESIGNFRONT:
            pygame.draw.rect(
                self.frameSurface,
                (200,0,0),
                (1520,0,400,360)
                )
            pygame.draw.rect(
                self.frameSurface,
                (0,200,0),
                (1520,360,400,360)
                )
            pygame.draw.rect(
                self.frameSurface,
                (0,0,200),
                (1520,720,400,360)
                )

    def blitGUI(self):
        if self.mode == self.MENU:
            self.screen.blit(self.menu,(760,0))
        if self.mode == self.DESIGN:
            self.screen.blit(self.design,(760,0))


    def runLoop(self):
        # Pygame events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
        # Reads and processes body frame from kinect
        if self.kinect.has_new_body_frame():
            self.bodies = self.kinect.get_last_body_frame()
            for i in range(self.kinect.max_body_count):
                body = self.bodies.bodies[i]
                if body.is_tracked:
                    joints = body.joints
                    self.updateBody(joints)
                    self.updateArms(joints)
                    self.updateHands(joints)

        # KeyPresses
        key = pygame.key.get_pressed()
        if sum(key) > 0:
            self.model.cam.keyPressed(key, self.model)

        # reads color images from kinect
        if self.kinect.has_new_color_frame():
            frame = self.kinect.get_last_color_frame()
            self.drawColorFrame(frame, self.frameSurface)
            frame = None

        self.model.draw()
        self.updateGUI()
        self.drawGUI()

        # changes ratio of image to output to window
        h_to_w = float(
            self.frameSurface.get_height() /
            self.frameSurface.get_width()
        )
        target_height = int(h_to_w * self.screen.get_width())
        surface_to_draw = pygame.transform.scale(
            self.frameSurface,
            (self.screen.get_width(), target_height)
        )

        self.screen.blit(surface_to_draw, (0,0))
        surface_to_draw = None
        self.blitGUI()
        pygame.display.update()

        if self.done: return False

        self.clock.tick(60)
        return True

    def run(self):
        while self.runLoop():
            pass
        self.kinect.close()
        pygame.quit()

game = Game()
game.run()

