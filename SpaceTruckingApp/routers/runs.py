import sys

sys.path.append("..")

from starlette import status
from starlette.responses import RedirectResponse

from fastapi import Depends, APIRouter, Request, Form
import models
from database import engine, SessionLocal
from sqlalchemy.orm import Session
from .auth import get_current_user
from sqlalchemy import func, extract



from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from datetime import datetime, timedelta

router = APIRouter(
    prefix="/runs",
    tags=["runs"],
    responses={404: {"description": "Not found"}}
)

models.Base.metadata.create_all(bind=engine)

templates = Jinja2Templates(directory="templates")
templates.env.globals['enumerate'] = enumerate


def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


@router.get("/", response_class=HTMLResponse)
async def read_all_by_user(request: Request, db: Session = Depends(get_db)):
    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url="/auth", status_code=status.HTTP_302_FOUND)

    runs = db.query(models.Run).filter(models.Run.owner_id == user.get("id")).all()

    return templates.TemplateResponse("home.html", {"request": request, "runs": runs, "user": user})


@router.get("/read-all", response_class=HTMLResponse)
async def read_all(request: Request, db: Session = Depends(get_db)):

    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url="/auth", status_code=status.HTTP_302_FOUND)

    runs = db.query(models.Run).all()
    return templates.TemplateResponse("read-all.html", {"request": request, "runs": runs, "user": user})


@router.get("/add-run", response_class=HTMLResponse)
async def add_new_run(request: Request):
    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url="/auth", status_code=status.HTTP_302_FOUND)

    return templates.TemplateResponse("add-run.html", {"request": request, "user": user})


@router.post("/add-run", response_class=HTMLResponse)
async def create_run(request: Request, commodity: str = Form(...),
                     buy_location: str = Form(...), sell_location: str = Form(...),
                     description: str = Form(...), expenditure: int = Form(...),
                     sale: int = Form(...), run_time: str = Form(...),
                     db: Session = Depends(get_db)):

    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url="/auth", status_code=status.HTTP_302_FOUND)

    runs_model = models.Run()
    runs_model.commodity = commodity
    runs_model.buy_location = buy_location
    runs_model.sell_location = sell_location
    runs_model.description = description
    runs_model.expenditure = expenditure
    runs_model.sale = sale
    runs_model.profit = sale - expenditure
    runs_model.run_time = datetime.strptime(run_time.strip(), '%H:%M').time()
    runs_model.run_date = datetime.now()
    runs_model.owner_id = user.get("id")

    db.add(runs_model)
    db.commit()

    return RedirectResponse(url="/runs", status_code=status.HTTP_302_FOUND)


@router.get("/edit-run/{run_id}", response_class=HTMLResponse)
async def edit_run(request: Request, run_id: int, db: Session = Depends(get_db)):

    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url="/auth", status_code=status.HTTP_302_FOUND)

    run = db.query(models.Run).filter(models.Run.id == run_id).first()

    return templates.TemplateResponse("edit-run.html", {"request": request, "run": run, "user": user})


@router.post("/edit-run/{run_id}", response_class=HTMLResponse)
async def edit_run_commit(request: Request, run_id: int, commodity: str = Form(...),
                          buy_location: str = Form(...), sell_location: str = Form(...),
                          description: str = Form(...), expenditure: int = Form(...),
                          sale: int = Form(...), run_time: str = Form(...),
                          db: Session = Depends(get_db)):

    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url="/auth", status_code=status.HTTP_302_FOUND)

    runs_model = db.query(models.Run).filter(models.Run.id == run_id).first()

    runs_model.commodity = commodity
    runs_model.buy_location = buy_location
    runs_model.sell_location = sell_location
    runs_model.description = description
    runs_model.expenditure = expenditure
    runs_model.sale = sale
    runs_model.profit = sale - expenditure
    try:
        if len(run_time.strip()) == 5:
            runs_model.run_time = datetime.strptime(run_time.strip(), '%H:%M').time()
        elif len(run_time.strip()) == 8:
            runs_model.run_time = datetime.strptime(run_time.strip(), '%H:%M:%S').time()
        else:
            raise ValueError("Invalid time format")
    except ValueError as e:
        return templates.TemplateResponse("edit-run.html", {"request": request, "run": runs_model, "msg": str(e)})

    runs_model.owner_id = user.get("id")

    db.add(runs_model)
    db.commit()

    return RedirectResponse(url="/runs", status_code=status.HTTP_302_FOUND)


@router.get("/delete/{run_id}")
async def delete_run(request: Request, run_id: int, db: Session = Depends(get_db)):

    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url="/auth", status_code=status.HTTP_302_FOUND)

    run_model = db.query(models.Run).filter(models.Run.id == run_id) \
        .filter(models.Run.owner_id == user.get("id")).first()

    if run_model is None:
        return RedirectResponse(url="/runs", status_code=status.HTTP_302_FOUND)

    db.query(models.Run).filter(models.Run.id == run_id).delete()

    db.commit()

    return RedirectResponse(url="/runs", status_code=status.HTTP_302_FOUND)



@router.get("/leaderboard", response_class=HTMLResponse)
async def leaderboard(request: Request, db: Session = Depends(get_db), user: dict = Depends(get_current_user)):
    if user is None:
        return RedirectResponse(url="/auth", status_code=status.HTTP_302_FOUND)

    current_month = datetime.now().month
    current_year = datetime.now().year

    previous_month = current_month - 1 if current_month > 1 else 12
    previous_month_year = current_year if current_month > 1 else current_year - 1

    # Query to calculate total profit for each user for the current month
    leaderboard_data = db.query(
        models.Users.username,
        func.coalesce(func.sum(models.Run.profit), 0).label('total_profit')).outerjoin(models.Run, models.Run.owner_id == models.Users.id).filter(
        extract('month', models.Run.run_date) == current_month,
        extract('year', models.Run.run_date) == current_year).group_by(models.Users.id).order_by(func.sum(models.Run.profit).desc()).all()

    # Query to calculate total profit for each user for the previous month
    previous_month_data = db.query(
        models.Users.username,
        func.coalesce(func.sum(models.Run.profit), 0).label('total_profit')).outerjoin(models.Run, models.Run.owner_id == models.Users.id).filter(
        extract('month', models.Run.run_date) == previous_month,
        extract('year', models.Run.run_date) == previous_month_year).group_by(models.Users.id).order_by(func.sum(models.Run.profit).desc()).limit(3).all()

    # Pass the current date to the template
    current_date = datetime.now().strftime('%B %Y')
    previous_month_date = (datetime.now().replace(day=1) - timedelta(days=1)).strftime('%B %Y')

    return templates.TemplateResponse("leaderboard.html", {
        "request": request,
        "leaderboard_data": leaderboard_data,
        "previous_month_data": previous_month_data,
        "current_date": current_date,
        "previous_month_date": previous_month_date,
        "user": user
    })
