@echo off

set CONTAINER=work-measurement-web
@REM set CONTAINER=work-measurement-web-dev
set APP_BIN=./factory_app


if "%1"=="build" (
    docker-compose build
)

if "%1"=="dev" (
    docker-compose --profile dev up --build
)
if "%1"=="prod" (
    docker-compose --profile prod up --build
)


if "%1"=="init" (
    docker exec -it %CONTAINER% %APP_BIN% db init
)

if "%1"=="migrate" (
    :: %~2 คือข้อความที่ตามหลังคำว่า migrate
    echo Running migrate with message: %~2
    docker exec -it %CONTAINER% %APP_BIN% db migrate --message "%~2"
)

if "%1"=="upgrade" (
    docker exec -it %CONTAINER% %APP_BIN% db upgrade
)

if "%1"=="seed" (
    :: docker exec -it %CONTAINER% %APP_BIN% db seed-db
    docker exec -it %CONTAINER% %APP_BIN% seed-db
)