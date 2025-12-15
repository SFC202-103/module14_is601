"""
Calculations API Routes

This module contains all calculation-related API endpoints following BREAD pattern:
- Browse: List all calculations
- Read: Get specific calculation
- Edit: Update calculation
- Add: Create new calculation
- Delete: Remove calculation

All endpoints require JWT authentication.
"""

from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.calculation import Calculation
from app.models.user import User
from app.schemas.calculation import CalculationBase, CalculationResponse, CalculationUpdate
from app.auth.dependencies import get_current_active_user

router = APIRouter(prefix="/api/calculations", tags=["Calculations"])


@router.post("/", response_model=CalculationResponse, status_code=status.HTTP_201_CREATED)
def create_calculation(
    calculation: CalculationBase,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Create a new calculation (Add in BREAD).
    
    Args:
        calculation: Calculation data (operation, operand1, operand2)
        current_user: Authenticated user
        db: Database session
        
    Returns:
        CalculationResponse: Created calculation with result
    """
    # Create new calculation
    db_calculation = Calculation(
        user_id=current_user.id,
        operation=calculation.operation,
        operand1=calculation.operand1,
        operand2=calculation.operand2
    )
    
    # Calculate result
    db_calculation.calculate()
    
    db.add(db_calculation)
    db.commit()
    db.refresh(db_calculation)
    
    return db_calculation


@router.get("/", response_model=List[CalculationResponse])
def list_calculations(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    List all calculations for current user (Browse in BREAD).
    
    Args:
        skip: Number of records to skip (pagination)
        limit: Maximum number of records to return
        current_user: Authenticated user
        db: Database session
        
    Returns:
        List[CalculationResponse]: List of user's calculations
    """
    calculations = db.query(Calculation).filter(
        Calculation.user_id == current_user.id
    ).offset(skip).limit(limit).all()
    
    return calculations


@router.get("/{calculation_id}", response_model=CalculationResponse)
def get_calculation(
    calculation_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get a specific calculation (Read in BREAD).
    
    Args:
        calculation_id: UUID of the calculation
        current_user: Authenticated user
        db: Database session
        
    Returns:
        CalculationResponse: Calculation data
        
    Raises:
        HTTPException: 404 if calculation not found or doesn't belong to user
    """
    calculation = db.query(Calculation).filter(
        Calculation.id == calculation_id,
        Calculation.user_id == current_user.id
    ).first()
    
    if not calculation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Calculation not found"
        )
    
    return calculation


@router.put("/{calculation_id}", response_model=CalculationResponse)
def update_calculation(
    calculation_id: UUID,
    calculation_update: CalculationUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Update a calculation (Edit in BREAD).
    
    Args:
        calculation_id: UUID of the calculation
        calculation_update: Updated calculation data
        current_user: Authenticated user
        db: Database session
        
    Returns:
        CalculationResponse: Updated calculation
        
    Raises:
        HTTPException: 404 if calculation not found or doesn't belong to user
    """
    db_calculation = db.query(Calculation).filter(
        Calculation.id == calculation_id,
        Calculation.user_id == current_user.id
    ).first()
    
    if not db_calculation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Calculation not found"
        )
    
    # Update fields if provided
    update_data = calculation_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_calculation, field, value)
    
    # Recalculate result
    db_calculation.calculate()
    
    db.commit()
    db.refresh(db_calculation)
    
    return db_calculation


@router.delete("/{calculation_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_calculation(
    calculation_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Delete a calculation (Delete in BREAD).
    
    Args:
        calculation_id: UUID of the calculation
        current_user: Authenticated user
        db: Database session
        
    Returns:
        None (204 No Content)
        
    Raises:
        HTTPException: 404 if calculation not found or doesn't belong to user
    """
    db_calculation = db.query(Calculation).filter(
        Calculation.id == calculation_id,
        Calculation.user_id == current_user.id
    ).first()
    
    if not db_calculation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Calculation not found"
        )
    
    db.delete(db_calculation)
    db.commit()
    
    return None


@router.get("/stats/summary")
def get_calculation_stats(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get calculation statistics for current user.
    
    Args:
        current_user: Authenticated user
        db: Database session
        
    Returns:
        dict: Statistics about user's calculations
    """
    from sqlalchemy import func
    
    # Get total count
    total = db.query(func.count(Calculation.id)).filter(
        Calculation.user_id == current_user.id
    ).scalar()
    
    # Get count by operation
    operations = db.query(
        Calculation.operation,
        func.count(Calculation.id).label('count')
    ).filter(
        Calculation.user_id == current_user.id
    ).group_by(Calculation.operation).all()
    
    operations_dict = {op: count for op, count in operations}
    
    return {
        "total_calculations": total,
        "operations": operations_dict,
        "user": {
            "id": str(current_user.id),
            "username": current_user.username,
            "email": current_user.email
        }
    }
