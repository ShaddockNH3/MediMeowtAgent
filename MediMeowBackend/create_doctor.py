import sys
from pathlib import Path
import os

# Add project root to path
backend_path = Path(r"e:\desktop\github\MediMeowtAgent\MediMeowBackend")
sys.path.insert(0, str(backend_path))

# Need to ensure we can import config
os.chdir(str(backend_path))

from app.database import SessionLocal
from app.models.doctor import Doctor
from app.models.department import Department
from app.utils.auth import get_password_hash
import uuid

db = SessionLocal()

try:
    # 1. Create Department if not exists
    dept = db.query(Department).filter(Department.department_name == "Internal Medicine").first()
    if not dept:
        dept = Department(
            id=str(uuid.uuid4()),
            department_name="Internal Medicine"
        )
        db.add(dept)
        db.commit()
        db.refresh(dept)
    
    print(f"Department ID: {dept.id}")

    # 2. Create Doctor
    username = "doctor"
    password = "123456"
    
    doc = db.query(Doctor).filter(Doctor.username == username).first()
    if not doc:
        doc = Doctor(
            id=str(uuid.uuid4()),
            username=username,
            password=get_password_hash(password),
            department_id=dept.id
        )
        db.add(doc)
        db.commit()
        print(f"Created doctor: {username} / {password}")
    else:
        # Reset password just in case
        doc.password = get_password_hash(password)
        db.commit()
        print(f"Updated doctor password: {username} / {password}")

except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
finally:
    db.close()
