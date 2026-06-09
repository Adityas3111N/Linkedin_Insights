from typing import List, Tuple
from sqlalchemy import select, func
from sqlalchemy.orm import Session
from app.models.employee import Employee


class EmployeeRepository:
    """Encapsulates database operations for the Employee entity."""

    def find_all_by_page_id(
        self, db: Session, page_id: int, skip: int, limit: int, title: str = None
    ) -> Tuple[int, List[Employee]]:
        """Fetch a paginated list of employees working at a specific page."""
        query = select(Employee).where(Employee.page_id == page_id)
        if title:
            query = query.where(Employee.title.like(f"%{title}%"))
            
        query = query.order_by(Employee.name.asc())

        # Count total records
        count_query = select(func.count()).select_from(query.subquery())
        total_count = db.execute(count_query).scalar_one()

        # Paginate results
        query = query.offset(skip).limit(limit)
        results = db.execute(query).scalars().all()

        return total_count, list(results)

    def bulk_create(self, db: Session, employees_data: List[dict]) -> List[Employee]:
        """Perform a batch insert of Employee dictionaries."""
        employees = [Employee(**data) for data in employees_data]
        db.add_all(employees)
        db.commit()
        for employee in employees:
            db.refresh(employee)
        return employees
