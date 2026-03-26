from fastapi.security import OAuth2PasswordRequestForm
import models, utils, schemas, oauth2
from database import engine, SessionLocal, get_db
from sqlalchemy.orm import Session
from fastapi import Depends, FastAPI, HTTPException, status
from schemas import PostCreate

app = FastAPI()

@app.post("/login")
def login(user_credentials: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(
        models.User.email == user_credentials.username
    ).first()

    if not user or not utils.verify(user_credentials.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid credentials"
        )

    token = oauth2.create_access_token(data={"user_id": user.id})
    return {"access_token": token, "token_type": "bearer"}

@app.post("/posts", status_code=status.HTTP_201_CREATED, response_model=schemas.PostOut, tags=["posts"])
async def create_new_post(
    post: PostCreate,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(oauth2.get_current_user)
):
    new_post = models.Post(
        owner_id=current_user_id,
        content=post.content,
        location=post.location
    )
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post

@app.get("/posts/search", tags=["posts"])
def search_posts(
    limit: int = 10,
    skip: int = 0,
    db: Session = Depends(get_db)
):
    posts = db.query(models.Post).offset(skip).limit(limit).all()
    return {"count": len(posts), "limit": limit, "skip": skip, "data": posts}

@app.get("/posts", response_model=list[schemas.PostOut], tags=["posts"])
def get_posts(db: Session = Depends(get_db)):
    return db.query(models.Post).all()

@app.get("/posts/{id}", response_model=schemas.PostOut, tags=["posts"])
def get_post_by_id(id: int, db: Session = Depends(get_db)):
    post = db.query(models.Post).filter(models.Post.id == id).first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Post with id {id} not found")
    return post

@app.put("/posts/{id}", response_model=schemas.PostOut, tags=["posts"])
def put_post_by_id(
    id: int,
    post: PostCreate,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(oauth2.get_current_user)
):
    post_query = db.query(models.Post).filter(models.Post.id == id)
    existing_post = post_query.first()
    if not existing_post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Post with id {id} not found")
    if existing_post.owner_id != current_user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Not authorized to update this post")
    post_query.update(post.model_dump(), synchronize_session=False)
    db.commit()
    return post_query.first()

@app.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT, tags=["posts"])
def delete_post_by_id(
    id: int,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(oauth2.get_current_user)
):
    post = db.query(models.Post).filter(models.Post.id == id).first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Post with id {id} not found")
    if post.owner_id != current_user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Not authorized to delete this post")
    db.delete(post)
    db.commit()

@app.post("/users", status_code=status.HTTP_201_CREATED, response_model=schemas.UserOut, tags=["users"])
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    hashed_pwd = utils.hash(user.password)
    new_user = models.User(email=user.email, password=hashed_pwd)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user