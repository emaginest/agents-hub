from mangum import Mangum
from app.main import app

# Create handler for AWS Lambda
handler = Mangum(app, lifespan="off")
