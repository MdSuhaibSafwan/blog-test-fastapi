from fastapi import FastAPI, Depends, status, Response
from blog_db import schemas, models
from blog_db.database import engine, SessionLocal
from sqlalchemy.orm import Session


models.Base.metadata.create_all(bind=engine)

app = FastAPI()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/blog/", status_code=200)
def get_all_blogs_api(db: Session=Depends(get_db)):
    blogs = db.query(models.Blog).all()
    response = {
        "data": blogs,
    }
    return response


@app.post("/blog/create/",status_code=201)
def create_blog(request: schemas.Blog, db: Session=Depends(get_db)):
    new_blog = models.Blog(title=request.title, content=request.content)
    db.add(new_blog)
    db.commit()
    db.refresh(new_blog)
    return new_blog


@app.get("/blog/{id}", status_code=200)
def get_queried_blog(id, response: Response, db: Session=Depends(get_db)):
    blog = db.query(models.Blog).filter(models.Blog.id == id).first()
    if not blog:
        response.status_code = 404
        return f"blog with id {id} is not found"
    return blog


@app.delete("/blog/{id}/delete/", status_code=204)
def destroy_blog(id, response: Response, db: Session=Depends(get_db)):
    db.query(models.Blog).filter(models.Blog.id == id).delete(synchronize_session=False)

    return {"status": "deleted"}


@app.put("/blog/{id}/update", status_code=202)
def update_blog(id, request: schemas.Blog, db: Session=Depends(get_db)):
    blog = db.query(models.Blog).filter(models.Blog.id == id)

    print(request)
    blog.update({models.Blog.title: request.title, models.Blog.content: request.content})
    db.commit()
    return "updated"