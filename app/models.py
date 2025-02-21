from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Float, Date
from sqlalchemy.orm import relationship
from app.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)
    role = Column(String, nullable=False)  # "admin", "landlord", "tenant"
    is_active = Column(Boolean, default=True)

    properties = relationship("Property", back_populates="landlord")
    tenants = relationship("Tenant", back_populates="user")

class Property(Base):
    __tablename__ = "properties"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    location = Column(String, nullable=False)
    landlord_id = Column(Integer, ForeignKey("users.id"))

    landlord = relationship("User", back_populates="properties")
    units = relationship("Unit", back_populates="property")

class Unit(Base):
    __tablename__ = "units"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    status = Column(String, default="available")  # "available", "occupied"
    property_id = Column(Integer, ForeignKey("properties.id"))

    property = relationship("Property", back_populates="units")
    lease = relationship("Lease", back_populates="unit", uselist=False)

class Tenant(Base):
    __tablename__ = "tenants"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)

    user = relationship("User", back_populates="tenants")
    leases = relationship("Lease", back_populates="tenant")
    payments = relationship("Payment", back_populates="tenant")

class Lease(Base):
    __tablename__ = "leases"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"))
    unit_id = Column(Integer, ForeignKey("units.id"))
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)

    tenant = relationship("Tenant", back_populates="leases")
    unit = relationship("Unit", back_populates="lease")

class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"))
    amount = Column(Float, nullable=False)
    date_paid = Column(Date, nullable=False)
    payment_method = Column(String, nullable=False)  # "M-Pesa", "Bank Transfer"

    tenant = relationship("Tenant", back_populates="payments")
