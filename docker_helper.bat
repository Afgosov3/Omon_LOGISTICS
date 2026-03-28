@echo off
REM Docker helper script for Omon Logistics

setlocal enabledelayedexpansion

if "%1"=="" (
    echo.
    echo Usage: docker_helper.bat [command]
    echo.
    echo Available commands:
    echo   up              - Start all Docker services
    echo   down            - Stop all Docker services
    echo   rebuild         - Rebuild and start all services
    echo   logs            - Show backend logs
    echo   logs-bot        - Show bot logs
    echo   logs-nginx      - Show nginx logs
    echo   shell-backend   - Open shell in backend container
    echo   shell-bot       - Open shell in bot container
    echo   migrate         - Run migrations
    echo   clean           - Remove containers and volumes
    echo.
    exit /b 1
)

if "%1"=="up" (
    echo Starting Docker services...
    docker compose up -d
    echo.
    echo Services started!
    echo Access API at: http://localhost:8888/api/docs/
    exit /b 0
)

if "%1"=="down" (
    echo Stopping Docker services...
    docker compose down
    echo Services stopped.
    exit /b 0
)

if "%1"=="rebuild" (
    echo Rebuilding Docker services...
    docker compose down
    docker compose build --no-cache
    docker compose up -d
    echo.
    echo Services rebuilt and started!
    echo Access API at: http://localhost:8888/api/docs/
    exit /b 0
)

if "%1"=="logs" (
    echo Showing backend logs (Ctrl+C to exit)...
    docker logs -f logistics_backend
    exit /b 0
)

if "%1"=="logs-bot" (
    echo Showing bot logs (Ctrl+C to exit)...
    docker logs -f logistics_bot
    exit /b 0
)

if "%1"=="logs-nginx" (
    echo Showing nginx logs (Ctrl+C to exit)...
    docker logs -f logistics_nginx
    exit /b 0
)

if "%1"=="shell-backend" (
    echo Opening shell in backend container...
    docker exec -it logistics_backend bash
    exit /b 0
)

if "%1"=="shell-bot" (
    echo Opening shell in bot container...
    docker exec -it logistics_bot bash
    exit /b 0
)

if "%1"=="migrate" (
    echo Running migrations in backend...
    docker exec -it logistics_backend python manage.py migrate
    exit /b 0
)

if "%1"=="clean" (
    echo WARNING: This will remove all containers and volumes!
    set /p confirm="Continue? (y/n): "
    if /i "!confirm!"=="y" (
        docker compose down -v
        echo All containers and volumes removed.
    ) else (
        echo Cancelled.
    )
    exit /b 0
)

echo Unknown command: %1
echo Run 'docker_helper.bat' with no arguments to see available commands.
exit /b 1

