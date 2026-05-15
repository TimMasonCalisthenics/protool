class MeasurementModel:
    def __init__(self, config):
        self.x0 = config.get('x0', 0)
        self.y0 = config.get('y0', 0)
        self.x1 = config.get('x1', 0)
        self.y1 = config.get('y1', 0)

    def calculate_y(self, raw_x):
        try:
            # สูตร Linear Interpolation
            slope = (self.y1 - self.y0) / (self.x1 - self.x0)
            return self.y0 + (raw_x - self.x0) * slope
        except ZeroDivisionError:
            return raw_x # ป้องกันกรณี x0 กับ x1 เท่ากัน