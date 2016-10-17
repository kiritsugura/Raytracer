import pygame
import math3d      # You'll need your math3d file to run this...
import objects3d   # You'll need your math3d file to run this...

#Ask question about inside circle.

def drawShape(surf, s):
    # You might *not* want to comment anything here -- these are the attributes / class names I'd like
    # you to use in this lab.
    pygameColor = None
    if hasattr(s, "color"):
        pygameColor =s.get_material().ambient
    if isinstance(s, objects3d.Ray):
        pygame.draw.circle(surf, (255,255,255), s.origin.int()[0:2], 4)
        pygame.draw.line(surf, (255,255,255), s.origin.int()[0:2], s.getPT(2000).int()[0:2])
    elif isinstance(s, objects3d.Sphere):
        pygame.draw.circle(surf, s.color.ambient*255, s.mCenter.int()[0:2], s.mRadius, 2)
    elif isinstance(s, objects3d.Plane):
        # This is an interesting one.  We first have to determine if this plane is more horizontal (the normal
        # will be more closely-aligned with an up vector) than vice-versa.  Note: the normal is perpendicular to the
        # plane.  So to test for vertical-ish-ness, you actually look for a horizontal normal.  Then, solve the plane
        # equation for the points on the sides (for horizontal planes) or top / bottom
        # (for vertical planes) of the screen.
        vertAlign = abs(math3d.VectorN(1, 0, 0).dot(s.mNormal))
        horzAlign = abs(math3d.VectorN(0, 1, 0).dot(s.mNormal))
        if vertAlign > horzAlign:
            h = surf.get_height() - 1
            pt1 = math3d.VectorN((s.mDistance - s.mNormal[1]) / s.mNormal[0], 0)
            pt2 = math3d.VectorN((s.mDistance - h * s.mNormal[1]) / s.mNormal[0], h)
        else:
            w = surf.get_width() - 1
            pt1 = math3d.VectorN(0, (s.mDistance - s.mNormal[0]) / s.mNormal[1])
            pt2 = math3d.VectorN(w, (s.mDistance - w * s.mNormal[0]) / s.mNormal[1])
        pygame.draw.line(surf, s.colors.ambient*255, pt1.int(), pt2.int(), 2)
        # Draw the normal vector
        midPt = (pt1 + pt2) * 0.5
        normal2D = math3d.VectorN(s.mNormal[0], s.mNormal[1])
        pygame.draw.line(surf, s.colors.ambient, midPt.int(), (midPt + 10 * normal2D))
    elif isinstance(s, objects3d.AABB):
        pygame.draw.rect(surf, s.color.ambient*255, (s.mMinPoint[0], s.mMinPoint[1], \
                                          s.mMaxPoint[0] - s.mMinPoint[0], s.mMaxPoint[1] - s.mMinPoint[1]), 2)
    elif isinstance(s, objects3d.Polymesh):
        for i in range(len(s.triangles)):
            v1 = s.verticies[int(s.triangles[i][0])].int()[0:2]
            v2 = s.verticies[int(s.triangles[i][1])].int()[0:2]
            v3 = s.verticies[int(s.triangles[i][2])].int()[0:2]
            pygame.draw.polygon(surf, s.get_material().ambient, (v1, v2, v3), 1)
            # print(s.triangles[i][0],s.triangles[i][1],s.triangles[i][2])
        pygame.draw.rect(surf, (255 * (s.mColor.ambient * 0.25)).int(), (s.mAABB.mMinPoint[0], s.mAABB.mMinPoint[1], \
                                          s.mAABB.mMaxPoint[0] - s.mAABB.mMinPoint[0], s.mAABB.mMaxPoint[1] - s.mAABB.mMinPoint[1]),2)


from objects3d import *
# Pygame setup
pygame.display.init()
pygame.font.init()
screen = pygame.display.set_mode((800, 600))
font = pygame.font.SysFont("Courier New", 15)
done = False

# "Scene" setup -- feel free to modify this and / or comment out sections as you test.
allShapes = []
mainRay = objects3d.Ray(math3d.VectorN(400, 300, 0), math3d.VectorN(1, 0, 0))
sphere=Material(VectorN(0.3,0,0),VectorN(1,0,0),VectorN(1,1,1),10.0)
plane1=Material(VectorN(0,0.5,0),VectorN(0,1,0),VectorN(1,0,0),2.0)
plane2=Material(VectorN(0,0,0.1),VectorN(0,0,1),VectorN(1,0,1),6.0)
aabb=Material(VectorN(0.5,0.3,0.1),VectorN(1,1,0),VectorN(0.5,1.0,0.5),30.0)
# mesh=Material(VectorN(0.2,0,0.4),VectorN(0.7,0,1),VectorN(1,1,1),50.0)
allShapes.append(mainRay)
allShapes.append(objects3d.Sphere(math3d.VectorN(200, 200, 0), 50, sphere))
allShapes.append(objects3d.Plane(math3d.VectorN(0,1,0), 10, plane1))
allShapes.append(objects3d.Plane(math3d.VectorN(20,1,0), 60, plane2))
allShapes.append(objects3d.Plane(math3d.VectorN(-2, -7, 0), -600, plane1))
allShapes.append(objects3d.AABB(math3d.VectorN(500,450,0), math3d.VectorN(660,420,0), aabb))
# allShapes.append(objects3d.Polymesh("monkey.obj", math3d.VectorN(500,100,0), 2.0, math3d.VectorN(1.0,0.3,0.8)))
# allShapes.append(objects3d.Polymesh("sword.obj", math3d.VectorN(150,350,0), 10.0, math3d.VectorN(0.5,0.5,1.0)))

# Main Loop
while not done:
    ##############################
    # UPDATES                    #
    ##############################
    # ... for everything but Ray's, call the rayIntersection method of each shape and collect any hit-points
    hitPoints = []
    hitColors = []
    for s in allShapes:
        if hasattr(s, "rayIntersection"):
            t = s.rayIntersection(mainRay)
            if t != None:
                hitPoints.append(mainRay.getPT(t))
                hitColors.append(s.get_material().ambient)


    ##############################
    # INPUT-HANDLING             #
    ##############################
    event = pygame.event.poll()
    if event.type == pygame.QUIT:
        done = True
    elif event.type == pygame.KEYDOWN:
        if event.key == pygame.K_ESCAPE:
            done = True
    # ... device-polling
    mx, my = pygame.mouse.get_pos()
    mouseButtons = pygame.mouse.get_pressed()
    if mouseButtons[2]:
        # Right-clicking.  Update the ray direction.
        mousePos = math3d.VectorN(mx, my, 0)
        mouseDir = mousePos - mainRay.origin
        if not mouseDir.isZero():
            mainRay.direction = mouseDir.normalized()
    elif mouseButtons[0]:
        # Left-clicking.  Update the ray origin
        mainRay.origin = math3d.VectorN(mx, my, 0)


    ##############################
    # DRAWING                    #
    ##############################
    screen.fill((0,0,0))
    # ... draw all the shapes using the helper function above
    for curShape in allShapes:
        drawShape(screen, curShape)
    # ... draw any intersection points
    for i in range(len(hitPoints)):
        # Occasionally, we could get a point that's *really* far away (probably from the plane) -- this could give
        # you a "OverflowError".  Just ignore it (the point's off-screen anyhow)
        try:
            hitPt = hitPoints[i].int()[0:2]
            print(hitColors[i])
            pygame.draw.circle(screen, (hitColors[i]*255).int(), hitPt, 5)
            pygame.draw.circle(screen, (255,0,0), hitPt, 5, 2)
        except OverflowError:
            pass
    screen.blit(font.render("Left click to set ray origin, Right-click to set ray direction", False, (128,128,128)), (0,580))
    pygame.display.flip()

pygame.font.quit()
pygame.display.quit()