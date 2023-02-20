# My Boid 
# Author: Qianru Zhou
# Reference from PyNBoids - a Boids simulation - github.com/Nikorasu/PyNBoids
# @ nikorasu85@gmail.com

import pygame
from pygame.sprite import Sprite
from sys import exit
import random
from random import randint
import numpy as np

# Bird(birdNum, birdData, scene)
class Bird(Sprite):
    def __init__(self, birdOrder, birdData, scene):
        Sprite.__init__(self)
        self.image = pygame.image.load('image/plane.png')
        self.image = pygame.transform.scale(self.image, (30,30))
        self.size_x = 10
        self.size_y = 6
        self.birdSize = 20
        self.scene = scene
        self.birdOrder = birdOrder
        self.birdData = birdData
        
        # 每只鸟初始角度和位置均随机
        self.ang = random.randint(0, 360)
        self.maxW, self.maxH = self.scene.get_size()
        self.rect = self.image.get_rect(center=(randint(50, self.maxW - 50), randint(50, self.maxH - 50)))
        self.pos = pygame.Vector2(self.rect.center)
        
    # update(frames, speed)
    def update(self, frames, speed):
        turnDir = xDir = yDir = 0
        turnRate = 120*frames
        # Make list of neighbor birds, sorted by distance
        otherBirds = np.delete(self.birdData, self.birdOrder, 0)
        distances = (self.pos.x - otherBirds[:,0])**2 + (self.pos.y - otherBirds[:,1])**2
        # 数字越大，黏性越强，因为考虑的邻居越多
        closestBirdsId = np.argsort(distances)[:9]
        closestBirds = otherBirds[closestBirdsId]
        closestBirds[:,3] = np.sqrt(distances[closestBirdsId])
        closestBirds = closestBirds[closestBirds[:,3] < self.birdSize*12 ]
        
        if closestBirds.size > 1:
            y = np.sum(np.sin(np.deg2rad(closestBirds[:,2])))
            x = np.sum(np.cos(np.deg2rad(closestBirds[:,2])))
            
            # 计算邻居鸟的平均位置和方向
            angle_average = np.rad2deg(np.arctan2(y,x))
            pos_average = (np.mean(closestBirds[:,0]), np.mean(closestBirds[:,1]))
            
            # 如果与最近的邻居太近
            if closestBirds[0,3] < self.birdSize:
                pos_average = (closestBirds[0,0], closestBirds[0,1])
                
            # 算出目标与现有的方向、距离差别
            pos_diff = pygame.Vector2(pos_average) - self.pos
            distance_diff, angle_diff = pygame.math.Vector2.as_polar(pos_diff)
            
            # 如果与邻居距离差足够小，则与邻居方向一致
            if distance_diff < self.birdSize*4:
                angle_diff = angle_average
            
            # smooth steering
            angle_to_steer = (angle_diff - self.ang) + 180
            if abs(angle_diff - self.ang) > 1.2:
                turnDir = (angle_to_steer/360 - (angle_to_steer // 360)) * 360 - 180
                
            # 如果与最近的邻居太近，飞离
            if closestBirds[0,3] < self.birdSize and distance_diff < self.birdSize:
                turnDir = -turnDir
            
        # 触碰到边缘返回机制
        margin = 42
        if min(self.pos.x, self.pos.y, self.maxW-self.pos.x, self.maxH - self.pos.y) < margin:
            if self.pos.x < margin:
                angle_diff = 0
            elif self.pos.x > self.maxW - margin:
                angle_diff = 180
            if self.pos.y < margin:
                angle_diff = 90
            elif self.pos.y > self.maxH - margin:
                angle_diff = 270
            # 如果处于边缘地带，加大转速
            turnRate = 120 * frames
            angle_to_steer = (angle_diff - self.ang) + 180
            #self.image = pygame.transform.rotate(self.image, angle_to_steer)
            turnDir = (angle_to_steer/360 - (angle_to_steer // 360)) * 360 - 180
            distance_edge = min(self.pos.x, self.pos.y, self.maxW - self.pos.x, self.maxH - self.pos.y)
            turnRate = turnRate + (1 - distance_edge/margin)*(20 - turnRate)
        
        if turnDir != 0:
            self.ang += turnRate * abs(turnDir) / turnDir
            self.ang %= 360
        # 转图像，匹配飞行方向
        # self.image = pygame.transform.rotate(self.image, -self.ang)
        # 重新校准中心点
        self.rect = self.image.get_rect(center=self.rect.center)
        self.dir = pygame.Vector2(1,0).rotate(self.ang).normalize()
        self.pos += self.dir * frames * (speed + (7 - closestBirds.size)*2)
        # 更新鸟的位置
        self.rect.center = self.pos
        self.birdData[self.birdOrder, :3] = [self.pos[0], self.pos[1], self.ang]


#主场景
class MainScene(object):
    def __init__(self, birdNum, frames, speed):
        self.size = (1000, 600)
        self.scene = pygame.display.set_mode([self.size[0], self.size[1]])
        self.pause = False
        self.frames = frames
        self.speed = speed
        self.bgcolor = (37,61,36)
        
        #创建鸟群 
        self.birdSwarm = pygame.sprite.Group()
        self.birdData = np.zeros((birdNum, 4), dtype=float)
        for n in range(birdNum):
            self.birdSwarm.add(Bird(n, self.birdData, self.scene))
    
    # 主循环
    def run_scene(self):
        #放音乐
        pygame.mixer.init()
        music_bg = pygame.mixer.Sound('bird-src/Jibbs-ChainHangLow.mp3')
        music_bg.play(loops=-1) #播放音乐（loops=-1循环播放）
        
        clock = pygame.time.Clock()
        
        now = 0
        while True:
            # 处理事件
            for event in pygame.event.get():
                if event.type == pygame.QUIT or event.type == pygame.KEYDOWN or event.type == pygame.K_ESCAPE:
                    exit()
            
            framePerSecond = clock.tick(60) / 1000
            self.scene.fill(self.bgcolor)
            self.birdSwarm.update(framePerSecond, self.speed)
            self.birdSwarm.draw(self.scene)
            
            pygame.display.update()
                

if __name__ == "__main__":
    mainScene = MainScene(30, 60, 160)
    mainScene.run_scene()