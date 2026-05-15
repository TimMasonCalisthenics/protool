from datetime import datetime
from sqlalchemy import String, Float, DateTime, Integer
from sqlalchemy.orm import Mapped, mapped_column
from infrastructure.database.database import db

class InspectionModel(db.Model):
    __tablename__ = "history_records"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    date_time: Mapped[datetime] = mapped_column(DateTime, default=datetime.now, name="date_time")
    serial_no_a: Mapped[str] = mapped_column(String(100), name="serial_no_a")
    serial_no_b: Mapped[str] = mapped_column(String(100), name="serial_no_b")

    # Group 1: 4.5(1) - 4.5(4)
    v4_5_1: Mapped[float] = mapped_column(Float, name="4.5_1")
    v4_5_2: Mapped[float] = mapped_column(Float, name="4.5_2")
    v4_5_3: Mapped[float] = mapped_column(Float, name="4.5_3")
    v4_5_4: Mapped[float] = mapped_column(Float, name="4.5_4")

    # Group 2: 5.5(5) - 5.5(8)
    v5_5_5: Mapped[float] = mapped_column(Float, name="5.5_5")
    v5_5_6: Mapped[float] = mapped_column(Float, name="5.5_6")
    v5_5_7: Mapped[float] = mapped_column(Float, name="5.5_7")
    v5_5_8: Mapped[float] = mapped_column(Float, name="5.5_8")

    # Group 3: Specs A & B
    v50_a: Mapped[float] = mapped_column(Float, name="50_a")
    v49_6_a: Mapped[float] = mapped_column(Float, name="49.6_a")
    v50_b: Mapped[float] = mapped_column(Float, name="50_b")
    v60_b: Mapped[float] = mapped_column(Float, name="60_b")
    v141_b: Mapped[float] = mapped_column(Float, name="141_b")
    v43_8_b: Mapped[float] = mapped_column(Float, name="43.8_b")

    # Group 4 4.5(1) - 4.5(4) (Repeat)
    v4_5_1_rep: Mapped[float] = mapped_column(Float, name="4.5_1_2")
    v4_5_2_rep: Mapped[float] = mapped_column(Float, name="4.5_2_2")
    v4_5_3_rep: Mapped[float] = mapped_column(Float, name="4.5_3_2")
    v4_5_4_rep: Mapped[float] = mapped_column(Float, name="4.5_4_2")

    # Group 5 5.5(5) - 5.5(8) (Repeat)
    v5_5_5_rep: Mapped[float] = mapped_column(Float, name="5.5_5_2")
    v5_5_6_rep: Mapped[float] = mapped_column(Float, name="5.5_6_2")
    v5_5_7_rep: Mapped[float] = mapped_column(Float, name="5.5_7_2")
    v5_5_8_rep: Mapped[float] = mapped_column(Float, name="5.5_8_2")

    # Group 6: Specs A & B (Repeat)
    v50_a_rep: Mapped[float] = mapped_column(Float, name="50_a_2")
    v49_6_a_rep: Mapped[float] = mapped_column(Float, name="49.6_a_2")
    v50_b_rep: Mapped[float] = mapped_column(Float, name="50_b_2")
    v60_b_rep: Mapped[float] = mapped_column(Float, name="60_b_2")
    v141_b_rep: Mapped[float] = mapped_column(Float, name="141_b_2")
    v43_8_b_rep: Mapped[float] = mapped_column(Float, name="43.8_b_2")

    # Group 7: Result
    result29: Mapped[str] = mapped_column(String(50), name="result29")