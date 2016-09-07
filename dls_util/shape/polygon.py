from __future__ import division


class Polygon:
    def __init__(self, vertices):
        """ Initialize the polygon with a ordered list of its vertices. The list should contain Point objects.
        The final vertex will form an edge by joining to the first. """
        if len(vertices) < 3:
            raise ValueError("A polygon must have at least 3 vertices")

        self._vertices = vertices

    def vertices(self):
        return self._vertices[:]

    def num_vertices(self):
        """ The number of vertices"""
        return len(self._vertices)

    def offset(self, offset):
        """ Returns a new polygon which is the same as this by moved by the specified amount. """
        new_vertices = [v+offset for v in self._vertices]
        return Polygon(new_vertices)

    def scale(self, factor):
        """ Returns a new polygon which is the same as this one but rescaled. """
        new_vertices = [v.scale(factor) for v in self._vertices]
        return Polygon(new_vertices)

    def edges(self):
        """ Returns an ordered list of the edges which are pairs of vertices. """
        edges = []
        num = self.num_vertices()

        for v in range(num - 1):
            edges.append([self._vertices[v], self._vertices[v+1]])

        edges.append([self._vertices[num - 1], self._vertices[0]])
        return edges

    def area(self):
        """ Returns the area of the polygon. """
        raise NotImplementedError()

    def is_convex(self):
        """ Returns True if the polygon is convex. """
        raise NotImplementedError()

    def is_complex(self):
        """ Returns True if the polygon is complex. """
        raise NotImplementedError()

    @staticmethod
    def from_rectangle(rectangle):
        return Polygon(rectangle.corners())

