from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel

from .database import get_db, engine
from .models import Base, Student

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Student Registry API", version="1.0.0")

YOUR_REG_NO = "YOUR_REG_NO"  # ← REPLACE WITH YOUR ACTUAL REG NUMBER


# ── Pydantic Schemas ──────────────────────────────────────────────────────────

class StudentCreate(BaseModel):
    name: str
    email: str
    course: str


class StudentResponse(BaseModel):
    id: int
    name: str
    email: str
    course: str

    class Config:
        from_attributes = True


# ── Endpoints ─────────────────────────────────────────────────────────────────

@app.get("/health")
def health_check(db: Session = Depends(get_db)):
    try:
        db.execute(__import__("sqlalchemy").text("SELECT 1"))
        db_status = "connected"
    except Exception:
        db_status = "disconnected"
    return {
        "status": "ok",
        "db": db_status,
        "student": YOUR_REG_NO,
    }


@app.post("/students", response_model=StudentResponse, status_code=201)
def create_student(student: StudentCreate, db: Session = Depends(get_db)):
    db_student = Student(
        name=student.name,
        email=student.email,
        course=student.course,
    )
    db.add(db_student)
    db.commit()
    db.refresh(db_student)
    return db_student


@app.get("/students", response_model=List[StudentResponse])
def list_students(db: Session = Depends(get_db)):
    return db.query(Student).all()


@app.get("/students/{reg_no}", response_model=StudentResponse)
def get_student(reg_no: int, db: Session = Depends(get_db)):
    student = db.query(Student).filter(Student.id == reg_no).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return student
