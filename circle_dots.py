from manimlib.imports import *
import uuid

class EvenlySpacedDots(VMobject):
    CONFIG = {
        "circle_color": BLUE,
        "circle_radius": 3,
        "num_points": 6,
        "ignored_indices": [],
    }

    def __init__(self, **kwargs):
        VMobject.__init__(self, **kwargs)

        self.circle = Circle(
            color=self.circle_color,
            radius=self.circle_radius,
        )

        self.dots = VGroup(*[
            Dot(point) for point in self.get_points()
        ])

        self.dot_arrows = VGroup(*[
            Arrow(*[
                interpolate(self.circle.get_center(), dot.get_center(), a)
                for a in (0.6, 0.9)
            ], buff=0)
            for dot in self.dots
        ])

    def get_points(self):
        return np.array([
            self.get_circle_point_at_proportion(fdiv(i, self.num_points))
            for i in range(self.num_points)
            if i not in self.ignored_indices
        ])

    def get_circle_point_at_proportion(self, alpha):
        radius = self.circle.get_width() / 2.0
        center = self.circle.get_center()
        angle = alpha * TAU
        unit_circle_point = np.cos(angle) * RIGHT + np.sin(angle) * UP
        return radius * unit_circle_point + center

    def get_fractional_arc(self, fraction, start_fraction=0):
        arc = Arc(
            angle=fraction * TAU,
            start_angle=start_fraction * TAU,
            radius=self.get_radius(),
        )
        arc.shift(self.circle.get_center())
        return arc


class DotsAroundCircle(Scene):
    CONFIG = {
        "circle_color": BLUE,
        "circle_radius": 3,
        "num_points": 6,
        "ignored_indices": [],
    } 
    def construct(self):
        circleDots = EvenlySpacedDots()


        beholdLabel = TextMobject("BEHOLD MY \\\\ EVENLY-SPACED \
                                                \\\\ DOTS, MORTAL")
        trembleLabel = TextMobject("TREMBLE \\\\ AND DISPAIR")
        beholdLabel.set_width(0.5 * circleDots.circle.get_width())
        beholdLabel.move_to(circleDots.circle)

        self.play(ShowCreation(circleDots.circle))
        self.play(
            LaggedStartMap(ShowCreation, circleDots.dots),
            LaggedStartMap(GrowArrow, circleDots.dot_arrows),
            Write(beholdLabel)
        )
        self.wait()
        self.play(Transform(beholdLabel, trembleLabel))
        self.wait(2)

