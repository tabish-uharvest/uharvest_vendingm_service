# Simple test for the fixed datetime serialization issue

$BASE_URL = "http://localhost:8000/api/v1"

Write-Host "Testing Datetime Serialization Fix"
Write-Host "=================================="
Write-Host ""

# Test the /orders/stats endpoint
Write-Host "Testing /orders/stats endpoint..."
try {
    $response = Invoke-RestMethod -Uri "$BASE_URL/orders/stats?machine_id=c2d72758-ad10-4906-bea7-5b44530f036a" -Method Get -ContentType "application/json"
    Write-Host "Success! Response:"
    Write-Host ($response | ConvertTo-Json -Depth 3)
} catch {
    $errorDetails = $_.Exception.Response
    if ($errorDetails) {
        $statusCode = $errorDetails.StatusCode.value__
        Write-Host "HTTP Status: $statusCode"
        
        # Try to get the response body
        try {
            $stream = $errorDetails.GetResponseStream()
            $reader = New-Object System.IO.StreamReader($stream)
            $responseBody = $reader.ReadToEnd()
            Write-Host "Response Body: $responseBody"
        } catch {
            Write-Host "Could not read response body"
        }
    } else {
        Write-Host "Error: $($_.Exception.Message)"
    }
}

Write-Host ""
Write-Host "Test completed!"
