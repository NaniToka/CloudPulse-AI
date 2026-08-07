"""
MetricPoint model for Real-Time Observability Platform.
"""

from datetime import datetime

from sqlalchemy import JSON, DateTime, Float, Integer
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base_class import Base
from app.models.mixins import UUIDMixin


class MetricPoint(UUIDMixin, Base):
    __tablename__ = "metric_points"

    cpu_usage: Mapped[float] = mapped_column(Float, nullable=False, default=45.0)  # %
    memory_usage: Mapped[float] = mapped_column(Float, nullable=False, default=62.5)  # %
    disk_usage: Mapped[float] = mapped_column(Float, nullable=False, default=58.0)  # %
    network_traffic_mbps: Mapped[float] = mapped_column(
        Float, nullable=False, default=1240.0
    )  # Mbps
    active_users: Mapped[int] = mapped_column(Integer, nullable=False, default=8450)
    requests_per_second: Mapped[int] = mapped_column(Integer, nullable=False, default=1420)
    error_rate: Mapped[float] = mapped_column(Float, nullable=False, default=0.25)  # %
    response_time_ms: Mapped[float] = mapped_column(Float, nullable=False, default=124.0)  # ms
    db_connections_active: Mapped[int] = mapped_column(Integer, nullable=False, default=85)
    db_connections_max: Mapped[int] = mapped_column(Integer, nullable=False, default=200)
    k8s_pods_json: Mapped[list] = mapped_column(JSON, nullable=True, default=list)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
