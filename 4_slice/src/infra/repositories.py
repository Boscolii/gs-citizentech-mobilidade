from src.domain.points import Point, PointStatus


class InMemoryPointRepository:
    def __init__(self):
        self.points = [
            Point("P001", "Terminal Central", "Av. Central, 100", PointStatus.AVAILABLE, ["101", "205"]),
            Point("P002", "Praça das Flores", "Rua das Flores, 45", PointStatus.MAINTENANCE, ["101"], "P001"),
        ]

    def get(self, point_id):
        return next((point for point in self.points if point.id == point_id), None)

    def list(self, limit, offset):
        return self.points[offset:offset + limit], len(self.points)
