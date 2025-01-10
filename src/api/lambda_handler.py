from mangum import Mangum
from .routes import app

handler = Mangum(app) 