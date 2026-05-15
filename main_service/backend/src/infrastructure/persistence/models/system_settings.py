from datetime import datetime
from sqlalchemy import String, Float, DateTime, Integer , ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from infrastructure.database.database import db

class SystemSetting(db.Model):
    __tablename__ = "system_settings"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    active_product_id: Mapped[int] = mapped_column(
        ForeignKey("products.id"),
        nullable=True
    )
    active_draft_id: Mapped[int] = mapped_column(
        ForeignKey("measurements.id"),
        nullable=True
    )
    
    last_active_draft_time: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    #Check Equipment Status and save to database
    is_barcode_enabled: Mapped[int] = mapped_column(Integer, nullable = False, default = 1)
    is_mitutoyo_enabled: Mapped[int] = mapped_column(Integer, nullable = False, default = 1)
    is_airgauge_enabled: Mapped[int] = mapped_column(Integer, nullable = False, default = 1)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    

def update_settings(data: dict):
    # ดึง record แรกของ system_settings มาอัปเดต
    settings = db.session.query(SystemSetting).first()
    
    if "is_barcode_enabled" in data:
        settings.is_barcode_enabled = data["is_barcode_enabled"]
    if "is_mitutoyo_enabled" in data:
        settings.is_mitutoyo_enabled = data["is_mitutoyo_enabled"]
    if "is_airgauge_enabled" in data:
        settings.is_airgauge_enabled = data["is_airgauge_enabled"]
        
    db.session.commit()
    return {"message": "Settings updated successfully"}