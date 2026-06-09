from typing import List, Tuple
from sqlalchemy import select, func
from sqlalchemy.orm import Session
from app.models.employee import Employee


class EmployeeRepository:
    def find_all_by_page_id(
        self, db: Session, page_id: int, skip: int, limit: int, title: str = None
    ) -> Tuple[int, List[Employee]]:
        query = select(Employee).where(Employee.page_id == page_id)
        if title:
            query = query.where(Employee.title.like(f"%{title}%"))
            
        query = query.order_by(Employee.name.asc())

        count_query = select(func.count()).select_from(query.subquery())
        total = db.execute(count_query).scalar_one()

        query = query.offset(skip).limit(limit)
        items = db.execute(query).scalars().all()

        return total, list(items)

    def bulk_create(self, db: Session, data: List[dict]) -> List[Employee]:
        employees = [Employee(**d) for d in data]
        db.add_all(employees)
        db.commit()
        for emp in employees:
            db.refresh(emp)
        return employees
