import sys
import os
import random
import copy
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

class Entity(RigidBody2D):
    def __init__(self, vertices, pos=Vec2D(0,0),velocity=Vec2D(0,0), angularVelocity=0,orientation=0,  health=100, inverseMass=0, inertia=1, muS=0, muK=0,color='black'):
        RigidBody2D.__init__(self, vertices=vertices, pos=pos, velocity=velocity,angularVelocity=angularVelocity, orientation=orientation, inverseMass=inverseMass, inertia=inertia, 
                             muS=muS, muK=muK)
        self.health=health
        self.color= color
    def hurt(self, amnt):
        self.health-=amnt
        self.health = max(self.health,0)
        
class Craft(Entity):
    def __init__(self, vertices, pos, inverseMass, inertia, muS, muK, health, color):
        self.turnRate = 1.5
        self.fowardThrust = 150
        self.MAX_SPEED = 300
        self.MAX_ANGULAR = 15
        self.heading=Vec2D(1,0)
        self.speed=0
        Entity.__init__(self, vertices=vertices, pos=pos, velocity=Vec2D(0,0),angularVelocity=0, orientation=0, inverseMass=inverseMass, inertia=inertia, 
                             muS=muS, muK=muK, health=health, color=color)
        
    def turnLeft(self):
        self.angularVelocity = min(-self.turnRate, self.angularVelocity)
        self.angularVelocity-=self.turnRate 
        self.angularVelocity = max(self.angularVelocity, -self.MAX_ANGULAR)
    
    def turnRight(self):
        self.angularVelocity = max(self.turnRate, self.angularVelocity)
        self.angularVelocity+=self.turnRate 
        self.angularVelocity = min(self.angularVelocity, self.MAX_ANGULAR)
    def foward(self):
        self.speed = min(self.speed+self.fowardThrust, self.MAX_SPEED)
        heading=self.heading.getRotated(self.orientation)
        self.velocity = (self.velocity + heading*self.speed).getNormalized() * self.speed
        
        
    def reverse(self):
        self.speed = max(self.speed-self.fowardThrust, -self.MAX_SPEED/2)
        heading=self.heading.getRotated(self.orientation)
        self.velocity= heading*self.speed
        
    def update(self, deltaTime):
        decayRate = .89
        self.angularVelocity*=decayRate
        self.velocity*=.98
        self.speed*=.98

        RigidBody2D.update(self, deltaTime)
        
width = height = 800
root = Tk()
cd = Physics()
can = Canvas(root, bg="gray", width=width, height=height)
can.pack()
renderer = Renderer(can)


damMult = .01
sidewidth = 20
sqr_vertices = [Vec2D(-10,-10), Vec2D(-10,10), Vec2D(10,10), Vec2D(10,-10)]

class HealthBar(Entity):
    def __init__(self,width, height, target, offset):
        self.rightVerts = [Vec2D(width/2,height/2), Vec2D(width/2,-height/2)]
        self.leftVerts=[Vec2D(-width/2,-height/2), Vec2D(-width/2,height/2)]
        self.originalHealth=target.health
        self.vertices=self.leftVerts+self.rightVerts
        self.target=target
        self.offset=offset
        self.width = width
        self.health = target.health
        Entity.__init__(self, vertices=self.vertices, pos=target.pos+offset, velocity=Vec2D(0,0), angularVelocity=0, 
                        orientation=0, health=target.health, inverseMass=0, inertia=0, muS=0, muK=0, color='green')
        
    def hurt(self, amnt):
        p = amnt / self.originalHealth
        delta_x = -1 * self.width * p
        for v in self.rightVerts:
            v.x += delta_x 
            if v.x < self.leftVerts[0].x:
                v.x = self.leftVerts[0].x
        self.vertices = self.leftVerts + self.rightVerts
        self.health = self.target.health
            
    def update(self):
        self.pos = self.target.pos+self.offset
        d = self.health-self.target.health
        if(d > 0):
            self.hurt(d)
        self.updateWorldVertices()
        

def randVec(myMax):
    return Vec2D(random.uniform(-1,1)*myMax, random.uniform(-1,1)*myMax)
def makeTarget(scale, vertices):
    v = copy.deepcopy(vertices)
    for vert in v:
        vert*=scale
    target = Entity( v, pos=Vec2D(width/2, height/2)+randVec(300), velocity=Vec2D(-2,-3), angularVelocity=5, orientation = 0, inverseMass = 1000 / scale, inertia =3 * scale,muS = .2, muK = .01, health=50*scale)
    helathbar = HealthBar(.5*target.health, 5, target, Vec2D(15 *scale,-15 *scale))
    return target, helathbar

vert_vertices = [Vec2D(-sidewidth/2,-height/2), Vec2D(-sidewidth/2,height/2), Vec2D(sidewidth/2,height/2), Vec2D(sidewidth/2,-height/2)]
hori_vertices = [Vec2D(-width/2 + 2*sidewidth, -sidewidth/2), Vec2D(-width/2+2*sidewidth, sidewidth/2), Vec2D(width/2-2*sidewidth, sidewidth/2), Vec2D(width/2-2*sidewidth, -sidewidth/2)]
avatar_vertices = [Vec2D(-10, -20), Vec2D(-10, 20), Vec2D(40, 0)]
bullet_vertices=[Vec2D(-5,-5), Vec2D(-5,5), Vec2D(10,0)]
debris_vertices=[Vec2D(-6, -4), Vec2D(-5, 6), Vec2D(2,8)]
leftwall = Entity(vert_vertices, pos=Vec2D(sidewidth,height/2), inverseMass = 0,  inertia = 999999)
rightwall = Entity(vert_vertices, pos=Vec2D(width-sidewidth,height/2), inverseMass = 0,  inertia = 999999)
topwall = Entity(hori_vertices, pos =Vec2D(width/2, sidewidth), inverseMass = 0,  inertia = 999999)
bottomwall = Entity(hori_vertices, pos=Vec2D(width/2, height-sidewidth), inverseMass = 0, inertia = 999999, orientation=0)
midwall1 = Entity([v*.8 for v in hori_vertices], pos=Vec2D(width/2, height-sidewidth-300), inverseMass = 0, inertia = 999999, orientation=2)
craft = Craft(avatar_vertices, pos = Vec2D(200,100), inverseMass=4000, inertia=.5, muS=.3, muK=.04, health = 20, color='blue')
static = [leftwall,rightwall,topwall, bottomwall, midwall1]
targets = [makeTarget(random.uniform(.5,5), sqr_vertices) for i in range(0, 5)]
entities = [craft]+[target[0] for target in targets]
hp=HealthBar(50, 5, craft, Vec2D(25,-25))
renderer.addEntity(hp)
for t,h in targets:
    renderer.addEntity(h)
debris = []

for e in entities+static:
    renderer.addEntity(e)


def left(event):
    craft.turnLeft()
def right(event):
    craft.turnRight()
def up(event):
    craft.foward()
def down(event):
    craft.reverse()
def shoot(event):
    bullet=Entity(bullet_vertices, pos=craft.worldVertices[2], velocity=Vec2D(1,0).getRotated(craft.orientation)*800, inverseMass=500, orientation=craft.orientation, inertia=1, health=20, color='red')
    entities.append(bullet)
    renderer.addEntity(bullet)
    renderer.setColor(bullet, bullet.color)
    
def randTri(scale):
    return [Vec2D(random.random() * -scale, random.random()*-scale),Vec2D(random.random() * -scale, random.random()*scale),Vec2D(random.random() * scale, random.uniform(-1,1)*scale)]

expCount = 30
debris_tris=[randTri(10) for i in range(0,expCount)]


   
def explode(e):
    entities.remove(e)
    renderer.removeEntity(e)
    for i in range(0,expCount):
        p=Vec2D(e.pos[0], e.pos[1])
        v = copy.deepcopy(debris_tris[i])
        crap=Entity(v, pos=p, velocity=randVec(300), angularVelocity=5, inverseMass=500000,color=e.color)
        debris.append(crap)
        renderer.addEntity(crap)
        renderer.setColor(crap, crap.color)
        
root.bind('<Left>', left)
root.bind('<Right>', right)
root.bind('<Up>', up)
root.bind('<Down>', down)
root.bind('<space>', shoot)

deltaTime = .015
while True:
    renderer.renderAll()
    time.sleep(deltaTime)
    
    for e in entities:
        e.update(deltaTime)
    hp.update()
    for t,h in targets:
        h.update()
    while(len(debris) > 200):
        renderer.removeEntity(debris.pop(0))
    for d in debris:
        for v in d.vertices:
            v*=.99
        d.update(deltaTime)
    for i in range(0, len(entities)):
        for j in range(i+1, len(entities)):
            e1 = entities[i]
            e2 = entities[j]        
            mtv = cd.testCollisionSAT(e1, e2)
            if mtv is not None:         
                e1.pos+=mtv*.7
                e2.pos-=mtv*.7
                manifold = cd.calcCollisionManifold(e1, e2, mtv)      
                if(len(manifold) >= 1): 
                    dam=(e1.velocity-e2.velocity).magnitude()*damMult
                    cd.calcImpulseFriction(e1, e2, mtv, manifold)
                    e1.hurt(dam)
                    e2.hurt(dam)
    for e in entities:
        for s in static: 
            mtv=cd.testCollisionSAT(e, s)
            if(mtv is not None):
                e.pos+=mtv
                e.hurt(e.velocity.magnitude()*damMult)
                manifold = cd.calcCollisionManifold(e, s, mtv)
                if(len(manifold) < 1): 
                    pass
                else:
                    cd.calcImpulseFriction(e, s, mtv, manifold)   
    for e in entities:
        if(e.health <=0):
            explode(e)
    
    root.update()
