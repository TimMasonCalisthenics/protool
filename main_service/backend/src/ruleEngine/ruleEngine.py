from flask import current_app
import math
# unused
class RuleEngine:
    def __init__(self , MeasurementDraftSpec_repo , MeasurementRawValue_repo , setting_repo ):
        self.MeasurementDraftSpec_repo = MeasurementDraftSpec_repo
        self.MeasurementRawValue_repo = MeasurementRawValue_repo
        self.setting_repo = setting_repo
    def process(self, measurement , draft_spec):
        raw_values = self.MeasurementRawValue_repo.get_by_measurement_and_point(measurement.id , draft_spec.spec_point_id , draft_spec.required_count)
        ##mitutoyo
        if draft_spec.sensor_type == "mitutoyo":
            result_check = False
            raw_values_list = [raw_value.raw_value for raw_value in raw_values]
            if len(raw_values) == draft_spec.required_count:
                if len(set(raw_values_list)) == 1:                    
                    if draft_spec.min_value <= raw_values[0].raw_value <= draft_spec.max_value  :
                        result_check = True
                self.MeasurementDraftSpec_repo.update_result(draft_spec.id , raw_values[0].raw_value , result_check)
        ##air gauge
        elif draft_spec.sensor_type == "air_gauge":
            current_app.logger.info(f"Processing air gauge for spec {draft_spec.id}")
            if draft_spec.status == "pending":
                if draft_spec.rule_type == "less than":
                    if raw_values[0].raw_value < draft_spec.nominal_value:                        
                        self.MeasurementDraftSpec_repo.update_status(draft_spec.id , "ready")
                elif draft_spec.rule_type == "more than":
                    if raw_values[0].raw_value > draft_spec.nominal_value:                        
                        self.MeasurementDraftSpec_repo.update_status(draft_spec.id , "ready")
                else: #normal 
                    self.MeasurementDraftSpec_repo.update_status(draft_spec.id , "ready")
                    current_app.logger.info(f"Updated status for spec {draft_spec.id} to ready")
            else: #status ready
                result_check = False
                raw_values_list = [raw_value.raw_value for raw_value in raw_values]
                if len(raw_values) == draft_spec.required_count :
                    if len(set(raw_values_list)) == 1:                                                
                        if draft_spec.min_value <= raw_values[0].raw_value <= draft_spec.max_value:
                            result_check = True
                    self.MeasurementDraftSpec_repo.update_result(draft_spec.id , raw_values[0].raw_value , result_check)

        ##commit all changes
        self.MeasurementDraftSpec_repo.commit()

    def clear_tmp(self):
        self.MeasurementRawValue_repo.clear_tmp()


