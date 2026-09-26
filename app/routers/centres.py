from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import CentreTest, DiagnosticCentre, DiagnosticTest
from app.schemas import (
    Centre,
    CentreCreate,
    CentreTestCreate,
    CentreTestResponse,
    Test,
    TestCreate,
)

router = APIRouter(tags=["centres"])


@router.post("/centres/", response_model=Centre)
def create_centre(data: CentreCreate, db: Session = Depends(get_db)):
    centre = DiagnosticCentre(name=data.name, location=data.location)
    db.add(centre)
    db.commit()
    db.refresh(centre)
    return centre


@router.get("/centres/", response_model=list[Centre])
def list_centres(db: Session = Depends(get_db)):
    return db.scalars(select(DiagnosticCentre)).all()


@router.post("/tests/", response_model=Test)
def create_test(data: TestCreate, db: Session = Depends(get_db)):
    test = DiagnosticTest(name=data.name)
    db.add(test)
    db.commit()
    db.refresh(test)
    return test


@router.get("/tests/", response_model=list[Test])
def list_tests(db: Session = Depends(get_db)):
    return db.scalars(select(DiagnosticTest)).all()


@router.post(
    "/centres/{centre_id}/tests/",
    response_model=CentreTestResponse,
)
def add_test_to_centre(
    centre_id: int,
    data: CentreTestCreate,
    db: Session = Depends(get_db),
):
    centre = db.get(DiagnosticCentre, centre_id)
    test = db.get(DiagnosticTest, data.test_id)

    if not centre:
        raise HTTPException(status_code=404, detail="Centre not found")

    if not test:
        raise HTTPException(status_code=404, detail="Test not found")

    existing = db.get(CentreTest, (centre_id, data.test_id))
    if existing:
        raise HTTPException(
            status_code=400,
            detail="Test already available at this centre",
        )

    centre_test = CentreTest(
        centre_id=centre_id,
        test_id=data.test_id,
        price=data.price,
    )
    db.add(centre_test)
    db.commit()

    return {
        "id": test.id,
        "name": test.name,
        "price": centre_test.price,
    }


@router.get(
    "/centres/{centre_id}",
)
def get_centre(centre_id: int, db: Session = Depends(get_db)):
    centre = db.get(DiagnosticCentre, centre_id)

    if not centre:
        raise HTTPException(status_code=404, detail="Centre not found")

    tests = [
        {
            "id": item.test.id,
            "name": item.test.name,
            "price": item.price,
        }
        for item in centre.tests
    ]

    return {
        "id": centre.id,
        "name": centre.name,
        "location": centre.location,
        "tests": tests,
    }
