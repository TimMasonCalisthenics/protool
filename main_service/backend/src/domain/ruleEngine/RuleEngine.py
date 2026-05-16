from flask import current_app

from domain.ruleEngine.MitutoyoRule.MitutoyoRule import MitutoyoRule
from domain.ruleEngine.AirGaugeRule.AirGaugeRule import AirGaugeRule
from enumCore.common import CommonEnum
class RuleEngine:
    def __init__(self):
        self.tolerance = 0.001

        self.mitutoyo_rule = MitutoyoRule(self)
        self.air_gauge_rule = AirGaugeRule(self)
    def _analyze_stable_average(self, spec, values):
        current_app.logger.info(f"Values: {values}")
        current_app.logger.info(f"Required count: {spec.required_count}")
        if len(values) < spec.required_count:
            return None

        window = values[-spec.required_count:]
        if max(window) - min(window) > self.tolerance:
            return None

        avg_value = sum(window) / len(window)
        is_pass = spec.min_value <= avg_value <= spec.max_value

        return {
            "value": avg_value,
            "is_pass": is_pass
        }
    def evaluate_xy(self, spec, values):
        if len(values) < spec.required_count:
            return {
                "status": "partial", 
                "current_count": len(values),
                "last_value": values[-1] if values else None
            }

            avg_value = sum(values) / len(values)
            is_pass = spec.min_value <= avg_value <= spec.max_value

            return {
                "value": avg_value,
                "is_pass": is_pass,
                "captured_data": values # [X_value, Y_value]
            }
    def evaluate(self, spec, values , context=None):
        current_app.logger.info(f"Spec: {spec}")
        current_app.logger.info(f"Values: {values}")
        if spec.is_pass != None:
            return None
        if spec.sensor_type == CommonEnum.Airguage.value or spec.sensor_type == CommonEnum.Airguage_X_axis.value or spec.sensor_type == CommonEnum.Airguage_Y_axis.value:
            return self.air_gauge_rule.evaluate(spec, values, context or {})
        if spec.sensor_type == CommonEnum.Mitutoyo.value:
            return self.mitutoyo_rule.evaluate(spec, values, context or {})

        return None
    