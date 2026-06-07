from fastapi import APIRouter
from services.assignment_service import (
    add_assignment,
    get_assignments,
    complete_assignment,
    delete_assignment
)

router = APIRouter()

@router.post("/assignments")
def create_assignment(title: str, due_date: str, priority: str = "Medium"):
    return add_assignment(title, due_date, priority)


@router.get("/assignments")
def list_assignments():
    return get_assignments()


@router.put("/assignments/complete/{assignment_id}")
def mark_complete(assignment_id: int):
    return complete_assignment(assignment_id)


@router.delete("/assignments/{assignment_id}")
def remove_assignment(assignment_id: int):
    return delete_assignment(assignment_id)