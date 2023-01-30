from fastapi import FastAPI

import api


def create_app():
    app_ = FastAPI(docs_url="/docs")
    app_.include_router(api.router)
    return app_


app = create_app()
