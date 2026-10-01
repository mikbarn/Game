import sys
import os
# Append the root directory to the python path so it can find your modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tkinter import *
from math import sqrt
import time

# Now these imports will resolve cleanly from the root directory
from Physics2D.RigidBody2D import RigidBody2D
from Physics2D.Core import Physics
from UI.Renderer import Renderer

from Math2D.Vec2D import Vec2D

def click(event):
#     global oldX, oldY
    x = event.x
    y = event.y
#   
#   
#     if pad.pos[0] < x:
#         x = x + pad.pos[0]
#     else:
#         x = -(pad.pos[0] - x)
#     if pad.pos[1] < y:
#         y = y + pad.pos[1]
#     else:
#         y = y - pad.pos[1]
#           
#       
#     pad.velocity = Vec2D(x, y)
#       
#     oldX = x
#     oldY = y

#     if y < 500 or y >=500:
#         y = 500
    pad.pos = Vec2D(x, y)
    

oldX = 0
oldY = 0

root = Tk()
cd = Physics()
width = height = 600
can = Canvas(root, bg="white", width=width, height=height)
renderer = Renderer(can)

circle = [Vec2D(10 * sqrt(3) / 2, 10 * .5), Vec2D(10 * sqrt(2) / 2, 10 * sqrt(2) / 2), Vec2D(10 * .5, 10 * sqrt(3) / 2), Vec2D(0, 10),
                Vec2D(10 * -.5, 10 * sqrt(3) / 2), Vec2D(10 * -sqrt(2) / 2, 10 * sqrt(2) / 2), Vec2D(10 * -sqrt(3) / 2, 10 * .5), Vec2D(-10, 0),
                 Vec2D(10 * -sqrt(3) / 2, 10 * -.5), Vec2D(10 * -sqrt(2) / 2, 10 * -sqrt(2) / 2), Vec2D(10 * -.5, 10 * -sqrt(3) / 2), Vec2D(0, -10),
                  Vec2D(10 * .5, 10 * -sqrt(3) / 2), Vec2D(10 * sqrt(2) / 2, 10 * -sqrt(2) / 2), Vec2D(10 * sqrt(3) / 2, 10 * -.5), Vec2D(10, 0)]
rect_vertices = [Vec2D(-10, -10), Vec2D(-10, 10), Vec2D(10, 10), Vec2D(10, -10)]
cir = RigidBody2D(circle, pos=Vec2D(150, 100), velocity=Vec2D(450, 300), angularVelocity=3, mass=100)
rect = RigidBody2D(rect_vertices, pos=Vec2D(300, 100), velocity=Vec2D(210, 380), angularVelocity=3, mass=1000)

pad_v = [Vec2D(-30, -10), Vec2D(-30, 10), Vec2D(30, 10), Vec2D(30, -10)]
pad = RigidBody2D(pad_v, pos=Vec2D(0, 0), inverseMass=0)

horizontal = [Vec2D(-5, -2), Vec2D(-5, 2), Vec2D(505, 2), Vec2D(505, -2)]
vertical = [Vec2D(-2, -5), Vec2D(-2, 505), Vec2D(2, 505), Vec2D(2, -5)]

top = RigidBody2D(horizontal, pos=Vec2D(50, 50), inverseMass=0, mass=1000000)
bot = RigidBody2D(horizontal, pos=Vec2D(50, 550), inverseMass=0, mass=1000000)
left = RigidBody2D(vertical, pos=Vec2D(50, 50), inverseMass=0 , mass=1000000)
right = RigidBody2D(vertical, pos=Vec2D(550, 50), inverseMass=0, mass=1000000)

entities = [rect, cir, top, bot, left, right, pad]
for e in entities:
    renderer.addEntity(e)
    
can.pack()

root.bind("<B1-Motion>", click)

def solve(e1, e2):
    if e1.mass == e2.mass: #trivial solution v1=u1,v2=u2
        return (e1.velocity, e2.velocity)
    
    totalMass = e1.mass + e2.mass
    massDiff = e1.mass - e2.mass

    u2 = (e2.velocity * totalMass * massDiff - e1.velocity * 2 * e1.mass * totalMass) / (massDiff * (-massDiff) - 4 * e1.mass * e2.mass)
    u1 = (e1.velocity * totalMass - u2 * 2 * e2.mass) / massDiff
    
    return (u1, u2)


friction = .999
deltaTime = .00525
while True:
    time.sleep(deltaTime)
    for e in entities:
        e.update(deltaTime)
#     cir.velocity *= friction
#     rect.velocity *= friction
    
    for i in range(0, len(entities)):
        for j in range(i + 1, len(entities)):
            e1 = entities[i]
            e2 = entities[j]

            mtv = cd.testCollisionSAT(e1, e2)
            if mtv:
                e1.pos += mtv * e1.inverseMass 
                e2.pos -= mtv * e2.inverseMass
                dur = mtv.getNormalized()
                v1, v2 = solve(e1, e2)
                e1.velocity = v1.getReflection(dur) * e1.inverseMass
                e2.velocity = v2.getReflection(-dur) * e2.inverseMass
                
    
    renderer.renderAll()
    
    root.update()
