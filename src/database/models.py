# File: /src/database/models.py

from sqlalchemy import Column, Integer, String, TIMESTAMP, ForeignKey, CheckConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import INET, CIDR


Base = declarative_base()

# Specify schema for the existing tables
schema = "ipman"


# Service model
class Service(Base):
    __tablename__ = "services"
    __table_args__ = {"schema": schema}  # Properly reference schema

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    description = Column(String)
    created_at = Column(TIMESTAMP, server_default=func.now(), nullable=False)

    # Define a relationship to ip_addresses
    ip_addresses = relationship("IPAddress", back_populates="service")


class IPAddress(Base):
    __tablename__ = "ip_addresses"
    __table_args__ = (
        CheckConstraint(
            "(ip_address IS NOT NULL) OR (range_start IS NOT NULL AND range_end IS NOT NULL) OR (ip_range IS NOT NULL)",
            name="check_ip_or_range_or_cidr",
        ),
        {"schema": schema},
    )

    id = Column(Integer, primary_key=True)
    ip_address = Column(INET, nullable=True)
    ip_range = Column(CIDR, nullable=True)  # New column for IP ranges in CIDR notation
    range_start = Column(INET, nullable=True)
    range_end = Column(INET, nullable=True)
    service_id = Column(
        Integer, ForeignKey(f"{schema}.services.id", ondelete="SET NULL"), nullable=True
    )
    status = Column(String(50), nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now(), nullable=False)
    updated_at = Column(
        TIMESTAMP, server_default=func.now(), onupdate=func.now(), nullable=False
    )
    deactivated_at = Column(TIMESTAMP, nullable=True)

    service = relationship("Service", back_populates="ip_addresses")

    # Method to deactivate an IP
    def deactivate(self):
        self.status = "inactive"
        self.deactivated_at = func.now()  # Set the deactivation timestamp

    # Method to activate an IP
    def activate(self):
        self.status = "active"
        self.deactivated_at = None  # Clear the deactivation timestamp
