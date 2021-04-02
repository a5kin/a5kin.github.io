from browser import document, window
import math
import random
from dataclasses import dataclass

from scripts.python.colorpalettes import PALETTES

SEED = "UNN"

# random.seed(SEED)
MAIN_PALETTE = random.choice(PALETTES)
MAX_RECURSION_DEPTH = 5
MAX_AGE = 100
SPROUT_PROBABILITY = 0.07
GROW_SPEED = 10


def polar2vec(r, phi):
    """Calculate Cartesian vector from polar coords."""
    return r * math.cos(phi), -r * math.sin(phi)


def generate_rho(old_rho):
    """Generate new angular velocities by shuffling old ones."""
    return [
        old_rho[0] + random.choice([-1, 1]) * 0.1,
        (random.random() - 0.5) * 0.6,
        (random.random() - 0.5) * 0.06,
        (random.random() - 0.5) * 0.006,
    ]


class App:
    """Base class for application."""

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

        # list of in-app objects
        self.objects = []

    def draw(self, *args):
        """Redraw the whole app."""
        self.ctx.clear()
        for obj in self.objects[::-1]:
            obj.update()
            obj.draw()
        window.requestAnimationFrame(self.draw)


@dataclass
class BranchDNA:
    """Class for keeping a branch's DNA."""
    rho: list[float]     # angular velocity derivatives
    age: int = 0         # ticks passed from the whole tree's birth
    generation: int = 0  # recursion depth

    def evolve(self, dt):
        """Evolve a DNA."""
        for i in range(len(self.rho) - 1):
            self.rho[i] += self.rho[i + 1] * dt
        self.age += 1


class Branch:
    """Class representing a single branch."""

    def __init__(self, app, seed, x, y):
        """Initialize a branch with DNA (seed)."""
        self._app = app
        self._dna = seed
        self._start_rho = self._dna.rho[0]

        self.path = [(x, y)]
        self.normals = [polar2vec(1, self._dna.rho[0] - math.pi / 2)]

        # hardcoded stuff
        self.color = MAIN_PALETTE[self._dna.generation % len(MAIN_PALETTE)]
        self.grow_speed = GROW_SPEED

    def update(self):
        """Evolve a branch."""
        too_curly = abs(self._start_rho - self._dna.rho[0]) > math.pi * 2
        if too_curly:
            return

        # grow a branch
        too_old = self._dna.age > MAX_AGE
        if not too_old:
            cur_x, cur_y = self.path[-1]
            new_x, new_y = polar2vec(self.grow_speed, self._dna.rho[0])
            new_x += cur_x
            new_y += cur_y
            self.path.append((new_x, new_y))
            self.normals.append(polar2vec(1, self._dna.rho[0] - math.pi / 2))
            self._dna.evolve(0.2)  # TODO: frame time as argument

        # sprout a new branch
        sprout_prob = SPROUT_PROBABILITY  # TODO: age-dependent function?
        # TODO: probability based on time since last sprout
        # sprout_prob = SPROUT_PROBABILITY * (self._dna.age / MAX_AGE) * 2.3
        need_sprout = random.random() < sprout_prob
        too_branchy = self._dna.generation >= MAX_RECURSION_DEPTH - 1
        if not too_old and not too_branchy and need_sprout:
            new_seed = BranchDNA(
                generate_rho(self._dna.rho),
                self._dna.age,
                self._dna.generation + 1,
            )
            new_branch = Branch(self._app, new_seed, *self.path[-1])
            self._app.objects.append(new_branch)

    def draw(self):
        """Draw a branch on canvas."""
        path_l, path_r = [], []
        num_points = len(self.path)
        p = window.PIXI.Point.new
        for i, ((x, y), (nx, ny)) in enumerate(zip(self.path, self.normals)):
            thickness = math.sqrt(num_points - i)
            path_l.append(p(x + nx * thickness, y + ny * thickness))
            path_r.append(p(x - nx * thickness, y - ny * thickness))
        poly_path = path_l + path_r[::-1]

        self._app.ctx.beginFill(self.color)
        self._app.ctx.drawPolygon(poly_path)
        self._app.ctx.endFill()


class TreeApp(App):
    """Main app for tree page."""

    def __init__(self):
        """Initialize the app engine."""
        super().__init__()

        seed = BranchDNA(generate_rho([math.pi / 2, 0, 0, 0]))
        self.objects.append(Branch(self, seed, 0, window.innerHeight / 2))


main_app = TreeApp()
main_app.draw()
