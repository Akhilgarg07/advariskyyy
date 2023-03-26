from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import or_
from utils.db import get_db
from models.users import User
from utils.schemas import UserIn, UserInDB, UserOut, UserUpdate
from .auth import get_hashed_password, has_access

router = APIRouter()


@router.post("/users/", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def create_user(user: UserIn, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(or_(User.email == user.email,
                                        User.username == user.username)).first()
    if db_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Email or username already in use")

    hashed_password = get_hashed_password(user.password)
    db_user = User(username=user.username, email=user.email,
                   hashed_password=hashed_password)

    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return UserOut.from_orm(db_user)


@router.get("/users/{user_id}", response_model=UserOut)
def get_user(
    user_id: int,
    current_user: UserOut = Depends(has_access),
    db: Session = Depends(get_db)
):
    """
    Get user details for the current user.
    """
    # Check if the current user is the same as the user requested
    if current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")

    # Get the user details from the database
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    return user


@router.put("/users/{user_id}", response_model=UserOut, status_code=status.HTTP_202_ACCEPTED)
def update_user(
    user_id: int,
    user: UserUpdate,
    current_user: UserOut = Depends(has_access),
    db: Session = Depends(get_db)
):
    """
    Update the current user.
    """
    # Check if the current user is the same as the user requested
    if current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")

    # Get the user details from the database
    db_user = db.query(User).filter(User.id == user_id).first()

    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    update_data = user.dict(exclude_unset=True)

    if "email" in update_data and db_user.email != user.email:
        db_user_email = db.query(User).filter(User.email == user.email).first()
        if db_user_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Email already in use")
    if "username" in update_data and db_user.username != user.username:
        db_user_username = db.query(User).filter(
            User.username == user.username).first()
        if db_user_username:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Username already in use")

    # Update the user details
    db_user.username = user.username
    db_user.email = user.email

    db.commit()
    db.refresh(db_user)

    return db_user


@router.delete("/users/{user_id}")
def delete_user(
    user_id: int,
    current_user: UserOut = Depends(has_access),
    db: Session = Depends(get_db)
):
    """
    Delete the current user.
    """
    # Check if the current user is the same as the user requested
    if current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")

    # Get the user details from the database
    db_user = db.query(User).filter(User.id == user_id).first()

    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    # Delete the user
    db.delete(db_user)
    db.commit()

    return {"message": "User deleted successfully"}
