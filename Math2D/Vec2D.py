import math

class Vec2D:
	DISTANCE_TOLERANCE = .001
	
	def __init__(self, x=0, y=0):
		self.x = self.y = 0
		if(x):
			self.x = x
		if(y):
			self.y = y
			
	def __add__(self, rhs):
		return Vec2D(self.x + rhs.x, self.y + rhs.y)
	
	#subract vectors, if vector is a offset from world origin, or position, then pos1 - pos2 can be thought of as vector from pos2 to pos1
	def __sub__(self, rhs):
		return Vec2D(self.x - rhs.x, self.y - rhs.y)
	
	#divide/multiply changes length of vector but not direction
	def __truediv__(self, scalar):
		return Vec2D(self.x / scalar, self.y / scalar)
	
	def __mul__(self, scalar):
		return Vec2D(self.x * scalar, self.y * scalar)
	
	def __iadd__(self, rhs):
		self.x += rhs.x
		self.y +=rhs.y
		return self
		
	def __isub__(self, rhs):
		self.x -= rhs.x
		self.y -=rhs.y
		return self
		
	def __imul__(self, scalar):
		self.x *= scalar
		self.y *= scalar
		return self
			
	def __idiv__(self, scalar):
		self.x /= scalar
		self.y /=scalar
		return self
	
	#dot product (scalar product). If a vector is unit vector, then dot product is magnitude of projections onto that vector. if < 0 then vectors face away from each other, if 0 perpendicular
	#if both are unit vectors, then dot product is cosine of angle between them  
	def dot(self, rhs):
		return self.x*rhs.x+self.y*rhs.y
	
	def magnitude(self):
		return math.sqrt(self.x*self.x + self.y*self.y)
	
	
	#square root is computationally more expensive than simple artihmetic, so when comparing lengths, it is more effiecient to compare square of magnitured
	def magnitudeSquared(self):
		return (self.x*self.x+self.y*self.y)
	
	
	#distance from head of 1 vector to another, same as (v1 - v2).magnitude()
	def distance(self, other):
		dx = (self.x - other.x)
		dy = (self.y - other.y)
		return math.sqrt(dx*dx + dy*dy)
	
	#Divide vector by it's length to get a unit vector of length = 1
	def getNormalized(self):
		mag = math.sqrt(self.x*self.x + self.y*self.y)
		if mag:
			return Vec2D(self.x / mag, self.y / mag)
		return Vec2D()
	
	#rotate by radians
	def getRotated(self, angle):
		cs = math.cos(angle)
		sn = math.sin(angle)
		return Vec2D(self.x*cs - self.y*sn, self.x*sn + self.y*cs)
	
	#rotate 90 degrees left
	def getLeftPerpendicular(self):
		return Vec2D(-self.y, self.x)
	
	
	def getRightPerpendicular(self):
		return Vec2D(self.y, -self.x)
	
	def __neg__(self):
		return Vec2D(-self.x, -self.y)
	
	def __eq__(self, other):
		return self.distance(other) < Vec2D.DISTANCE_TOLERANCE
	
	
	def __getitem__(self, key):
		if key == 0:
			return self.x
		elif key == 1:
			return self.y
		else:
			raise IndexError("Invalid subscript "+str(key)+" to Vec2d")
	def __setitem__(self, key, value):
		if key == 0:
			self.x = value
		elif key == 1:
			self.y = value
		else:
			raise IndexError("Invalid subscript "+str(key)+" to Vec2d")
	def __repr__(self):
		return 'Vec2d(%s, %s)' % (self.x, self.y)
	
	def getReflection(self, other):
		unitN = other.getNormalized()
		c = unitN * self.dot(unitN)
		return (c*2) - self
	
	def getDeflection(self, other): 
		unitN = other.getNormalized()
		return self - (2 * (unitN * self.dot(unitN)))
	
	def cross(self, other):
		return self.x*other[1] - self.y*other[0]
		
	