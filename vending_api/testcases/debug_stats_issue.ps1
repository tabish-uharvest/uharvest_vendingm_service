# Debug script to test the order statistics SQL query
# This will help identify the issue with the DATABASE_ERROR

$BASE_URL = "http://localhost:8000/api/v1"

Write-Host "Debugging Order Statistics Issue"
Write-Host "================================="
Write-Host ""

# Test 1: Check if there are any orders at all
Write-Host "1. Testing basic orders endpoint to see if there are any orders..."
try {
    $response = Invoke-RestMethod -Uri "$BASE_URL/machines/c2d72758-ad10-4906-bea7-5b44530f036a/orders" -Method Get -ContentType "application/json"
    Write-Host "Orders found: $(($response | Measure-Object).Count)"
    if (($response | Measure-Object).Count -gt 0) {
        Write-Host "Sample order:"
        Write-Host ($response[0] | ConvertTo-Json -Depth 2)
    } else {
        Write-Host "No orders found in the database"
    }
} catch {
    Write-Host "Error getting orders: $($_.Exception.Message)"
    if ($_.Exception.Response) {
        $statusCode = $_.Exception.Response.StatusCode.value__
        Write-Host "HTTP Status: $statusCode"
    }
}

Write-Host ""

# Test 2: Try stats without machine_id filter
Write-Host "2. Testing stats without machine_id filter..."
try {
    $response = Invoke-RestMethod -Uri "$BASE_URL/orders/stats" -Method Get -ContentType "application/json"
    Write-Host "Success! Response:"
    Write-Host ($response | ConvertTo-Json -Depth 3)
} catch {
    Write-Host "Error: $($_.Exception.Message)"
    if ($_.Exception.Response) {
        $statusCode = $_.Exception.Response.StatusCode.value__
        Write-Host "HTTP Status: $statusCode"
        
        try {
            $stream = $_.Exception.Response.GetResponseStream()
            $reader = New-Object System.IO.StreamReader($stream)
            $responseBody = $reader.ReadToEnd()
            Write-Host "Response Body: $responseBody"
        } catch {
            Write-Host "Could not read response body"
        }
    }
}

Write-Host ""

# Test 3: Try stats with machine_id
Write-Host "3. Testing stats with machine_id..."
try {
    $response = Invoke-RestMethod -Uri "$BASE_URL/orders/stats?machine_id=c2d72758-ad10-4906-bea7-5b44530f036a" -Method Get -ContentType "application/json"
    Write-Host "Success! Response:"
    Write-Host ($response | ConvertTo-Json -Depth 3)
} catch {
    Write-Host "Error: $($_.Exception.Message)"
    if ($_.Exception.Response) {
        $statusCode = $_.Exception.Response.StatusCode.value__
        Write-Host "HTTP Status: $statusCode"
        
        try {
            $stream = $_.Exception.Response.GetResponseStream()
            $reader = New-Object System.IO.StreamReader($stream)
            $responseBody = $reader.ReadToEnd()
            Write-Host "Response Body: $responseBody"
        } catch {
            Write-Host "Could not read response body"
        }
    }
}

Write-Host ""

# Test 4: Test health endpoint to make sure API is working
Write-Host "4. Testing health endpoint..."
try {
    $response = Invoke-RestMethod -Uri "$BASE_URL/health" -Method Get -ContentType "application/json"
    Write-Host "Health check success:"
    Write-Host ($response | ConvertTo-Json -Depth 2)
} catch {
    Write-Host "Health check failed: $($_.Exception.Message)"
}

Write-Host ""
Write-Host "Debug completed!"
Write-Host ""
Write-Host "Analysis:"
Write-Host "- If orders endpoint works but stats doesn't, the issue is in the SQL query"
Write-Host "- If no orders exist, stats should return zeros but not a database error"
Write-Host "- If health check fails, there's a broader API issue"
