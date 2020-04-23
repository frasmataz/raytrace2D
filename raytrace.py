import pygame
import numpy

successes, failures = pygame.init()
print("{0} successes and {1} failures".format(successes, failures))

FPS = 60

class Game:
    screen = pygame.display.set_mode((1280, 720))
    clock = pygame.time.Clock()

    playerPosition = (50.0, 50.0)
    playerMoveSpeed = 10.0
    playerVelocity = (0.0, 0.0)

    mousePosition = (0,0)

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

    def draw(self):
        self.screen.fill(pygame.Color(20, 20, 30))
        self.drawPlayer()
        pygame.display.flip()

    def run(self):
        while True:
            self.clock.tick(FPS)
            self.handleEvents()
            self.update()
            self.draw()

game = Game()
game.run()