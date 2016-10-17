from math3d import VectorN
import pygame
import math
import math3d

class Camera():
    def __init__(self,pos,coi,up,fov,near,surf):
        self.position=pos
        self.point_of_interest=coi
        self.up=up
        self.fov=fov
        self.near=near
        self.surface=surf
        self.aspect_ratio=self.surface.get_width()/self.surface.get_height()
        z_between=self.point_of_interest-self.position
        self.z_axes=z_between.normalized()
        self.x_axes=(self.up.cross(self.z_axes)).normalized()
        self.y_axes=self.z_axes.cross(self.x_axes)
        height=math.tan(math.radians(self.fov/2))*self.near*2
        self.view_plane_dimensions=(self.aspect_ratio*height,height)
        a=near*self.z_axes
        b=(self.view_plane_dimensions[1]/2)*self.y_axes
        c=(self.view_plane_dimensions[0]/2)*self.x_axes
        self.view_plane_origin=self.position+a+b-c
    def print(self):
        print("Camera Position:",self.position)
        print("COI:",self.point_of_interest)
        print("Up",self.up)
        print("X-Axis:",self.x_axes,"\nY-Axes:",self.y_axes,"\nZ-Axes:",self.z_axes)
        print("Dimensions:",self.surface.get_width(),"x",self.surface.get_height(),"pixels.")
        print("Aspect Ratio:",self.aspect_ratio)
        print("Camera Field-of-View:",self.fov,"degrees.")
        print("Camera Near:",self.near,"world units.")
        print("Viewplane Dimensions:",self.view_plane_dimensions[0],"x",self.view_plane_dimensions[1],"world units.")
        print("Viewplane origin",self.view_plane_origin,"\n")
    def getPixelPosition(self,ix,iy):
        s=(ix/(self.surface.get_width()-1))*self.view_plane_dimensions[0]
        t=(iy/(self.surface.get_height()-1))*self.view_plane_dimensions[1]
        d=s*self.x_axes
        e=-t*self.y_axes
        return self.view_plane_origin+d+e
class Plane():
    def __init__(self,normal,distance,color):
        self.mNormal=normal.normalized()
        self.mDistance=distance
        self.colors=color
    def rayIntersection(self,ray):
        """
        :param ray:
        :return: Return None if no hit, will return distance along ray if there is a hit.
        """
        s=self.mNormal.dot(ray.direction)
        if s==0:
            return None
        t=(self.mDistance-ray.origin.dot(self.mNormal))/s
        if t>0:
            return t
        return None
    # def draw(self,window):
    #
    #     pass
    def get_normal(self,point,distance=0):
        return self.mNormal
    def get_material(self):
        return self.colors
    def has(self,pt,distance):
        # print(pt.dot(self.mNormal),distance)
        # print(pt)
        # print(abs(self.mNormal.dot(pt)-self.mDistance))
        return abs(pt.dot(self.mNormal)-self.mDistance)
class Sphere():
    def __init__(self,center,radius,color):
        self.mCenter=center
        self.mRadius=radius
        self.rs=radius*radius
        self.color=color
    def rayIntersection(self,ray):
        # ray.getDistanceToPoint(self.mCenter=
        q=self.mCenter-ray.origin
        para_dist=q.dot(ray.direction)
        perp=q-para_dist*ray.direction
        perpsq=perp.dot(perp)
        if perpsq>self.rs:
            return None
        else:
            offset=(self.rs-perpsq)**.5
            t=para_dist-offset
            if t>0:
                # print(t)
                return t
            return None
    # def draw(self,window):
    #     pygame.draw.rect(window,(123,0,123),(self.mCenter[0],self.mCenter[1]),self.mRadius)
    def get_normal(self,point,distance=0):
        return (point-self.mCenter).normalized()
    def get_material(self):
        return self.color
class AABB():
    def __init__(self,p1,p2,color):
        self.color=color
        self.mMinPoint=[0,0,0]
        self.mMaxPoint=[0,0,0]
        if p1[0]>p2[0]:
            self.mMinPoint[0]=p2[0]
            self.mMaxPoint[0]=p1[0]
        else:
            self.mMinPoint[0]=p1[0]
            self.mMaxPoint[0]=p2[0]
        if p1[1]>p2[1]:
            self.mMinPoint[1]=p2[1]
            self.mMaxPoint[1]=p1[1]
        else:
            self.mMinPoint[1]=p1[1]
            self.mMaxPoint[1]=p2[1]
        if p1[2]>p2[2]:
            self.mMinPoint[2]=p2[2]
            self.mMaxPoint[2]=p1[2]
        else:
            self.mMinPoint[2]=p1[2]
            self.mMaxPoint[2]=p2[2]
        self.plane_list=[Plane(VectorN(-1,0,0),-self.mMinPoint[0],self.color),Plane(VectorN(1,0,0),self.mMaxPoint[0],self.color),Plane(VectorN(0,-1,0),-self.mMinPoint[1],self.color),
                         Plane(VectorN(0,1,0),self.mMaxPoint[1],self.color),Plane(VectorN(0,0,-1),-self.mMinPoint[2],self.color),Plane(VectorN(0,0,1),self.mMaxPoint[2],self.color)]
    def get_normal(self,pt,distance=0):
        return self.plane.mNormal
    def rayIntersection(self,ray):
        self.hit_list=[]
        self.plane=None
        index_list=[]
        for plane in self.plane_list:
            distance=plane.rayIntersection(ray)
            if distance!=None :
                point=ray.getPT(distance)
                e1=.0000001
                # print(distance,point)
                if self.mMaxPoint[0]+e1>= point[0]>=self.mMinPoint[0]-e1 and self.mMaxPoint[1]+e1>=point[1]>=self.mMinPoint[1]-e1 and self.mMaxPoint[2]+e1>=point[2]>=self.mMinPoint[2]-e1:
                    self.hit_list.append(distance)
                    index_list.append(plane)
        closest=None
        for distance in range(len(self.hit_list)):
            if closest==None:
                closest=self.hit_list[distance]
                self.plane=index_list[distance]
            elif closest>self.hit_list[distance]:
                closest=self.hit_list[distance]
                self.plane=index_list[distance]
        # print(closest)
        return closest
    def get_material(self):
        return self.color
class Polymesh():
    #subtract 1 from all from f values in obj file
    def __init__(self,filename,offset,scale,color):
        self.triangles=[]
        self.verticies=[]
        smallest_x,smallest_y,smallest_z=None,None,None
        largest_x,largest_y,largest_z=None,None,None
        with open(filename) as f:
            for line in f:
                if line[0]=='v':
                    lineSplit=line.split(' ')
                    self.verticies.append(VectorN(offset[0]+float(lineSplit[1])*scale,offset[1]+float(lineSplit[2])*scale,offset[2]+float(lineSplit[3])*scale))
                    vert=self.verticies[len(self.verticies)-1]
                    if smallest_x==None :
                        smallest_x=vert[0]
                    if smallest_y==None:
                        smallest_y=vert[1]
                    if smallest_z==None:
                        smallest_z=vert[2]
                    if largest_x==None:
                        largest_x=vert[0]
                    if largest_y==None:
                        largest_y=vert[1]
                    if largest_z==None:
                        largest_z=vert[2]
                    if smallest_x>vert[0] :
                        smallest_x=vert[0]
                    if smallest_y>vert[1]:
                        smallest_y=vert[1]
                    if smallest_z==vert[2]:
                        smallest_z=vert[2]
                    if largest_x<vert[0]:
                        largest_x=vert[0]
                    if largest_y<vert[1]:
                        largest_y=vert[1]
                    if largest_z<vert[2]:
                        largest_z=vert[2]
                if line[0]=='f':
                    lineSplit=line.split(' ')
                    self.triangles.append(VectorN(float(lineSplit[1])-1,float(lineSplit[2])-1,float(lineSplit[3])-1))
        self.mColor=color
        self.mAABB=AABB(VectorN(smallest_x,smallest_y,smallest_z),VectorN(largest_x,largest_y,largest_z),self.mColor)
    def rayIntersection(self,ray):
        if self.mAABB.rayIntersection(ray)!=None:
            self.last=None
            closest=None
            index=0
            for triangles in self.triangles:
                # print(self.verticies[int(triangles[0])])
                a=self.verticies[int(triangles[0])]
                b=self.verticies[int(triangles[1])]
                c=self.verticies[int(triangles[2])]
                v=a-b
                w=c-b
                # print(v,w)
                normal=(v).cross(w)
                # print("Normal",normal)
                area=normal.magnitude()/2
                p=Plane(normal,normal.normalized().dot(a),self.get_material())
                d=p.rayIntersection(ray)
                if d==None or d<0:
                    continue
                point=ray.getPT(d)
                # print("Point",point,"V:",v,"W:",w,"X:",x)
                barya=((point-a).cross(b-point).magnitude()/2)/area
                baryb=((point-a).cross(c-point).magnitude()/2)/area
                baryc=((point-b).cross(c-point).magnitude()/2)/area
                # print("Barya:",barya,"Bartb:",baryb,"Baryc:",baryc)
                if(1-.0000001<barya+baryb+baryc<1+.00000001 and (closest==None or closest>d)):
                    closest=d
                    self.last=normal.normalized()
            return closest
        else:
            return None
    def get_normal(self,pt,distance=0):
        return self.last
    def get_material(self):
        return self.mColor
#A drawable mathmatical ray.
class Ray():
    def __init__(self,origin,direction):
        """
        Constructor
        :param origin: The point(VectorN) at which this Ray will originate.
        :param direction: The direction(VectorN) that this Ray will be facing.
        """
        if len(origin)!=len(direction):
            raise ValueError("The dimensions of the direction and the point must be the same.")
        self.origin=origin
        self.direction=direction.normalized()
    def getPT(self,scalar):
        """
        :param scalar: A distance down the current ray.
        :return: returns a point that is scalar distance along this current ray
        """
        return self.origin+self.direction.normalized()*scalar
    def drawPygame(self,surface,line_thickness,color,distance):
        """
        A draw method for this ray.
        :param surface: A pygame surface that this ray will be rendered onto.
        :param line_thickness: The thickness of the ray that will be rendered
        :param color: The color of the ray.
        :param distance: The amount of the infinite ray that should be rendered.
        :return:
        """
        pygame.draw.line(surface,color,self.origin.int(),(self.origin+(self.direction*distance)).int(),line_thickness)
        pygame.draw.circle(surface,(123,123,123),self.origin.int(),2)
    def getDistanceToPoint(self,point):
        """
        :param point: a Vector N point.
        :return: returns the scalar distance from a point to the ray.
        """
        dist=point-self.origin
        if dist.dot(self.direction)<0:
            return None
        # print(dist)
        parallel=dist.dot(self.direction)/(self.direction.dot(self.direction))*self.direction
        # print(parallel)
        return(dist-parallel).magnitude()
    def draw_projection(self,player_pos,window):
        """
        :param player_pos: The position of the player.
        :param window: The window that the objects will be rendered onto.
        """
        dist=player_pos-self.origin
        parallel=dist.dot(self.direction)/self.direction.dot(self.direction)*self.direction
        if dist.dot(self.direction)>0:
            pygame.draw.line(window,(255,0,0),self.origin,self.origin+parallel,2)
            pygame.draw.line(window,(0,255,0),self.origin+parallel,player_pos,2)
class Material():
    def __init__(self,am,dif,spe,shine):
        self.ambient=am
        self.diffuse=dif
        self.specular=spe
        self.shiny=shine

class Light():
    def __init__(self,pos,dif,specular,atten):
        self.position=pos
        self.diffuse=dif
        self.specular=specular
        self.attenuation=atten
class RayTracer():
    def __init__(self,cam,amb):
        self.screen=pygame.display.set_mode((300,200))
        self.clk=pygame.time.Clock()
        self.allShapes = []
        self.running=True
        self.once=True
        self.lights=[]
        self.amb=amb
        self.cam=cam
    def get_closest(self,R,allShapes):
        closest=None
        closest_result=20000
        for obj in allShapes:
            result=obj.rayIntersection(R)
            # print(obj,result)
            if result!=None and (closest==None or result<closest_result):
                closest=obj
                closest_result=result
        return closest,closest_result
    def one_line(self,y,screen,allShapes,cam):
        for x in range(0,screen.get_width()):
            rayOrigin=cam.getPixelPosition(x,y)
            rayDirection=rayOrigin-cam.position
            R=Ray(rayOrigin,rayDirection)
            closest,distance=self.get_closest(R,allShapes)
            pt=R.getPT(distance)
            if closest==None:
                screen.set_at((x,y),(30,30,30))
            else:
                cDiff=VectorN(0,0,0)
                cSpec=VectorN(0,0,0)
                closest_color_items=closest.get_material()
                amb_c=self.amb.p_mul(closest_color_items.ambient)
                total=amb_c
                normal=closest.get_normal(pt,distance)
                for light in self.lights:
                    shadowRay=Ray(pt+0.001*normal,light.position-pt)
                    shadowCheck,other=self.get_closest(shadowRay,allShapes)
                    light_dist=(light.position-pt).magnitude()
                    # print(other,light_dist,shadowCheck,pt)
                    if shadowCheck!=None and other>=0 and other!=20000 and other>.0001 and other<light_dist:
                        continue
                    l_dir=light.position-pt
                    l_dir=l_dir.normalized()
                    dStr=l_dir.dot(normal)
                    if dStr<=0:
                        cDiff=VectorN(0,0,0)
                    else:
                        cDiff=dStr*light.diffuse.p_mul(closest_color_items.diffuse)
                    R=2*(l_dir.dot(normal))*normal-l_dir
                    V=(cam.position-pt).normalized()
                    sStr=V.dot(R)
                    if sStr<=0:
                        cSpec=VectorN(0,0,0)
                    else:
                        cSpec=(sStr**closest_color_items.shiny)*(light.specular.p_mul(closest_color_items.specular))
                    total+=cDiff+cSpec
                screen.set_at((x,y),total.clamp()*255)
                # print("\n\n")
    def add_object(self,item):
        self.allShapes.append(item)
    def add_lights(self,light):
        self.lights.append(light)
    def run(self):
        pygame.init()
        y=0
        while self.running:
            if y<self.screen.get_height():
                self.one_line(y,self.screen,self.allShapes,cam)
                y+=1
            elapsed=self.clk.tick()/1000
            keysPressed=pygame.key.get_pressed()
            evt=pygame.event.poll()
            if keysPressed[pygame.K_ESCAPE]:
                running=False
                break
            if evt.type==pygame.QUIT:
                running=False
                break
            pygame.display.flip()
        pygame.quit()
if __name__ == "__main__":
    light1=Light(VectorN(0,50,0),VectorN(1.0,1.0,1.0),VectorN(1.0,1.0,1.0),VectorN(0.0,0.0,0.0))
    light2=Light(VectorN(50,50,-50),VectorN(0.4,0,0),VectorN(0,0.6,0),VectorN(0,0,0))
    cam=Camera(VectorN(-15.0,19.0,-30.0),VectorN(2.0,5.0,3.0),VectorN(0.0,1.0,0.0),60.0,1.5,pygame.Surface((300,200)))
    sphere=Material(VectorN(0.3,0,0),VectorN(1,0,0),VectorN(1,1,1),10.0)
    plane1=Material(VectorN(0,0.5,0),VectorN(0,1,0),VectorN(1,0,0),2.0)
    plane2=Material(VectorN(0,0,0.1),VectorN(0,0,1),VectorN(1,0,1),6.0)
    aabb=Material(VectorN(0.5,0.3,0.1),VectorN(1,1,0),VectorN(0.5,1.0,0.5),30.0)
    mesh=Material(VectorN(0.2,0,0.4),VectorN(0.7,0,1),VectorN(1,1,1),50.0)
    r=RayTracer(cam,VectorN(1.0,1.0,1.0))
    r.add_object(Sphere(VectorN(2, 5, 3), 7,sphere))
    r.add_object(Plane(VectorN(0,1,0), 5,plane1))
    r.add_object(Plane(VectorN(0.1,1,0), 4,plane2))
    r.add_lights(light1)
    r.add_lights(light2)
    r.add_object(AABB(VectorN(2,9,-6),VectorN(8,15,0),aabb))
    r.add_object(Polymesh("sword.obj",VectorN(-10,8,3),1.0,mesh))
    r.run()
    # cam.print()
    # pass
    # print("Pixel(0,0)=",cam.getPixelPosition(0,0))
    # print("Pixel(299,199)=",cam.getPixelPosition(299,199))
    # print("Pixel(150,100)=",cam.getPixelPosition(150,100))
    # print("Pixel(113,542)=",cam.getPixelPosition(113,542))
    # print("Pixel(723,11)=",cam.getPixelPosition(723,11),"\n\n")
    # allShapes.append(Sphere(VectorN(2, 5, 3), 7, VectorN(1, 0, 0)))
    # allShapes.append(Plane(VectorN(0,1,0), 5, VectorN(0,1,0)))
    # allShapes.append(Plane(VectorN(0.1,1,0), 4, VectorN(0,0,1)))
    # allShapes.append(AABB(VectorN(2,9,-6),VectorN(8,15,0),VectorN(1,1,0)))
    # print(allShapes)
    # running=True
    # once=True
    # y=0
    # while running:
    #     if y<screen.get_height():
    #         for x in range(0,screen.get_width()):
    #             # print("ww")
    #             rayOrigin=cam.getPixelPosition(x,y)
    #             rayDirection=rayOrigin-cam.position
    #             R=Ray(rayOrigin,rayDirection)
    #             closest=None
    #             closest_result=20000
    #             for obj in allShapes:
    #                 # print(obj)
    #                 result=obj.rayIntersection(R)
    #                 if result!=None and (closest==None or result<closest_result):
    #                     closest=obj
    #                     closest_result=result
    #             if closest==None:
    #                 screen.set_at((x,y),(30,30,30))
    #             else:
    #                 screen.set_at((x,y),closest.get_material())
    #                 # print(x,y)
    #         y+=1
    #     elapsed=clk.tick()/1000
    #     keysPressed=pygame.key.get_pressed()
    #     evt=pygame.event.poll()
    #     if keysPressed[pygame.K_ESCAPE]:
    #         running=False
    #         break
    #     if evt.type==pygame.QUIT:
    #         running=False
    #         break
    #     pygame.display.flip()
    # pygame.quit()
    # c=Camera(VectorN(0.0,0.0,-20.0),VectorN(0.0,0.0,0.0),VectorN(0.0,1.0,0.0),45.0,3.2,pygame.Surface((700,150)))
    # c.print()
    # print("Pixel(0,0)=",c.get_pixel_pos(0,0))
    # print("Pixel(699,149)=",c.get_pixel_pos(699,149))
    # print("Pixel(350,75)=",c.get_pixel_pos(350,75))
    # print("Pixel(113,23)=",c.get_pixel_pos(113,23))
    # print("Pixel(623,83)=",c.get_pixel_pos(623,83),"\n\n")
    # c=Camera(VectorN(5.0,7.0,-20.0),VectorN(2.0,5.0,3.0),VectorN(0.09950371902099892, 0.9950371902099892, 0.0),60.0,1.5,pygame.Surface((800,600)))
    # c.print()
    # print("Pixel(0,0)=",c.get_pixel_pos(0,0))
    # print("Pixel(799,599)=",c.get_pixel_pos(799,599))
    # print("Pixel(400,300)=",c.get_pixel_pos(400,300))
    # print("Pixel(113,542)=",c.get_pixel_pos(113,542))
    # print("Pixel(723,11)=",c.get_pixel_pos(723,11),"\n\n")                    