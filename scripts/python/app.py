from browser import document, window
import math
import random

from scripts.python.colorpalettes import PALETTES

NUM_CIRCLES = 50
SEED = "Andrey Zamaraev1"

# random.seed(SEED)


class ExcentricCircle:
    """Excentric circle sumulation"""

    def __init__(self, x_e, y_e, r_e, r_c, fi, dfi, color, opacity):
        self.x_e, self.y_e = x_e, y_e
        self.r_e = r_e
        self.fi, self.dfi = fi, dfi
        self.color = color
        self.opacity = opacity
        self.x, self.y, self.r = 0, 0, r_c
        self.update()

    def update(self):
        """Move and update circle position."""
        self.fi += self.dfi
        self.x = -self.r_e * math.sin(self.fi) + self.x_e
        self.y = self.r_e * math.cos(self.fi) + self.y_e


class DevApp:
    """Main app for dev page."""

    def __init__(self):
        """Initialize the app engine."""
        # setup Pixi
        self.app = window.PIXI.Application.new({"width": 256, "height": 256})
        document.body.appendChild(self.app.view)
        self.app.renderer.view.style.position = "absolute"
        self.app.renderer.view.style.display = "block"
        self.app.renderer.autoResize = True
        self.app.renderer.resize(window.innerWidth, window.innerHeight)

        # add graphics context for drawing
        self.ctx = window.PIXI.Graphics.new()
        self.ctx.x = window.innerWidth / 2
        self.ctx.y = window.innerHeight / 2
        self.app.stage.addChild(self.ctx)

        self.excentrics = []
        self.create_excentrics()

    def create_excentrics(self):
        """Create excentric circles for the stage."""
        palette = random.choice(PALETTES)
        for i in range(NUM_CIRCLES):
            x_e = random.randint(-50, 50)
            y_e = random.randint(-50, 50)
            r_e = 23 * (1 + random.random())
            r_c = (NUM_CIRCLES - i) / NUM_CIRCLES * 69 * (1 + random.random())
            fi = 2 * math.pi * random.random()
            dfi = (0.5 - random.random()) * math.pi / 50
            color = random.choice(palette)
            opacity = 0.5
            circle = ExcentricCircle(x_e, y_e, r_e, r_c,
                                     fi, dfi, color, opacity)
            self.excentrics.append(circle)

    def draw(self, *args):
        """Redraw the whole app."""
        self.ctx.clear()
        for circle in self.excentrics:
            self.ctx.beginFill(circle.color, circle.opacity)
            self.ctx.drawCircle(circle.x, circle.y, circle.r)
            self.ctx.endFill()
            circle.update()
        window.requestAnimationFrame(self.draw)


main_app = DevApp()
main_app.draw()
