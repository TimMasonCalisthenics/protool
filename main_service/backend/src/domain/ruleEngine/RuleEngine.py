from flask import current_app

from domain.ruleEngine.MitutoyoRule.MitutoyoRule import MitutoyoRule
from domain.ruleEngine.AirGaugeRule.AirGaugeRule import AirGaugeRule

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
    # def _check_trigger(self, value, spec):
    #     if spec.rule_type == "less than":
    #         return value < spec.nominal_value
    #     elif spec.rule_type == "more than":
    #         return value > spec.nominal_value
    #     return True
        
    # def evaluate(self, spec, values ):        

    #     if spec.sensor_type == "air_gauge" and spec.status == "pending":
    #         if not values:
    #             return None
    #         latest = values[-1]
    #         if self._check_trigger(latest, spec):
    #             return {
    #                 "action": "update_status",
    #                 "status": "ready"
    #             }

    #         return None

    #     if len(values) < spec.required_count:
    #         return None

    #     window = values[-spec.required_count:]
    #     if max(window) - min(window) > self.tolerance:
    #         return None

    #     avg_value = sum(window) / len(window)
    #     is_pass = spec.min_value <= avg_value <= spec.max_value

    #     return {
    #         "value": avg_value,
    #         "is_pass": is_pass
    #     }
    # def evaluate(self, spec, values , context=None):        
    #     context = context or {}
    #     if spec.sensor_type == "air_gauge" and spec.status == "pending":
    #         if not values:
    #             return None
    #         latest = values[-1]
    #         current_app.logger.info(f"Latest: {latest}")
    #         current_app.logger.info(f"is_active: {context.get('is_active')}")
    #         if context.get("has_active") == True:
    #             if context.get("is_active") == True:
    #                 if self._check_trigger(latest, spec):
    #                     return {
    #                         "action": "broadcast_ready"
    #                     }
    #         else:
    #             if self._check_trigger(latest, spec):
    #                 return {
    #                     "action": "update_status",
    #                     "status": "ready"
    #                 }
    #         return None

    #     if len(values) < spec.required_count:
    #         return None

    #     window = values[-spec.required_count:]
    #     if max(window) - min(window) > self.tolerance:
    #         return None

    #     avg_value = sum(window) / len(window)
    #     is_pass = spec.min_value <= avg_value <= spec.max_value

    #     return {
    #         "value": avg_value,
    #         "is_pass": is_pass
    #     }
    def evaluate(self, spec, values , context=None):
        if spec.sensor_type == "air_gauge":
            return self.air_gauge_rule.evaluate(spec, values, context or {})
        if spec.sensor_type == "mitutoyo":
            return self.mitutoyo_rule.evaluate(spec, values, context or {})

        return None
    