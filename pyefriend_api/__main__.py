# -*- coding:utf-8 -*-
from pyefriend_api.api import create_app
import uvicorn


def main():
    app = f'{create_app.__module__}:{create_app.__name__}'

    uvicorn.run(app,
                host='0.0.0.0',
                port=8000,
                factory=True,
                reload=True)


if __name__ == "__main__":
    main()
