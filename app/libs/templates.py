from pathlib import Path
from fastapi.templating import Jinja2Templates

# Path(__file__).parent -> app/libs
# Path(__file__) → app/libs/templates.py
# 这里需要指向app/templates目录
templates_dir = Path(__file__).parent.parent / "templates"
templates = Jinja2Templates(directory=str(templates_dir))
