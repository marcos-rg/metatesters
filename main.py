from app.logs import setup_logging
from app.ui.main import demo
from dotenv import load_dotenv

load_dotenv(override=True)

setup_logging()

demo.launch(inbrowser=True)

