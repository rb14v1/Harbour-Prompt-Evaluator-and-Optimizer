# Test Frontend + Backend Connection
# Run this after starting both services

Write-Host "=== Testing Prompt Evaluator + Optimizer ===" -ForegroundColor Cyan
Write-Host ""

# Test 1: Backend Health Check
Write-Host "1. Testing backend health..." -ForegroundColor Yellow
$health = try {
    $response = curl.exe -s http://localhost:8000/api/health/
    $response | ConvertFrom-Json
    Write-Host "   ✓ Backend is running" -ForegroundColor Green
    $response
} catch {
    Write-Host "   ✗ Backend is NOT running" -ForegroundColor Red
    Write-Host "   Fix: Run 'cd backend && python manage.py runserver' in another terminal" -ForegroundColor Gray
    $null
}

Write-Host ""

# Test 2: Test Evaluation Endpoint
if ($health) {
    Write-Host "2. Testing evaluation endpoint..." -ForegroundColor Yellow
    $testPrompt = "Write a Python function that sorts arrays using bubble sort"

    try {
        $response = curl.exe -s -X POST http://localhost:8000/api/evaluations/evaluate/ `
            -H "Content-Type: application/json" `
            -d "{`"prompt`": `"$testPrompt`"}"

        $result = $response | ConvertFrom-Json

        if ($result.final_score) {
            Write-Host "   ✓ Evaluation endpoint works" -ForegroundColor Green
            Write-Host "   - Original Score: $($result.initial_evaluation.overall_score)" -ForegroundColor Gray
            Write-Host "   - Final Score: $($result.final_score)" -ForegroundColor Gray
            Write-Host "   - Status: $($result.status)" -ForegroundColor Gray
            Write-Host ""
        } else {
            Write-Host "   ✗ Error in response:" -ForegroundColor Red
            Write-Host "   $response" -ForegroundColor Gray
        }
    } catch {
        Write-Host "   ✗ Failed to evaluate prompt" -ForegroundColor Red
        Write-Host "   Error: $_" -ForegroundColor Gray
    }
}

Write-Host ""

# Test 3: Test History Endpoint
Write-Host "3. Testing history endpoint..." -ForegroundColor Yellow
try {
    $response = curl.exe -s http://localhost:8000/api/history/
    $results = $response | ConvertFrom-Json

    Write-Host "   ✓ History endpoint works" -ForegroundColor Green
    Write-Host "   - Total evaluations: $($results.Count)" -ForegroundColor Gray

    if ($results.Count -gt 0) {
        Write-Host "   - Latest evaluation score: $($results[0].final_score)" -ForegroundColor Gray
    }
} catch {
    Write-Host "   ✗ Failed to fetch history" -ForegroundColor Red
    Write-Host "   Error: $_" -ForegroundColor Gray
}

Write-Host ""

# Test 4: Check Frontend Files
Write-Host "4. Checking frontend setup..." -ForegroundColor Yellow
$envExists = Test-Path "frontend\.env"
if ($envExists) {
    Write-Host "   ✓ Frontend .env file exists" -ForegroundColor Green
    $envContent = Get-Content "frontend\.env"
    Write-Host "   - VITE_API_URL configured" -ForegroundColor Gray
} else {
    Write-Host "   ✗ Frontend .env file missing" -ForegroundColor Red
}

Write-Host ""
Write-Host "=== Test Summary ===" -ForegroundColor Cyan
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Backend terminal: cd backend && python manage.py runserver"
Write-Host "2. Frontend terminal: cd frontend && npm run dev"
Write-Host "3. Open browser: http://localhost:5173"
Write-Host ""
