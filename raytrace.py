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
    rays = 600

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

    # Given three colinear points p, q, r, the function checks if
    # point q lies on line segment 'pr'
    def onSegment(self, p, q, r):
        if ((q[0] <= max(p[0], r[0])) and (q[0] >= min(p[0], r[0])) and
                (q[1] <= max(p[1], r[1])) and (q[1] >= min(p[1], r[1]))):
            return True
        return False

    def orientation(self, p, q, r):
        # to find the orientation of an ordered triplet (p,q,r)
        # function returns the following values:
        # 0 : Colinear points
        # 1 : Clockwise points
        # 2 : Counterclockwise

        # See https://www.geeksforgeeks.org/orientation-3-ordered-points/amp/
        # for details of below formula.

        val = (float(q[1] - p[1]) * (r[0] - q[0])) - \
            (float(q[0] - p[0]) * (r[1] - q[1]))
        if (val > 0):

            # Clockwise orientation
            return 1
        elif (val < 0):

            # Counterclockwise orientation
            return 2
        else:

            # Colinear orientation
            return 0

    # The main function that returns true if
    # the line segment 'p1q1' and 'p2q2' intersect.
    def doIntersect(self, p1, q1, p2, q2):

        # Find the 4 orientations required for
        # the general and special cases
        o1 = self.orientation(p1, q1, p2)
        o2 = self.orientation(p1, q1, q2)
        o3 = self.orientation(p2, q2, p1)
        o4 = self.orientation(p2, q2, q1)

        # General case
        if ((o1 != o2) and (o3 != o4)):
            return True

        # Special Cases

        # p1 , q1 and p2 are colinear and p2 lies on segment p1q1
        if ((o1 == 0) and self.onSegment(p1, p2, q1)):
            return True

        # p1 , q1 and q2 are colinear and q2 lies on segment p1q1
        if ((o2 == 0) and self.onSegment(p1, q2, q1)):
            return True

        # p2 , q2 and p1 are colinear and p1 lies on segment p2q2
        if ((o3 == 0) and self.onSegment(p2, p1, q2)):
            return True

        # p2 , q2 and q1 are colinear and q1 lies on segment p2q2
        if ((o4 == 0) and self.onSegment(p2, q1, q2)):
            return True

        # If none of the cases
        return False

    def getIntersectPoint(self, line1, line2):
        xdiff = (line1[0][0] - line1[1][0], line2[0][0] - line2[1][0])
        ydiff = (line1[0][1] - line1[1][1], line2[0][1] - line2[1][1])

        def det(a, b):
            return a[0] * b[1] - a[1] * b[0]

        div = det(xdiff, ydiff)
        if div == 0:
            return None

        d = (det(*line1), det(*line2))
        x = det(d, xdiff) / div
        y = det(d, ydiff) / div
        return x, y

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
            if self.doIntersect(self.playerPosition, endPos, surface[0], surface[1]):
                intersectPos = self.getIntersectPoint(
                    (self.playerPosition, endPos), surface)
            else:
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

    def drawRays(self):
        angleToMouse = self.getRayAngle(
            self.playerPosition, self.mousePosition)
        zeroRayAngle = angleToMouse - (self.fov/2)
        for rayIndex in range(self.rays):
            angle = zeroRayAngle + (rayIndex * (self.fov/self.rays))
            ray = self.castRay(self.playerPosition, angle)

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

    def draw(self):
        self.screen.fill(pygame.Color(20, 20, 30))
        self.drawSurfaces()
        self.drawPlayer()
        self.drawRays()
        pygame.display.flip()

    def run(self):
        while True:
            self.clock.tick(FPS)
            self.handleEvents()
            self.update()
            self.draw()


game = Game()
game.run()
