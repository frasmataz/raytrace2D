import pygame
import numpy

successes, failures = pygame.init()
print("{0} successes and {1} failures".format(successes, failures))

FPS = 60

class Game:
    screenWidth = 1280
    screenHeight = 720
    screen = pygame.display.set_mode((screenWidth, screenHeight))
    clock = pygame.time.Clock()

    fov = numpy.pi/4
    rays = 30

    playerPosition = (50.0, 50.0)
    playerMoveSpeed = 10.0
    playerVelocity = (0.0, 0.0)

    mousePosition = (0,0)
    surfaces = [
        # Window edges
        ((0,0), (screenWidth,0)),
        ((0,0), (0,screenHeight)),
        ((screenWidth,0), (screenWidth,screenHeight)),
        ((0,screenHeight), (screenWidth,screenHeight)),

        # Box
        ((500,200), (700,200)),
        ((500,200), (500,400)),
        ((700,200), (700,400)),
        ((500,400), (700,400))
    ]

    def handleEvents(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_w:
                    self.playerVelocity = (self.playerVelocity[0], -self.playerMoveSpeed)
                if event.key == pygame.K_s:
                    self.playerVelocity = (self.playerVelocity[0], self.playerMoveSpeed)
                if event.key == pygame.K_a:
                    self.playerVelocity = (-self.playerMoveSpeed, self.playerVelocity[1])
                if event.key == pygame.K_d:
                    self.playerVelocity = (self.playerMoveSpeed, self.playerVelocity[1])

            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_w or event.key == pygame.K_s:
                    self.playerVelocity = (self.playerVelocity[0], 0.0)
                if event.key == pygame.K_a or event.key == pygame.K_d:
                    self.playerVelocity = (0.0, self.playerVelocity[1])

    def update(self):
        self.playerPosition = tuple(numpy.add(self.playerPosition, self.playerVelocity))
        self.mousePosition = pygame.mouse.get_pos()

    def line_intersection(line1, line2):
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

    def castRay(self, pos, angle):
        rayLength = 10000  # Arbitrary ray length
        endPos = (
            (numpy.cos(angle) * rayLength) + pos[0],
            (numpy.sin(angle) * rayLength) + pos[1]
        )

        pygame.draw.line(
            self.screen,
            pygame.Color(255,0,0),
            (int(self.playerPosition[0]), int(self.playerPosition[1])),
            (int(endPos[0]), int(endPos[1])),
            2
        )

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
        angleToMouse = self.getRayAngle(self.playerPosition, self.mousePosition)
        zeroRayAngle = angleToMouse - (self.fov/2)
        for rayIndex in range(self.rays):
            angle = zeroRayAngle + (rayIndex * (self.fov/self.rays))
            ray = self.castRay(self.playerPosition, angle)

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