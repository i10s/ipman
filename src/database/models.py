# File: /src/database/models.py

from sqlalchemy import Column, Integer, String, TIMESTAMP, ForeignKey, CheckConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import INET

Base = declarative_base()

# Specify schema for the existing tables
schema = 'ipman'

# Service model
class Service(Base):
    __tablename__ = "services"
    __table_args__ = {'schema': schema}  # Properly reference schema

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    description = Column(String)
    created_at = Column(TIMESTAMP, default="NOW()")

    # Define a relationship to ip_addresses
    ip_addresses = relationship("IPAddress", back_populates="service")

# IPAddress model
class IPAddress(Base):
    __tablename__ = "ip_addresses"
    __table_args__ = (
        CheckConstraint(
            "(ip_address IS NOT NULL) OR (range_start IS NOT NULL AND range_end IS NOT NULL)",
            name="check_ip_or_range"
        ),
        {'schema': schema},  # Move the schema into the tuple of table arguments
    )

    id = Column(Integer, primary_key=True)
    ip_address = Column(INET, nullable=True)  # Support for single IPs
    range_start = Column(INET, nullable=True)  # Support for range start
    range_end = Column(INET, nullable=True)  # Support for range end
    service_id = Column(Integer, ForeignKey(f"{schema}.services.id", ondelete="SET NULL"), nullable=True)
    status = Column(String(50), nullable=False)
    created_at = Column(TIMESTAMP)
    updated_at = Column(TIMESTAMP)
    deactivated_at = Column(TIMESTAMP, nullable=True)

    # Define a relationship back to the service
    service = relationship("Service", back_populates="ip_addresses")
