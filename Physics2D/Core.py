import math
class Physics:
    
    def testCollisionSAT(self, e1, e2): #Seperating Axis Theorem Test, returns minimum translation vector to separate 2d convex polygon
        normals = e1.worldNormals + e2.worldNormals #normals are vectors perpendicular to shape edges
        minOverlap = 999999999
        minOverlapAxis = None
        
        for norm in normals: 
            e1Dots, e2Dots = [v.dot(norm) for v in e1.worldVertices], [v.dot(norm) for v in e2.worldVertices]
            e1Min, e1Max, e2Min, e2Max = min(e1Dots), max(e1Dots), min(e2Dots), max(e2Dots)
            
            diff1 = e1Max - e2Min
            overlap = min(diff1, e2Max - e1Min)
                   
            if(overlap <= 0): #Exit if there is an axis with space between shapes
                return None
            
            if(overlap < minOverlap):
                minOverlap = overlap
                minOverlapAxis = -norm
                if(overlap != diff1):
                    minOverlapAxis = norm
                
        return minOverlapAxis * minOverlap

    
    def getAdj(self, alist, i, count): #get adjacent list elements or loop around
        return alist[max((i-1) * -(count-1), i-1)], alist[((i+1) % count)]
  
    def calcCollisionEdge(self, vertices, shape, axis): #calculate max vertex projection on a vector and return edge (vertex-pair) most-perpendicular to that vector
        sMax, vi = -99999999, 0 #max, vertex-index
        count = len(vertices)
        
        for i in range(count):
            dp = vertices[i].dot(axis)
            if(dp > sMax):
                sMax, vi = dp, i
        
        adj = self.getAdj(vertices, vi, count) #get adjacent vertices
        v1, v2, v3 = vertices[vi], adj[0], adj[1] #3 vertices
        e1, e2 = (v1,v2),(v1, v3) #2 edges
        d1, d2 = v1- v2, v1 - v3 #vectors to max-vertex along edges
        
        if(abs(d1.dot(axis)) < abs(d2.dot(axis))):
            return e1
        return e2
    
    def clip(self, v1, v2, offset, n): #takes 2 vertices and checks if they lie above or below some distance along a vector n  (the reference edge)
        d1 = v1.dot(n) - offset
        d2 = v2.dot(n) - offset
        ret = []
        if(d1 >= 0): #if vertex is beyond offset, save it
            ret.append(v1) 
        if(d2 >= 0):
            ret.append(v2)
        
        if(d1*d2 < 0): # 1 vertex was below offset, so need to clip that part off
            inc = v2-v1 #incident edge vector, n is reference
            p = d1 / (d1 - d2) #percent of incident not behind the the offset
            inc*=p #scale by that amount
            ret.append(v1+inc)
        return ret  
        
    def calcCollisionManifold(self, s1, s2, n):
        ref, inc = self.calcCollisionEdge(s1.worldVertices, s1, -n), self.calcCollisionEdge(s2.worldVertices, s2, n)
        flip = False
        vecRef, vecInc = ref[0]- ref[1], inc[0] - inc[1]
        

        if abs(vecInc.dot(n)) < abs(vecRef.dot(n)):
            ref,inc = inc, ref
            flip = True
   
        refAxis = (ref[1] - ref[0]).getNormalized()
        offset = refAxis.dot(ref[0])
            
        manifold = self.clip(inc[0], inc[1], offset, refAxis)
        offset = refAxis.dot(ref[1])
        if(len(manifold) < 2):
            return manifold
        manifold = self.clip(manifold[0], manifold[1], -offset, -refAxis)
        
        if(len(manifold) < 2):
            return manifold
        nNorm = refAxis.getLeftPerpendicular()
        toS2 = s2.pos  - s1.pos
        if(toS2.dot(nNorm) > 0):
            nNorm = -nNorm
        if(flip):
            nNorm = -nNorm
        maxV = nNorm.dot(ref[0])
        ret = []
        d = nNorm.dot(manifold[0])
        if( d - maxV >= 0):
            ret.append(manifold[0])
        d = nNorm.dot(manifold[1])
        if(nNorm.dot(manifold[1]) - maxV  >= 0):
            ret.append(manifold[1])
        if(len(ret)==0):
            pass
        return ret
    
  
         
    def calcImpulse(self, s1, s2, mtv, manifold):
        e = 1
        cp = manifold[0]
        r1 = cp-s1.pos
        r2 = cp-s2.pos
        rPerp1 = r1.getLeftPerpendicular()
        rPerp2 = r2.getLeftPerpendicular()
        velCP1 = rPerp1 * s1.angularVelocity
        velCP2 = rPerp2 * s2.angularVelocity
        relVel = (s2.velocity + velCP2) - (s1.velocity + velCP1)
        n = mtv.getNormalized()
        s1A = n.dot(rPerp1 * (r1.cross(n) / s1.inertia))
        s2A = n.dot(rPerp2 * (r2.cross(n) / s2.inertia))
        

        denom = (s1.inverseMass + s2.inverseMass) + s1A + s2A
        j = (relVel.dot(n) * -(1+e)) / denom
        s1.velocity -= n * j * s1.inverseMass
        s2.velocity += n * j * s2.inverseMass
        s1.angularVelocity -= r1.cross(n*j) / s1.inertia
        s2.angularVelocity += r2.cross(n*j) / s2.inertia
        
    def calcImpulseFriction(self, s1, s2, mtv, manifold):
        e = .8
        cp = manifold[0]
        r1 = cp-s1.pos
        r2 = cp-s2.pos
        rPerp1 = r1.getLeftPerpendicular()
        rPerp2 = r2.getLeftPerpendicular()
        velCP1 = rPerp1 * s1.angularVelocity
        velCP2 = rPerp2 * s2.angularVelocity
        relVel = (s2.velocity + velCP2) - (s1.velocity + velCP1)
        n = mtv.getNormalized() 
        s1A = n.dot(rPerp1 * (r1.cross(n) / s1.inertia))
        s2A = n.dot(rPerp2 * (r2.cross(n) / s2.inertia))
        denom = (s1.inverseMass + s2.inverseMass) + s1A + s2A
        j = (relVel.dot(n) * -(1+e)) / denom
        s1.velocity -= n * j * s1.inverseMass
        s2.velocity += n * j * s2.inverseMass
        s1.angularVelocity -= r1.cross(n*j) / s1.inertia
        s2.angularVelocity += r2.cross(n*j) / s2.inertia
        
        velCP1 = rPerp1 * s1.angularVelocity
        velCP2 = rPerp2 * s2.angularVelocity
        relVel = (s2.velocity + velCP2) - (s1.velocity + velCP1)
      
        t = relVel - (n* n.dot(relVel))
        t = t.getNormalized()
        jt = -relVel.dot(t)
        mu = max(s1.muS, s2.muS)
        jt /= (s1.inverseMass + s2.inverseMass)
        if abs(jt) < j * mu:
            fi = t * jt
        else:
            mu = max(s1.muK, s2.muK)
            fi = t * -j * mu
        s1.velocity += fi * s1.inverseMass
        s2.velocity -= fi * mu * s2.inverseMass