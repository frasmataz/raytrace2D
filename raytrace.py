import pygame
import numpy

successes, failures = pygame.init()
print("{0} successes and {1} failures".format(successes, failures))

FPS = 90


class Game:
    screenWidth = 1280
    screenHeight = 720
    screen = pygame.display.set_mode((screenWidth, screenHeight))
    clock = pygame.time.Clock()

    fov = numpy.pi/2
    numberOfRays = 180

    playerPosition = (50.0, 50.0)
    playerMoveSpeed = 10.0
    playerVelocity = (0.0, 0.0)

    mousePosition = (0, 0)
    surfaces = [
        # Window edges
        ((0, 0), (screenWidth, 0)),
        ((0, 0), (0, screenHeight)),
        ((screenWidth, 0), (screenWidth, screenHeight)),
        ((0, screenHeight), (screenWidth, screenHeight)),

        # Box
        ((500, 200), (700, 200)),
        ((500, 200), (500, 400)),
        ((700, 200), (700, 400)),
        ((500, 400), (700, 400))
    ]

    def handleEvents(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_w:
                    self.playerVelocity = (
                        self.playerVelocity[0], -self.playerMoveSpeed)
                if event.key == pygame.K_s:
                    self.playerVelocity = (
                        self.playerVelocity[0], self.playerMoveSpeed)
                if event.key == pygame.K_a:
                    self.playerVelocity = (-self.playerMoveSpeed,
                                           self.playerVelocity[1])
                if event.key == pygame.K_d:
                    self.playerVelocity = (
                        self.playerMoveSpeed, self.playerVelocity[1])

            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_w or event.key == pygame.K_s:
                    self.playerVelocity = (self.playerVelocity[0], 0.0)
                if event.key == pygame.K_a or event.key == pygame.K_d:
                    self.playerVelocity = (0.0, self.playerVelocity[1])

    def update(self):
        self.playerPosition = tuple(
            numpy.add(self.playerPosition, self.playerVelocity))
        self.mousePosition = pygame.mouse.get_pos()

    def onSegment(self, p, q, r):
        if ((q[0] <= max(p[0], r[0])) and (q[0] >= min(p[0], r[0])) and
                (q[1] <= max(p[1], r[1])) and (q[1] >= min(p[1], r[1]))):
            return True
        return False

    def orientation(self, p, q, r):
        val = (float(q[1] - p[1]) * (r[0] - q[0])) - \
            (float(q[0] - p[0]) * (r[1] - q[1]))
        if (val > 0):
            return 1
        elif (val < 0):
            return 2
        else:
            return 0

    def getIntersectPoint(self, p1, q1, p2, q2):
        o1 = self.orientation(p1, q1, p2)
        o2 = self.orientation(p1, q1, q2)
        o3 = self.orientation(p2, q2, p1)
        o4 = self.orientation(p2, q2, q1)

        if (((o1 != o2) and (o3 != o4))
        or ((o1 == 0) and self.onSegment(p1, p2, q1))
        or ((o2 == 0) and self.onSegment(p1, q2, q1))
        or ((o3 == 0) and self.onSegment(p2, p1, q2))
        or ((o4 == 0) and self.onSegment(p2, q1, q2))):
            xdiff = (p1[0] - q1[0], p2[0] - q2[0])
            ydiff = (p1[1] - q1[1], p2[1] - q2[1])

            def det(a, b):
                return a[0] * b[1] - a[1] * b[0]

            div = det(xdiff, ydiff)
            if div == 0:
                return None

            d = (det(*(p1, q1))), det(*(p2, q2))
            x = det(d, xdiff) / div
            y = det(d, ydiff) / div
            return x, y

        return None

    def lineLength(self, p1, p2):
        return numpy.sqrt(numpy.square(p1[0] - p2[0]) + numpy.square(p1[1] - p2[1]))

    def castRay(self, pos, angle):
        rayLength = 10000  # Arbitrary ray length
        endPos = (
            (numpy.cos(angle) * rayLength) + pos[0],
            (numpy.sin(angle) * rayLength) + pos[1]
        )

        minLength = 10000
        minIntersectPos = (0, 0)

        for surface in self.surfaces:
            intersectPos = self.getIntersectPoint( self.playerPosition, endPos, surface[0], surface[1] )

            if intersectPos == None:
                continue

            length = self.lineLength(self.playerPosition, intersectPos)
            if length < minLength:
                minLength = length
                minIntersectPos = intersectPos

        return {
            'pos': minIntersectPos,
            'length': minLength
        }

    def getRayAngle(self, p1, p2):
        return numpy.arctan2(
            p2[1] - p1[1],
            p2[0] - p1[0]
        )

    def drawSurfaces(self):
        surfaceColor = pygame.Color(180, 120, 120)

        # Draw surfaces
        for surface in self.surfaces:
            pygame.draw.line(
                self.screen,
                surfaceColor,
                surface[0],
                surface[1],
                10
            )

    def drawPlayer(self):
        playerRadius = 8
        playerColor = pygame.Color(120, 180, 180)

        # Draw player
        pygame.draw.circle(
            self.screen,
            playerColor,
            (int(self.playerPosition[0]), int(self.playerPosition[1])),
            playerRadius
        )

        # Draw sightline
        pygame.draw.line(
            self.screen,
            playerColor,
            (int(self.playerPosition[0]), int(self.playerPosition[1])),
            self.mousePosition,
            2
        )

    def computeRays(self):
        angleToMouse = self.getRayAngle(
            self.playerPosition, self.mousePosition)

        zeroRayAngle = angleToMouse - (self.fov/2)

        rays = []
        for rayIndex in range(self.numberOfRays):
            angle = zeroRayAngle + (rayIndex * (self.fov/self.numberOfRays))
            rays.append(self.castRay(self.playerPosition, angle))

        return rays

    def drawRays(self, rays):
        for ray in rays:
            pygame.draw.line(
                self.screen,
                pygame.Color(
                    int(numpy.clip(
                        (1/numpy.square(ray['length']/self.screenWidth)),
                    0, 255)),
                0, 0),
                (int(self.playerPosition[0]), int(self.playerPosition[1])),
                ray['pos'],
                2
            )

    def drawMap(self, rays):
        self.drawSurfaces()
        self.drawPlayer()
        #self.drawRays(rays)
        pygame.display.flip()

    def drawFirstPerson(self, rays):
        rectWidth = int(self.screenWidth/self.numberOfRays)
        for slice in range(self.numberOfRays):
            ray = rays[slice]
            rectX = (rectWidth * slice) - rectWidth
            rectHeight = numpy.clip(1000 - ray['length'], 0, self.screenHeight)
            screenCentreline = self.screenHeight/2
            rect = pygame.Rect(
                rectX,
                screenCentreline - (rectHeight / 2),
                rectWidth,
                rectHeight
            )
            pygame.draw.rect(
                self.screen,
                pygame.Color(
                    int(numpy.clip(
                        (1/numpy.square(ray['length']/self.screenWidth))* 5,
                    0, 255)),
                0, 0),
                rect
            )

    def run(self):
        while True:
            self.clock.tick(FPS)
            self.handleEvents()
            self.update()
            rays = self.computeRays()

            self.screen.fill(pygame.Color(20, 20, 30))
            self.drawFirstPerson(rays)
            self.drawMap(rays)


game = Game()
game.run()
