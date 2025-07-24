# Test the PostgreSQL parameter fix for order statistics

$BASE_URL = "http://localhost:8000/api/v1"

Write-Host "Testing PostgreSQL Parameter Fix"
Write-Host "================================="
Write-Host ""

# Test 1: /orders/stats with machine_id (the one that was failing)
Write-Host "1. Testing /orders/stats with machine_id..."
try {
    $response = Invoke-RestMethod -Uri "$BASE_URL/orders/stats?machine_id=c2d72758-ad10-4906-bea7-5b44530f036a" -Method Get -ContentType "application/json"
    Write-Host "✅ Success! Response:"
    Write-Host ($response | ConvertTo-Json -Depth 3)
} catch {
    Write-Host "❌ Error: $($_.Exception.Message)"
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

# Test 2: /orders/stats without machine_id
Write-Host "2. Testing /orders/stats without machine_id..."
try {
    $response = Invoke-RestMethod -Uri "$BASE_URL/orders/stats" -Method Get -ContentType "application/json"
    Write-Host "✅ Success! Response:"
    Write-Host ($response | ConvertTo-Json -Depth 3)
} catch {
    Write-Host "❌ Error: $($_.Exception.Message)"
}

Write-Host ""

# Test 3: /orders/popular-items (also uses similar queries)
Write-Host "3. Testing /orders/popular-items..."
try {
    $response = Invoke-RestMethod -Uri "$BASE_URL/orders/popular-items" -Method Get -ContentType "application/json"
    Write-Host "✅ Success! Response:"
    Write-Host ($response | ConvertTo-Json -Depth 3)
} catch {
    Write-Host "❌ Error: $($_.Exception.Message)"
}

Write-Host ""
Write-Host "Test completed!"
Write-Host ""
Write-Host "Expected results:"
Write-Host "- Should return 200 with proper JSON data (even if zeros for empty database)"
Write-Host "- Should NOT get PostgreSQL parameter type errors"
Write-Host "- Should properly handle UUID and timestamp parameters"
