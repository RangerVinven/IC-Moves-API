from fastapi import FastAPI

from routes.users import router as users_router
from routes.images import router as images_router
from routes.properties import router as properties_router
from routes.authentication import router as authentication_router  # Login and sign-out functionality
from routes.saved_properties import router as saved_properties_router

app = FastAPI()

app.include_router(users_router, prefix="/users")
app.include_router(properties_router, prefix="/properties")
app.include_router(images_router, prefix="/images")
app.include_router(saved_properties_router, prefix="/saved")
app.include_router(authentication_router)
