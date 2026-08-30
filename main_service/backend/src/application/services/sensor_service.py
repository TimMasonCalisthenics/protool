from enumCore.common import CommonEnum
from flask import current_app
from collections import defaultdict
from domain.exceptions.base import AppError
from infrastructure.persistence.models.MeasurementRawValue import MeasurementRawValue
class SensorService:
    def __init__(self, sensor_repo, measurement_raw_value_repo, measurement_draft_spec_repo, setting_repo, rule_engine):
        self.sensor_repo = sensor_repo
        self.raw_repo = measurement_raw_value_repo
        self.spec_repo = measurement_draft_spec_repo
        self.setting_repo = setting_repo
        self.rule_engine = rule_engine
    
    
    def ingest_sensor_data(self, data):
        settings = self.setting_repo.get_detail_setting()
        measurement_id = settings.active_draft_id
        if not measurement_id:
            raise AppError("No active draft")
        

        specs_to_process = []

        specs = self.spec_repo.get_by_device_id(
            data.device_id
        )

        spec_map = {s.value_key: s for s in specs}
        specs_to_process = set()

        raw_list = []
        for item in data.measurements:
            spec = spec_map.get(item.key_value)
            if not spec: continue
            
            # ดึงค่าเดิมและ append ค่าใหม่
            current_values = list(spec.captured_values) if spec.captured_values else []
            current_values.append(item.value)
            
            spec.captured_values = current_values
            spec.current_count = len(current_values)

            raw_list.append(
                MeasurementRawValue(
                    measurement_id=measurement_id,
                    spec_point_id=spec.spec_point_id,
                    sensor_device_id=data.device_id,
                    raw_value=item.value
                )
            )

            # ✅ แก้ไข: ลบ context และอนุญาตให้ส่งผ่านไป process ด้านล่างได้เลย
            if spec.current_count >= spec.required_count:
                specs_to_process.add(spec)

        if not specs_to_process:
            return 0
            
        self.raw_repo.create_list(raw_list)

        # raws_data = self.raw_repo.get_by_measurement_and_device(
        #     measurement_id,
        #     data.device_id,            
        # )

        max_required = max(s.required_count for s in specs_to_process)

        raws_data = self.raw_repo.get_latest_grouped(
            measurement_id,
            data.device_id,
            max_required
        )

        raw_map = {}
        for r in raws_data:
            raw_map.setdefault(r.spec_point_id, []).append(r.raw_value)

        # group spec by sensor type
        specs_by_type = {}
        for s in specs_to_process:
            specs_by_type.setdefault(s.sensor_type, []).append(s)
        # process mitutoyo
        for spec in specs_by_type.get(CommonEnum.Mitutoyo.value, []):
            values = raw_map.get(spec.spec_point_id, [])

            result = self.rule_engine.evaluate(spec, values)

            if not result:
                continue

            self.spec_repo.update_result(
                spec.id,
                result["value"],
                result["is_pass"]
            )

            if result["is_pass"]:
                self.raw_repo.clear_by_point(
                    measurement_id,
                    spec.spec_point_id
                )

        
        grouped = defaultdict(list)
        for s in specs_by_type.get("air_gauge", []):
            grouped[s.group_id].append(s)

        for group_id, specs in grouped.items():

            # -------- find active --------
            active_specs = [s for s in specs if getattr(s, "active_value", False)]

            #if len(active_specs) > 1:
            #    raise AppError(f"Multiple active spec in group {group_id}")

            active_spec = active_specs[0] if active_specs else None

            # -------- process each spec --------
            for spec in specs:
                values = raw_map.get(spec.spec_point_id, [])

                context = {
                    "has_active": active_spec is not None,
                    "is_active": active_spec and spec.id == active_spec.id
                }

                result = self.rule_engine.evaluate(
                    spec,
                    values,
                    context=context
                )

                if not result:
                    continue

                # -------- handle action --------
                if result.get("action") == "broadcast_ready":
                    current_app.logger.info(f"[Group {group_id}] broadcast READY")

                    for s in specs:
                        self.spec_repo.update_status(s.id, "ready")

                    break  # 🔥 สำคัญ: stop group หลัง broadcast

                if result.get("action") == "update_status":
                    self.spec_repo.update_status(spec.id, result["status"])
                    continue 
                if "value" in result:
                    self.spec_repo.update_result(
                        spec.id,
                        result["value"],
                        result["is_pass"]
                    )

                    if result["is_pass"]:
                        self.raw_repo.clear_by_point(
                            measurement_id,
                            spec.spec_point_id
                        )
      
        self.sensor_repo.commit()

        return len(specs_to_process)
    
    def clear_tmp(self):
        self.raw_repo.clear_tmp()
