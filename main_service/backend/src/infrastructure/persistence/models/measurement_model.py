from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String , Column , Integer , ForeignKey , JSON
from infrastructure.database.database import db
from datetime import datetime
from sqlalchemy import DateTime
from sqlalchemy.orm import relationship

class MeasurementModel(db.Model):
    __tablename__ = 'measurements'
    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    product_id = Column(Integer, ForeignKey('products.id'), nullable=False)

    serial_a = Column(String(100), index=True)
    serial_b = Column(String(100), index=True)
    details = Column(JSON, nullable=True)
    status = Column(String(10), nullable=False)
    stage = Column(String(10), nullable=False)
    flow_stages = Column(JSON , nullable=False)
    final_result = Column(String(10), nullable=True)

    created_at: Mapped[datetime] = mapped_column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    operator = relationship("UserModel", back_populates="measurements")
    product = relationship("ProductModel", back_populates="measurements")
    measurement_draft_specs = relationship(
        "MeasurementDraftSpec", 
        backref="parent_measurement", # เปลี่ยนชื่อ backref เลี่ยงการซ้ำซ้อน
        overlaps="measurement"        # ยอมให้ใช้ชื่อทับซ้อนกันได้เพื่อไม่ให้แครช
    )
    measurement_details = relationship("MeasurementDetail", back_populates="measurement")

class MeasurementDetail(db.Model):
    __tablename__ = 'measurement_details'
    id: Mapped[int] = mapped_column(primary_key=True)
    measurement_id: Mapped[int] = mapped_column(db.ForeignKey('measurements.id'), index=True)
    point_name: Mapped[str] = mapped_column(db.String(50) , nullable=True)
    measured_value: Mapped[float] = mapped_column(db.Float , nullable=True)

    nominal_value: Mapped[float] = mapped_column(db.Float , nullable=True)
    upper_limit: Mapped[float] = mapped_column(db.Float , nullable=True)
    lower_limit: Mapped[float] = mapped_column(db.Float , nullable=True)

    is_pass: Mapped[bool] = mapped_column(db.Boolean, index=True)
    measurement = relationship("MeasurementModel", back_populates="measurement_details")
    
# measurement_model.py

class MeasurementDraftSpec(db.Model):
    __tablename__ = 'measurement_draft_specs'
    
    # ✅ ป้องกัน Error การประกาศตารางซ้ำซ้อน
    __table_args__ = {'extend_existing': True} 

    id = Column(Integer, primary_key=True)
    measurement_id = Column(Integer, ForeignKey('measurements.id'), nullable=False)
    spec_point_id = Column(Integer)
    point_name = Column(String(100))
    min_value = Column(db.Float)
    max_value = Column(db.Float)
    nominal_value = Column(db.Float)
    sensor_device_id = Column(Integer)
    value_key = Column(String(50))
    rule_type = Column(String(50))
    required_count = Column(Integer)
    sensor_type = Column(String(50))
    active_value = Column(Integer)
    group_id = Column(Integer)
    
    captured_values = Column(JSON, default=[]) # ✅ เก็บค่า [50.052, 15.789]
    current_count = Column(Integer, default=0)
    final_value = Column(db.Float)
    is_pass = Column(db.Boolean)
    status = Column(String(20), default='pending')
    is_completed = Column(db.Boolean, default=False)

    # ✅ ต้องมีฟังก์ชันนี้เพื่อให้ Route หรือ Service เรียกใช้ .to_dict() ได้
    def to_dict(self):
        return {
            "id": self.id,
            "measurement_id": self.measurement_id,
            "point_name": self.point_name,
            "captured_values": self.captured_values, # ✅ เลข [50.052, 15.789] อยู่ที่นี่
            "current_count": self.current_count,
            "final_value": self.final_value,
            "is_pass": self.is_pass
        }