Write-Host "Starting Bharat Study Chatbot Backend..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit -Command `"cd backend; pip install -r requirements.txt; python -m uvicorn app:app --host 0.0.0.0 --port 8080 --reload`""

Write-Host "Starting Bharat Study Chatbot Frontend..." -ForegroundColor Blue
Start-Process powershell -ArgumentList "-NoExit -Command `"cd frontend; npm run dev -- -H 0.0.0.0`""

Write-Host "Both processes started! Access on your Laptop at http://localhost:3000" -ForegroundColor Yellow
Write-Host "To access on your Phone, connect to the same Wi-Fi and open http://YOUR_LAPTOP_IP:3000" -ForegroundColor Cyan
