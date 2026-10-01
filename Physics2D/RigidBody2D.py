from Math2D.Vec2D import Vec2D

class RigidBody2D:
    def __init__(self, vertices, pos = Vec2D(), velocity=Vec2D(), orientation = 0, angularVelocity = 0, mass = 1, inverseMass = 1, inertia = 1,
                 muS = .5, muK = .5):
        self.vertices = vertices
        self.pos = pos
        self.velocity = velocity
        self.orientation = orientation
        self.angularVelocity = angularVelocity
        self.inertia = inertia
        self.mass = mass
        self.inverseMass = inverseMass
        self.muS = muS #static friction co-efficient
        self.muK = muK #kinetic friction
        self.worldVertices = []
        self.worldNormalIndices = []
        self.worldNormals = []
        self.worldVerticesList = []
        self.__initWorldVertices__()
        self.color='black'
        
    def __initWorldVertices__(self):  
        for i in range(0, len(self.vertices)):
            rotated = self.vertices[i].getRotated(self.orientation)
            self.worldVertices.append(rotated + self.pos)
            self.worldVerticesList.append(self.worldVertices[i].x)
            self.worldVerticesList.append(self.worldVertices[i].y)
        
        #maintain list of vertex pairs which define edges with non parallel normal vectors, to avoid duplicate collision checks   
        count = len(self.worldVertices)
        self.worldNormalIndices.append((0,count-1))
        for n in range(1, count):
            self.worldNormalIndices.append((n, n-1))
            
        for pair in self.worldNormalIndices:
            normal = (self.worldVertices[pair[0]]- self.worldVertices[pair[1]]).getLeftPerpendicular().getNormalized()
            self.worldNormals.append(normal)
        
        count = len(self.worldNormals)
        pairsToRemove = []
        for i in range(0, count):
            for j in range(i+1, count):
                if abs(self.worldNormals[i].dot(self.worldNormals[j].getLeftPerpendicular())) < .0001:
                    if i == 0:
                        pairsToRemove.append((i, len(self.worldVertices)-1))
                    else:
                        pairsToRemove.append((i, i-1))
                    break

        for p in pairsToRemove:
            self.worldNormalIndices.remove(p)
        
    def updateWorldVertices(self):
        count = len(self.vertices)
        for i in range(0, count):
            self.worldVertices[i] = self.vertices[i].getRotated(self.orientation)+self.pos
        
        for pair in self.worldNormalIndices:
            normal = (self.worldVertices[pair[0]]- self.worldVertices[pair[1]]).getLeftPerpendicular().getNormalized()
            self.worldNormals.append(normal)
            
        for i in range(0, count):
            j = 2*i
            v = self.worldVertices[i]
            self.worldVerticesList[j] = v.x
            self.worldVerticesList[j+1] = v.y
        
            
        
    def update(self, deltaTime):
        self.orientation+=self.angularVelocity*deltaTime
        self.pos+= (self.velocity*deltaTime)
        self.updateWorldVertices()
        