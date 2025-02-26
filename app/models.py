# from datetime import datetime
# from sqlalchemy import Column, DateTime, Integer, Numeric, String, Boolean, ForeignKey, Float, Date, func
# from sqlalchemy.orm import relationship
# from app.database import Base

# class User(Base):
#     __tablename__ = "users"

#     id = Column(Integer, primary_key=True, index=True)
#     full_name = Column(String, nullable=False)
#     email = Column(String, unique=True, index=True, nullable=False)
#     password = Column(String, nullable=False)
#     role = Column(String, nullable=False)  # "admin" or "tenant"
#     is_active = Column(Boolean, default=True)

#     properties = relationship("Property", back_populates="admin")  # Properties owned by the admin
#     tenants = relationship("Tenant", back_populates="user")  # Tenants associated with this user (if the user is a tenant)

# class Property(Base):
#     __tablename__ = "properties"

#     id = Column(Integer, primary_key=True, index=True)
#     name = Column(String, nullable=False)
#     location = Column(String, nullable=False)
#     description = Column(String, nullable=True)  
#     admin_id = Column(Integer, ForeignKey("users.id"))  # Refers to the user (admin/owner)

#     admin = relationship("User", back_populates="properties")
#     units = relationship("Unit", back_populates="property")

# class Unit(Base):
#     __tablename__ = "units"

#     id = Column(Integer, primary_key=True, index=True)
#     name = Column(String, nullable=False)
#     status = Column(String, default="available")  # "available", "occupied"
#     property_id = Column(Integer, ForeignKey("properties.id"))

#     property = relationship("Property", back_populates="units")
#     lease = relationship("Lease", back_populates="unit", uselist=False)

# class Tenant(Base):
#     __tablename__ = "tenants"

#     id = Column(Integer, primary_key=True, index=True)
#     user_id = Column(Integer, ForeignKey("users.id"), unique=True)  # Tenant user link

#     full_name = Column(String, nullable=False)
#     email = Column(String, nullable=False)
#     phone_number = Column(String, nullable=False)

#     user = relationship("User", back_populates="tenants")
#     leases = relationship("Lease", back_populates="tenant")
#     payments = relationship("Payment", back_populates="tenant")

# class Lease(Base):
#     __tablename__ = "leases"

#     id = Column(Integer, primary_key=True, index=True)
#     tenant_id = Column(Integer, ForeignKey("tenants.id"))
#     unit_id = Column(Integer, ForeignKey("units.id"))
#     start_date = Column(Date, nullable=False)
#     end_date = Column(Date, nullable=False)
#     rent_amount = Column(Float, nullable=False)  # Rent amount for the lease
#     deposit_amount = Column(Float, nullable=False)  # Security deposit
#     lease_status = Column(String, default="Active")  # Lease status as a string
#     created_at = Column(Date, default=func.now())  # Automatically set creation time
#     updated_at = Column(Date, default=func.now(), onupdate=func.now())  # Automatically set update time

#     tenant = relationship("Tenant", back_populates="leases")
#     unit = relationship("Unit", back_populates="lease")
#     payments = relationship("Payment", back_populates="lease")

# class Payment(Base):
#     __tablename__ = "payments"

#     id = Column(Integer, primary_key=True, index=True)
#     tenant_id = Column(Integer, ForeignKey("tenants.id"))
#     lease_id = Column(Integer, ForeignKey("leases.id"))
#     amount_paid = Column(Numeric(10, 2), nullable=False)
#     payment_status = Column(String, default="pending")
#     stripe_payment_intent_id = Column(String, unique=True, nullable=True)
#     stripe_charge_id = Column(String, unique=True, nullable=True)
#     created_at = Column(DateTime, default=datetime.utcnow)

#     tenant = relationship("Tenant", back_populates="payments")
#     lease = relationship("Lease", back_populates="payments")

#     def __repr__(self):
#         return f"<Payment {self.id}, Tenant {self.tenant_id}, Amount {self.amount_paid}>"



# from datetime import datetime
# from sqlalchemy import Column, DateTime, Integer, Numeric, String, Boolean, ForeignKey, Float, Date, func
# from sqlalchemy.orm import relationship
# from app.database import Base

# class User(Base):
#     __tablename__ = "users"

#     id = Column(Integer, primary_key=True, index=True)
#     full_name = Column(String, nullable=False)
#     email = Column(String, unique=True, index=True, nullable=False)
#     password = Column(String, nullable=False)
#     role = Column(String, nullable=False)
#     is_active = Column(Boolean, default=True)

#     properties = relationship("Property", back_populates="admin")
#     tenants = relationship("Tenant", back_populates="user")

# class Property(Base):
#     __tablename__ = "properties"

#     id = Column(Integer, primary_key=True, index=True)
#     name = Column(String, nullable=False)
#     location = Column(String, nullable=False)
#     description = Column(String, nullable=True)
#     admin_id = Column(Integer, ForeignKey("users.id"))

#     admin = relationship("User", back_populates="properties")
#     units = relationship("Unit", back_populates="property", cascade="all, delete")

# class Unit(Base):
#     __tablename__ = "units"

#     id = Column(Integer, primary_key=True, index=True)
#     name = Column(String, nullable=False)
#     status = Column(String, default="available")
#     property_id = Column(Integer, ForeignKey("properties.id"))

#     property = relationship("Property", back_populates="units")
#     lease = relationship("Lease", back_populates="unit", uselist=False, cascade="all, delete")

# class Tenant(Base):
#     __tablename__ = "tenants"

#     id = Column(Integer, primary_key=True, index=True)
#     user_id = Column(Integer, ForeignKey("users.id"), unique=True)
#     full_name = Column(String, nullable=False)
#     email = Column(String, nullable=False)
#     phone_number = Column(String, nullable=False)

#     user = relationship("User", back_populates="tenants")
#     leases = relationship("Lease", back_populates="tenant", cascade="all, delete")
#     payments = relationship("Payment", back_populates="tenant", cascade="all, delete")

# class Lease(Base):
#     __tablename__ = "leases"

#     id = Column(Integer, primary_key=True, index=True)
#     tenant_id = Column(Integer, ForeignKey("tenants.id", ondelete="CASCADE"))
#     unit_id = Column(Integer, ForeignKey("units.id", ondelete="CASCADE"))
#     start_date = Column(Date, nullable=False)
#     end_date = Column(Date, nullable=False)
#     rent_amount = Column(Float, nullable=False)
#     deposit_amount = Column(Float, nullable=False)
#     lease_status = Column(String, default="Active")
#     created_at = Column(Date, default=func.now())
#     updated_at = Column(Date, default=func.now(), onupdate=func.now())

#     tenant = relationship("Tenant", back_populates="leases")
#     unit = relationship("Unit", back_populates="lease")
#     payments = relationship("Payment", back_populates="lease")

# class Payment(Base):
#     __tablename__ = "payments"

#     id = Column(Integer, primary_key=True, index=True)
#     tenant_id = Column(Integer, ForeignKey("tenants.id", ondelete="CASCADE"))
#     lease_id = Column(Integer, ForeignKey("leases.id", ondelete="CASCADE"))
#     amount_paid = Column(Numeric(10, 2), nullable=False)
#     payment_status = Column(String, default="pending")
#     stripe_payment_intent_id = Column(String, unique=True, nullable=True)
#     stripe_charge_id = Column(String, unique=True, nullable=True)
#     created_at = Column(DateTime, default=datetime.utcnow)

#     tenant = relationship("Tenant", back_populates="payments")
#     lease = relationship("Lease", back_populates="payments")

#     def __repr__(self):
#         return f"<Payment {self.id}, Tenant {self.tenant_id}, Amount {self.amount_paid}>"

from datetime import datetime
from sqlalchemy import Column, DateTime, Integer, Numeric, String, Boolean, ForeignKey, Float, Date, func
from sqlalchemy.orm import relationship
from app.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)
    role = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)

    properties = relationship("Property", back_populates="admin")
    tenants = relationship("Tenant", back_populates="user")

class Property(Base):
    __tablename__ = "properties"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    location = Column(String, nullable=False)
    description = Column(String, nullable=True)
    image_url = Column(String, nullable=True)  # Added image URL field
    admin_id = Column(Integer, ForeignKey("users.id"))

    admin = relationship("User", back_populates="properties")
    units = relationship("Unit", back_populates="property", cascade="all, delete")

class Unit(Base):
    __tablename__ = "units"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    status = Column(String, default="available")
    property_id = Column(Integer, ForeignKey("properties.id"))

    property = relationship("Property", back_populates="units")
    lease = relationship("Lease", back_populates="unit", uselist=False, cascade="all, delete")

class Tenant(Base):
    __tablename__ = "tenants"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    full_name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    phone_number = Column(String, nullable=False)

    user = relationship("User", back_populates="tenants")
    leases = relationship("Lease", back_populates="tenant", cascade="all, delete")
    payments = relationship("Payment", back_populates="tenant", cascade="all, delete")
    support_tickets = relationship("SupportTicket", back_populates="tenant", cascade="all, delete")

class Lease(Base):
    __tablename__ = "leases"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id", ondelete="CASCADE"))
    unit_id = Column(Integer, ForeignKey("units.id", ondelete="CASCADE"))
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    rent_amount = Column(Float, nullable=False)
    deposit_amount = Column(Float, nullable=False)
    lease_status = Column(String, default="Active")
    created_at = Column(Date, default=func.now())
    updated_at = Column(Date, default=func.now(), onupdate=func.now())

    tenant = relationship("Tenant", back_populates="leases")
    unit = relationship("Unit", back_populates="lease")
    payments = relationship("Payment", back_populates="lease")

class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id", ondelete="CASCADE"))
    lease_id = Column(Integer, ForeignKey("leases.id", ondelete="CASCADE"))
    amount_paid = Column(Numeric(10, 2), nullable=False)
    payment_status = Column(String, default="pending")
    stripe_payment_intent_id = Column(String, unique=True, nullable=True)
    stripe_charge_id = Column(String, unique=True, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    tenant = relationship("Tenant", back_populates="payments")
    lease = relationship("Lease", back_populates="payments")

    def __repr__(self):
        return f"<Payment {self.id}, Tenant {self.tenant_id}, Amount {self.amount_paid}>"

class SupportTicket(Base):
    __tablename__ = "support_tickets"

    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id", ondelete="CASCADE"))
    subject = Column(String, nullable=False)
    description = Column(String, nullable=False)
    status = Column(String, default="open")  # Open, In Progress, Closed
    created_at = Column(DateTime, default=datetime.utcnow)

    tenant = relationship("Tenant", back_populates="support_tickets")

    def __repr__(self):
        return f"<SupportTicket {self.id}, Tenant {self.tenant_id}, Status {self.status}>"

# Let me know if you’d like any adjustments or if you want to add more fields! 🚀
