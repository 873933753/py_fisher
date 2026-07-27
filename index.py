from app import create_app
from app.secure import IS_PROD
import uvicorn

app = create_app()

if __name__ == "__main__":
    if IS_PROD:
        # 生产：关 reload；经 Nginx 时也可只绑 127.0.0.1
        uvicorn.run("index:app", host="0.0.0.0", port=8010, reload=False)
    else:
        uvicorn.run("index:app", host="127.0.0.1", port=8010, reload=True)
