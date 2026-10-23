@echo off
setlocal
cd /d "%~dp0"
echo DS60 Docker Classroom
where docker >nul 2>&1
if errorlevel 1 goto missing
docker info >nul 2>&1
if errorlevel 1 goto missing
docker image inspect postgres:17 >nul 2>&1
if errorlevel 1 (
    echo Preparing the PostgreSQL image for the first start...
    docker compose -f compose.classroom.yaml pull postgres
    if errorlevel 1 goto failed
)
echo Building the classroom application with visible logs...
set BUILDKIT_PROGRESS=plain
set COMPOSE_PROGRESS=plain
docker compose -f compose.classroom.yaml build lab
if errorlevel 1 goto failed
docker compose -f compose.classroom.yaml --profile python-core build python-core-worker
if errorlevel 1 goto failed
echo Starting the classroom and its Python/LLM worker...
docker compose -f compose.classroom.yaml --profile python-core up -d --no-build --pull never --wait lab python-core-worker
if errorlevel 1 goto failed
if not defined DS60_LAB_PORT set DS60_LAB_PORT=8765
set CLASSROOM_ADDRESS=127.0.0.1:%DS60_LAB_PORT%
for /f "delims=" %%U in ('docker compose -f compose.classroom.yaml port postgres %DS60_LAB_PORT%') do set CLASSROOM_ADDRESS=%%U
start "" "http://%CLASSROOM_ADDRESS%/journeys"
echo Progress stays in the local classroom-learning Docker volume.
echo Add TensorFlow, C++ and Spark using docs/docker-classroom.md.
exit /b 0
:missing
echo Start your installed Docker engine in Linux-container mode, then run this file again.
echo Windows uses the WSL 2 backend. See docs/docker-beginners.md.
pause
exit /b 1
:failed
echo The Docker command failed. Read the build logs above; saved volumes are retained.
pause
exit /b 1
