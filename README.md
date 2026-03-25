# OMON Logistics Backend

Django + DRF + SimpleJWT + drf-spectacular asosidagi backend. Hozircha SQLite bilan ishlaydi, Docker orqali ham ko‘tarish mumkin.

## Tez start (lokal, SQLite)
```bash
cd C:\Users\whoami\PycharmProjects\LOGISTICS
python -m venv .venv
.venv\Scripts\pip install --upgrade pip
.venv\Scripts\pip install -r requirements.txt
.venv\Scripts\python manage.py migrate
.venv\Scripts\python manage.py create_default_dispatchers
.venv\Scripts\python manage.py runserver 0.0.0.0:8000
```

## Docker bilan (SQLite ichida)
```bash
cd C:\Users\whoami\PycharmProjects\LOGISTICS
docker-compose up --build
```
`entrypoint.sh` migratsiya qiladi, default userlarni yaratadi va serverni 8000-portda ishga tushiradi.

## Swagger va API
- Swagger UI: `http://localhost:8000/api/docs/`
- OpenAPI schema: `http://localhost:8000/api/schema/`

## Auth endpointlari
- `POST /api/auth/login/` — email/parol bilan JWT olish (dispatcher yoki main dispatcher)
- `POST /api/auth/token/refresh/`
- `GET /api/auth/me/` — joriy foydalanuvchi

Default foydalanuvchilar (create_default_dispatchers orqali):
- main dispatcher: `main@example.com` / `pass1234`
- dispatcher: `dispatcher@example.com` / `pass1234`

## Asosiy app/modelar
- `accounts` — Custom User (role: `main_dispatcher`, `dispatcher`)
- `clients`, `drivers`, `vehicles`
- `orders` (Order, OrderPoint, OrderStatusHistory, OrderProof) — statuslar va soft delete, public_id generator, status transition validator
- `payouts` — Payout (order bilan unique)
- `notifications`, `telegram_bot` (BotSession indexed), `audit`, `common` (timestamp bazasi)

## Qo‘shimcha eslatma
- `.gitignore` sozlangan (`.venv`, `db.sqlite3`, media/static va IDE fayllari kiritilmaydi).
- Hozircha storage mahalliy; prod uchun S3/MinIO konfiguratsiyasi qo‘shilishi mumkin.

"# Omon_LOGISTICS" 
