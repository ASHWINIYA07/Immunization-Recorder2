from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database import SessionLocal, engine, Base
from models import Child as ChildModel
from scheduler import (
    generate_schedule,
    mark_vaccine_done,
    calculate_progress,
    update_all_status
)
from certificate import generate_certificate

app = FastAPI()

# Create tables
Base.metadata.create_all(bind=engine)


# 📌 Request Models
class Child(BaseModel):
    name: str
    dob: str


class VaccineUpdate(BaseModel):
    name: str
    vaccine: str


# 🏠 Home Route
@app.get("/")
def home():
    return {"message": "ImmuniTrack Backend Running"}


# ➕ Add Child (DB version)
@app.post("/add_child")
def add_child(child: Child):
    db: Session = SessionLocal()

    existing = db.query(ChildModel).filter(ChildModel.name == child.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Child already exists")

    schedule = generate_schedule(child.dob)

    new_child = ChildModel(
        name=child.name,
        dob=child.dob,
        schedule=schedule
    )

    db.add(new_child)
    db.commit()
    db.refresh(new_child)

    return {
        "message": "Child added successfully",
        "schedule": schedule
    }


# 📋 Get Schedule
@app.get("/get_schedule/{name}")
def get_schedule(name: str):
    db: Session = SessionLocal()

    child = db.query(ChildModel).filter(ChildModel.name == name).first()

    if not child:
        raise HTTPException(status_code=404, detail="Child not found")

    updated_schedule = update_all_status(child.schedule)

    # Save updated status back to DB
    child.schedule = updated_schedule
    db.commit()

    return {
        "name": name,
        "schedule": updated_schedule
    }


# 💉 Update Vaccine
@app.post("/update_vaccine")
def update_vaccine(data: VaccineUpdate):
    db: Session = SessionLocal()

    child = db.query(ChildModel).filter(ChildModel.name == data.name).first()

    if not child:
        raise HTTPException(status_code=404, detail="Child not found")

    success = mark_vaccine_done(child.schedule, data.vaccine)

    if not success:
        raise HTTPException(status_code=404, detail="Vaccine not found")

    db.commit()

    return {"message": f"{data.vaccine} marked as done"}


# 📊 Progress
@app.get("/progress/{name}")
def get_progress(name: str):
    db: Session = SessionLocal()

    child = db.query(ChildModel).filter(ChildModel.name == name).first()

    if not child:
        raise HTTPException(status_code=404, detail="Child not found")

    progress = calculate_progress(child.schedule)

    return {
        "name": name,
        "progress_percentage": progress
    }


# 📄 Certificate API
@app.get("/certificate/{name}")
def get_certificate(name: str):
    db: Session = SessionLocal()

    child = db.query(ChildModel).filter(ChildModel.name == name).first()

    if not child:
        raise HTTPException(status_code=404, detail="Child not found")

    file = generate_certificate(name, child.schedule)

    return {
        "message": "Certificate generated successfully",
        "file": file
    }