import sys

sys.path.append("..")

from starlette import status
from starlette.responses import RedirectResponse
from fastapi import Depends, APIRouter, Request, Form
import models
from database import engine, SessionLocal
from sqlalchemy.orm import Session
from pydantic import BaseModel
from .auth import get_current_user, verify_password, get_password_hash
import models


from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

router = APIRouter(
    prefix="/users",
    tags=["users"],
    responses={404: {"description": "Not Found"}}
)

models.Base.metadata.create_all(bind=engine)

templates = Jinja2Templates(directory="templates")


def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


class UserVerification(BaseModel):
    username: str
    password: str
    new_password: str


@router.get("/edit-password", response_class=HTMLResponse)
async def edit_user_view(request: Request, db: Session = Depends(get_db)):
    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url="/auth", status_code=status.HTTP_302_FOUND)

    user_data = db.query(models.Users).filter(models.Users.id == user.get("id")).first()

    return templates.TemplateResponse("edit-user-password.html", {"request": request, "user": user_data})

@router.post("/edit-password", response_class=HTMLResponse)
async def user_password_change(request: Request, username: str = Form(...), email: str = Form(...),
                               new_password: str = Form(None), confirm_password: str = Form(None),
                               current_password: str = Form(...), db: Session = Depends(get_db)):
    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url="/auth", status_code=status.HTTP_302_FOUND)

    user_data = db.query(models.Users).filter(models.Users.username == user.get('username')).first()

    if not user_data:
        return templates.TemplateResponse("edit-user-password.html", {"request": request, "msg": "User not found"})

    # Verify the current password
    if not verify_password(current_password, user_data.hashed_password):
        return templates.TemplateResponse("edit-user-password.html", {"request": request, "user": user_data, "msg": "Current password is incorrect"})

    # Update username and email
    user_data.username = username
    user_data.email = email

    # Update password if provided
    if new_password and confirm_password:
        if new_password != confirm_password:
            return templates.TemplateResponse("edit-user-password.html", {"request": request, "user": user_data, "msg": "New passwords do not match"})
        user_data.hashed_password = get_password_hash(new_password)  # Hash the new password before saving it

    try:
        db.add(user_data)
        db.commit()
        msg = 'User information updated successfully'
    except Exception as e:
        db.rollback()
        msg = f"Error updating user information: {str(e)}"

    return templates.TemplateResponse("edit-user-password.html", {"request": request, "user": user_data, "msg": msg})
