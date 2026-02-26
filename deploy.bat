@echo off
REM Deploy script for Everlast Voice Agent on Windows
REM Usage: deploy.bat

echo ==========================================
echo  EVERLAST VOICE AGENT - DEPLOYMENT
echo ==========================================
echo.

REM Check for environment variables
if "%VAPI_API_KEY%"=="" (
    echo [31m❌ VAPI_API_KEY not set[0m
    exit /b 1
)

if "%SUPABASE_URL%"=="" (
    echo [31m❌ SUPABASE_URL not set[0m
    exit /b 1
)

if "%SUPABASE_SERVICE_KEY%"=="" (
    echo [31m❌ SUPABASE_SERVICE_KEY not set[0m
    exit /b 1
)

echo 1️⃣ Checking prerequisites...
echo.

REM Check Railway CLI
where railway >nul 2>nul
if %errorlevel% neq 0 (
    echo Installing Railway CLI...
    npm install -g @railway/cli
)

REM Check Vercel CLI
where vercel >nul 2>nul
if %errorlevel% neq 0 (
    echo Installing Vercel CLI...
    npm install -g vercel
)

REM Check Supabase CLI
where supabase >nul 2>nul
if %errorlevel% neq 0 (
    echo Installing Supabase CLI...
    npm install -g supabase
)

echo.
echo 2️⃣ Deploying to Railway (Backend)...
echo -------------------------------------------
cd api

REM Login to Railway
echo Logging in to Railway...
railway login

REM Link project
if not exist ".railway\config.json" (
    railway init --name everlast-voice-agent
) else (
    railway link
)

REM Set environment variables
echo Setting environment variables...
railway variables set VAPI_API_KEY="%VAPI_API_KEY%"
railway variables set SUPABASE_URL="%SUPABASE_URL%"
railway variables set SUPABASE_SERVICE_KEY="%SUPABASE_SERVICE_KEY%"
railway variables set ANTHROPIC_API_KEY="%ANTHROPIC_API_KEY%"
railway variables set CALENDLY_API_KEY="%CALENDLY_API_KEY%"
railway variables set ENVIRONMENT="production"
railway variables set CHECKPOINTER_BACKEND="supabase"

REM Deploy
echo Deploying...
railway up

cd ..

echo.
echo 3️⃣ Deploying to Vercel (Dashboard)...
echo -------------------------------------------
cd dashboard

REM Login
echo Logging in to Vercel...
vercel login

REM Link project
vercel link --project everlast-dashboard --yes

REM Set environment variables
vercel env add NEXT_PUBLIC_SUPABASE_URL production
echo %SUPABASE_URL% | vercel env add NEXT_PUBLIC_SUPABASE_URL production
vercel env add NEXT_PUBLIC_SUPABASE_ANON_KEY production
echo %SUPABASE_ANON_KEY% | vercel env add NEXT_PUBLIC_SUPABASE_ANON_KEY production

REM Deploy
echo Deploying...
vercel --prod --yes

cd ..

echo.
echo 4️⃣ Pushing Supabase Schema...
echo -------------------------------------------

REM Link project
echo Linking Supabase project...
supabase link --project-ref %SUPABASE_URL:~-15%

REM Push schema
echo Pushing schema...
supabase db push

echo.
echo 5️⃣ Importing Vapi Assistant...
echo -------------------------------------------

REM Update assistant.json with Railway URL
for /f "tokens=*" %%a in ('cd api && railway domain') do set RAILWAY_URL=%%a
powershell -Command "(Get-Content vapi/assistant.json) -replace 'https://everlast-api.railway.app', '%RAILWAY_URL%' | Set-Content vapi/assistant.json"

REM Import assistant
curl -X POST https://api.vapi.ai/assistant ^
  -H "Authorization: Bearer %VAPI_API_KEY%" ^
  -H "Content-Type: application/json" ^
  -d @vapi/assistant.json

echo.
echo ==========================================
echo  🎉 DEPLOYMENT COMPLETE!
echo ==========================================
echo.
echo Backend: %RAILWAY_URL%
echo Dashboard: https://everlast-dashboard.vercel.app
echo.
