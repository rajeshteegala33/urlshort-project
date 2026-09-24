from fastapi import FastAPI, Depends, HTTPException, status, Request, Response
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from . import db, models, schemas, auth, utils, analytics
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST

# Create DB tables (simple local dev approach)
models.Base.metadata.create_all(bind=db.engine)

app = FastAPI(title="URL Shortener with Analytics")

def get_db():
    session = db.SessionLocal()
    try:
        yield session
    finally:
        session.close()

def get_current_user(request: Request, database: Session = Depends(get_db)) -> models.User:
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing auth token")
    token = auth_header.split(" ", 1)[1]
    username = auth.decode_token(token)
    if not username:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    user = database.query(models.User).filter(models.User.username == username).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user

@app.get("/health/ready")
def ready():
    return {"status": "ready"}

@app.get("/health/live")
def live():
    return {"status": "alive"}

@app.post("/signup", response_model=schemas.TokenResponse)
def signup(payload: schemas.SignupRequest, database: Session = Depends(get_db)):
    existing = database.query(models.User).filter(models.User.username == payload.username).first()
    if existing:
        raise HTTPException(status_code=400, detail="Username already exists")
    hashed = auth.hash_password(payload.password)
    user = models.User(username=payload.username, password_hash=hashed)
    database.add(user)
    database.commit()
    database.refresh(user)
    token = auth.create_access_token(user.username)
    return {"access_token": token, "token_type": "bearer"}

@app.post("/login", response_model=schemas.TokenResponse)
def login(payload: schemas.LoginRequest, database: Session = Depends(get_db)):
    user = database.query(models.User).filter(models.User.username == payload.username).first()
    if not user or not auth.verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = auth.create_access_token(user.username)
    return {"access_token": token, "token_type": "bearer"}

@app.post("/shorten", response_model=schemas.ShortenResponse)
def shorten(payload: schemas.ShortenRequest, current_user: models.User = Depends(get_current_user), database: Session = Depends(get_db)):
    short = payload.custom_short or utils.generate_short_code()
    while database.query(models.URL).filter(models.URL.short == short).first():
        short = utils.generate_short_code()
    url = models.URL(short=short, original=str(payload.original_url), owner_id=current_user.id)
    database.add(url)
    database.commit()
    database.refresh(url)
    return {"short": short, "original": url.original}

@app.get("/{short}")
def redirect_short(short: str, request: Request, database: Session = Depends(get_db)):
    url_obj = database.query(models.URL).filter(models.URL.short == short).first()
    if not url_obj:
        raise HTTPException(status_code=404, detail="Short URL not found")
    referrer = request.headers.get("referer")
    ua = request.headers.get("user-agent")
    ip = request.client.host if request.client else None
    analytics.record_click(database, url_obj, referrer=referrer, user_agent=ua, ip=ip)
    return RedirectResponse(url_obj.original)

@app.get("/analytics/{short}", response_model=schemas.AnalyticsResponse)
def get_analytics(short: str, current_user: models.User = Depends(get_current_user), database: Session = Depends(get_db)):
    url_obj = database.query(models.URL).filter(models.URL.short == short, models.URL.owner_id == current_user.id).first()
    if not url_obj:
        raise HTTPException(status_code=404, detail="Short URL not found or not owned by user")
    total, clicks = analytics.get_analytics(database, url_obj)
    click_items = []
    for c in clicks:
        click_items.append({
            "timestamp": c.timestamp,
            "referrer": c.referrer,
            "user_agent": c.user_agent,
            "ip": c.ip
        })
    return {"short": short, "total_clicks": total, "clicks": click_items}

@app.get("/metrics")
def metrics():
    data = generate_latest()
    return Response(content=data, media_type=CONTENT_TYPE_LATEST)
