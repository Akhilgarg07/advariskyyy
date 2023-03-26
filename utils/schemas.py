import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field


class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=20)
    email: EmailStr = Field(...)


class UserUpdate(UserBase):
    username: Optional[str] = Field(..., min_length=3, max_length=20)
    email: Optional[EmailStr] = Field(...)


class UserIn(UserBase):
    password: str = Field(..., min_length=8, max_length=50)


class UserInDB(UserBase):
    hashed_password: str


class UserOut(UserBase):
    id: int

    class Config:
        orm_mode = True


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str = None


class AccountBase(BaseModel):
    account_name: str = Field(..., min_length=3, max_length=50)
    balance: float = Field(..., ge=0.00)


class AccountCreate(AccountBase):
    pass


class AccountUpdate(AccountBase):
    pass


class Account(AccountBase):
    account_id: int
    created_at: Optional[datetime.datetime]
    updated_at: Optional[datetime.datetime]

    class Config:
        orm_mode = True


class AccountInDB(AccountBase):
    user: UserOut


class CategoryBase(BaseModel):
    category_name: str = Field(..., min_length=3, max_length=50)


class CategoryCreate(CategoryBase):
    pass


class CategoryOutDB(CategoryBase):
    category_id: int

    class Config:
        orm_mode = True


class ExpenseBase(BaseModel):
    account_id: int
    category: str = Field(..., min_length=3, max_length=50)
    amount: float = Field(..., gt=0.00)
    date: datetime.date = Field(default=datetime.date.today())
    notes: Optional[str]


class ExpenseCreate(ExpenseBase):
    pass


class ExpenseInDB(ExpenseBase):
    expense_id: int
    account_id: int

    class Config:
        orm_mode = True


class BudgetBase(BaseModel):
    amount: float = Field(..., gt=0.00)
    start_date: datetime.date
    end_date: datetime.date


class BudgetCreate(BudgetBase):
    account_id: int


class BudgetUpdate(BudgetBase):
    pass


class BudgetInDB(BudgetBase):
    budget_id: int
    account_id: int

    class Config:
        orm_mode = True


class BudgetProgress(BaseModel):
    account_id: int
    category: str = Field(..., min_length=3, max_length=50)
    amount: float = Field(..., gt=0.00)
    spent: float = Field(..., gt=0.00)
    remaining: Optional[float] = Field(None, ge=0.00)
