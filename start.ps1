Write-Host "Starting Bharat Study Chatbot Backend..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit -Command `"cd backend; pip install -r requirements.txt; uvicorn app:app --reload`""

Write-Host "Starting Bharat Study Chatbot Frontend..." -ForegroundColor Blue
Start-Process powershell -ArgumentList "-NoExit -Command `"cd frontend; npm run dev`""

Write-Host "Both processes started in new windows! The frontend will be available at http://localhost:3000 and backend at http://localhost:8000" -ForegroundColor Yellow
