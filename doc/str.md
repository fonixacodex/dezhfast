myapp/
├── app/
│   ├── core/               # config, security, exceptions, middleware, logging
│   │   ├── config.py
│   │   ├── exceptions.py   # ۱۲ کلاس خطای دامنه‌ای
│   │   ├── handlers.py     # ۸ exception handler
│   │   ├── limiter.py      # rate limiting
│   │   ├── logging.py      # JSON + Dev formatter
│   │   ├── middleware.py   # Request ID + Logging
│   │   └── paths.py
│   ├── api/                # لایه‌ی HTTP مشترک
│   │   ├── dependencies.py
│   │   └── web.py          # صفحات HTML
│   ├── database/           # دیتابیس
│   │   ├── base.py         # Base + import_all_models()
│   │   ├── connection.py   # engine + SessionLocal
│   │   └── session.py      # get_db
│   ├── modules/            # ماژول‌های دامنه
│   │   └── auth/
│   │       ├── __init__.py   # AuthModule
│   │       ├── model.py      # User, RefreshToken
│   │       ├── schema.py     # Pydantic schemas
│   │       ├── repository.py # DB queries
│   │       ├── service.py    # business logic
│   │       └── router.py     # endpoints
│   └── main.py
├── framework/              # هسته‌ی قابل استفاده مجدد
│   ├── container.py        # DI Container
│   ├── lifecycle.py        # startup/shutdown
│   ├── module.py           # BaseModule
│   ├── routing.py          # iter_routes (سازگار با FastAPI >= 0.137)
│   └── application.py      # Application
├── cli/                    # دستورات Artisan-style
│   ├── main.py
│   └── commands/
│       ├── make.py
│       ├── migrate.py
│       ├── route.py
│       ├── serve.py
│       ├── doctor.py
│       ├── mcp.py
│       ├── tinker.py
│       └── new.py
├── resources/
│   ├── templates/          # Jinja2
│   └── static/             # CSS, JS, images
├── storage/
│   ├── db/                 # SQLite
│   ├── logs/
│   └── uploads/
├── tests/
├── pyproject.toml
├── Dockerfile
├── docker-compose.yml
└── .env.example