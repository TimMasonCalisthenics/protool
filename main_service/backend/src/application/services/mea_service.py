from application.dtos.measurementDTO import  MeasurementCreate , MeasurementUpdate \
                                            ,MeasurementResponse , MeasurementDraftCreate , MeasurementDraftUpdate

from infrastructure.persistence.models.measurement_model import MeasurementModel , MeasurementDetail

from domain.exceptions.base import AppError

from domain.measurement_domain import MeasurementDomain
from domain.draft_flowmanager import DraftFlowManager
from domain.measurement_finalizer import MeasurementFinalizer

from utils.export_csv import MeasurementCSVExporter
from flask import current_app
from datetime import datetime
import io
import csv

class MeasurementService:

    def __init__(self, measurement_repo , product_repo , measurement_draft_spec_repo ,
                         measurement_raw_repo , system_config_repo):
        self.measurement_repo = measurement_repo
        self.product_repo = product_repo
        self.measurement_draft_spec_repo = measurement_draft_spec_repo
        self.measurement_raw_repo = measurement_raw_repo
        self.system_config_repo = system_config_repo
    #สร้างการวัดคุม
    def create_measurement(self, measurement: MeasurementCreate):
        product = self.product_repo.get_by_id(measurement.product_id)
        if not product:
            raise AppError("Product not found")

        spec_map = {s.point_name: s for s in product.spec_points}

        final_details = []
        all_pass = True

        for m_point in measurement.details:
            spec = spec_map.get(m_point.point_name)
            if not spec:
                raise AppError("Spec point not found")

            result = MeasurementDomain.evaluate_point(spec, m_point.measured_value)

            if not result["is_pass"]:
                all_pass = False

            final_details.append(result)

        save_data = measurement.model_dump()
        save_data["user_id"] = 1
        save_data["measurement_details"] = final_details
        save_data["final_result"] = "PASS" if all_pass else "NG"

        if not isinstance(save_data.get("details"), dict):
            save_data["details"] = {}

        save_data["details"]["measurement_snapshot"] = final_details

        return self.measurement_repo.save(save_data)
    
    def reset_point_measurement(self, draft_id: int, spec_point_id: int):
        spec = self.measurement_draft_spec_repo.get_by_id_and_draft(draft_id, spec_point_id)
        if not spec:
            raise AppError("Point not found")
        
        spec.captured_values = []
        spec.current_count = 0
        spec.final_value = None
        spec.is_pass = None
        spec.status = "pending"
        
        self.measurement_repo.commit()
        return True



    def get_all_measurements_paginated(self, page: int, page_size: int , search: str = None, search_result: str = None, start_date=None, end_date=None):
        measurements_data , total = self.measurement_repo.get_all_measurements_paginated(search , search_result , page , page_size, start_date, end_date)
        data = [MeasurementResponse.model_validate(item).model_dump(exclude_none=True)
            for item in measurements_data
        ]
        return data , total

    def export_measurements_csv(self, search=None, search_result=None, start_date=None, end_date=None):
        measurements, _ = self.measurement_repo.get_history_by_serial(
            serial=search,
            page=1,
            page_size=1000000,
            search_result=search_result,
            start_date=start_date,
            end_date=end_date
        )

        data = [
            MeasurementResponse.model_validate(item).model_dump(exclude_none=True)
            for item in measurements
        ]

        return MeasurementCSVExporter.export(data)
    def get_measurement_by_id(self, measurement_id: int):
        measurement_data = self.measurement_repo.get_by_id(measurement_id)
        if not measurement_data:
            raise AppError("Measurement not found")
        
        return MeasurementResponse.model_validate(measurement_data).model_dump(exclude_none=True)
    def update_measurement(self, measurement_id: int, measurement: MeasurementUpdate):
        pass
    def delete_measurement(self, measurement_id: int):
        pass
    def create_measurements_draft(self, user_id: int, measurement: MeasurementDraftCreate):
        current_app.logger.info("create draft ")
        exist = self.measurement_repo.get_measurements_draft_byIdUser(user_id)
        
        if exist:                
            return exist

        product = self.product_repo.get_by_id(measurement.product_id)
        if not product:
            raise AppError("Product not found")

        measurement.flow_stages = DraftFlowManager.build_flow(product)

        if measurement.serial_a != measurement.serial_b:
            measurement.status = "completed"
            measurement.stage = "completed"
            measurement.final_result = "NG"

            return self.measurement_repo.create_measurements_draft(
                measurement.model_dump(), user_id
            )

        measurement.status = "draft"
        measurement.stage = "qrcode"

        data = self.measurement_repo.create_measurements_draft(
            measurement.model_dump(), user_id
        )

        self.system_config_repo.update_active_id_draft(data.id, datetime.utcnow())

        draft_specs = [
            {
                "measurement_id": data.id,
                "spec_point_id": p.id,
                "point_name": p.point_name,
                "min_value": p.ctrl_min_value if p.sensor_type == "air_gauge" and p.ctrl_min_value else p.min_value,
                "max_value": p.ctrl_max_value if p.sensor_type == "air_gauge" and p.ctrl_max_value else p.max_value,
                "nominal_value": p.nominal_value if p.sensor_type == "air_gauge" and p.start_value else p.nominal_value,
                "sensor_device_id": p.assigned_sensor_device_id,
                "value_key": p.sensor_value_key,
                "rule_type": p.rule_type,
                "required_count": p.required_count,
                "sensor_type": p.sensor_type,
                "active_value": p.active_value,
                "group_id": p.group_id
            }
            for p in product.spec_points
        ]
        current_app.logger.info("draft_specs data: %s", draft_specs) # แบบนี้กราบไหว้ไวยากรณ์เก่าได้ถูกต้อง
        self.measurement_draft_spec_repo.bulk_create(draft_specs)

        return data

    def get_measurements_draft(self):
        data = self.measurement_repo.get_measurements_draft()
        if not data: return None
        
        return {
            "id": data.id,
            "product_id": data.product_id,
            "serial_a": data.serial_a,
            "serial_b": data.serial_b,
            "status": data.status,
            "stage": data.stage,
            "measurement_draft_specs": [
                {
                    "id": s.id,
                    "measurement_id": s.measurement_id,
                    "point_name": s.point_name,
                    "captured_values": s.captured_values, # ข้อมูลจะอยู่ที่ index 1
                    "final_value": s.final_value,
                    "is_pass": s.is_pass
                } for s in data.measurement_draft_specs
            ]
        }
    def update_measurements_draft(self, draft_id:int , data:MeasurementDraftUpdate):
        draft = self.measurement_repo.get_draft_by_id(draft_id)
        if not draft:
            raise AppError("Draft not found")
        if data.stage:
            draft.stage = data.stage
        if data.status:
            draft.status = data.status
        draft.updated_at = datetime.utcnow()
        self.measurement_repo.commit()
        return draft
    def cancel_measurements_draft(self):
        settings = self.system_config_repo.get_active_id_draft()

        if settings.active_draft_id:
            draft = self.measurement_repo.get_draft_by_id(settings.active_draft_id)
        else:
            draft = self.measurement_repo.get_draft_by_status("draft")
        if not draft:
            raise AppError("Draft not found")
        draft.status = "cancel"
        draft.updated_at = datetime.utcnow()
        self.measurement_draft_spec_repo.delete_by_measurement(draft.id)
        self.measurement_raw_repo.clear_tmp()
        settings.active_draft_id = None
        self.measurement_repo.commit()
        return draft
    def save_draft(self, stage: str):
        settings = self.system_config_repo.get_active_id_draft()
        if not settings.active_draft_id:
            raise AppError("Draft not found")
        
        measurement = self.measurement_repo.get_by_id(settings.active_draft_id)
        flow = measurement.flow_stages
        
        try:
            current_index = flow.index(measurement.stage)
            target_index = flow.index(stage)
        except ValueError as e:
            raise AppError(f"Invalid flow stage: {str(e)}")
        
        if target_index < current_index:
            return True
        
        measurement_stages = ['qrcode', 'x_axis', 'y_axis', 'air_gauge']
        if measurement.stage not in measurement_stages and target_index > current_index:
            raise AppError(f"Stage mismatch: current={measurement.stage}, target={stage}")
        
        specs = self.measurement_draft_spec_repo.get_by_measurement(measurement.id)
        is_pass = True
        
        for s in specs:
            if s.sensor_type == stage or s.sensor_type == measurement.stage:
                if s.current_count < s.required_count:
                    raise AppError(f"จุด {s.point_name} ยังวัดไม่ครบ (ครั้งที่ {s.current_count}/{s.required_count})")
                if not s.is_pass:
                    is_pass = False
                s.is_completed = True
                
        next_stage = DraftFlowManager.next_stage(flow, measurement.stage)
        
        if not is_pass or next_stage == "completed":
        # ⚠️ มั่นใจว่า MeasurementFinalizer.finalize รองรับ List ของ Specs
            details, final_result = MeasurementFinalizer.finalize(specs)

            measurement.details = details
            measurement.final_result = final_result
            measurement.stage = "completed"

        # บันทึกลงฐานข้อมูลจริงและลบ Draft ทิ้ง
            self.measurement_repo.bulk_add_details(details)
            self.measurement_draft_spec_repo.delete_by_measurement(measurement.id)
            self.measurement_repo.update_status(measurement.id, "completed")

            settings.active_draft_id = None
            self.measurement_raw_repo.clear_tmp()
        else:
        # ถ้ายังไม่จบ ให้เลื่อนไป Stage ถัดไป (เช่น จาก x_axis ไป y_axis)
            measurement.stage = next_stage
        try:
            self.measurement_repo.commit()
        except Exception as e:
            self.measurement_repo.rollback()
        # พ่น Error จริงออกมาดูใน Docker Log ถ้ายังติดปัญหา Database
            current_app.logger.error(f"SAVE_DRAFT_COMMIT_ERROR: {repr(e)}")
            raise AppError(f"Database error: {str(e)}")

        return True