"""The Lucide vocabulary: the only elements and attributes an icon may have (spec seguranca-doacoes, section 8)."""
from html.parser import HTMLParser

ELEMENTS = {"svg", "path", "circle", "rect", "line", "polyline", "polygon", "ellipse", "g"}
ATTRIBUTES = {"xmlns", "width", "height", "viewbox", "fill", "stroke", "stroke-width", "stroke-linecap", "stroke-linejoin", "class",
              "d", "cx", "cy", "r", "rx", "ry", "x", "y", "x1", "y1", "x2", "y2", "points"}


class _Walk(HTMLParser):
    def __init__(self):
        super().__init__()
        self.problems, self.depth, self.roots = [], 0, 0

    def handle_starttag(self, tag, attrs):
        if self.depth == 0:
            self.roots += 1
        if tag not in ELEMENTS:
            self.problems.append(f"element {tag}")
        self.problems += [f"attribute {k}" for k, _ in attrs if k not in ATTRIBUTES]
        self.depth += 1

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        self.depth -= 1

    def handle_endtag(self, tag):
        self.depth -= 1

    def handle_data(self, data):
        if data.strip():
            self.problems.append("text")


def problems(svg):
    w = _Walk()
    w.feed(svg.split("-->", 1)[-1] if svg.lstrip().startswith("<!--") else svg)
    if w.roots != 1:
        w.problems.append(f"{w.roots} root elements")
    return w.problems
