$token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI2IiwidHlwZSI6ImFkbWluX2FjY2Vzc190b2tlbiIsImV4cCI6MTc4NTkyNzU4Mn0.SLjzgDciUK4XEYYXoANY9sFUM0vaHJev2x1oMtIPet0"
$url = "http://127.0.0.1:8010/admin/users?page=1&size=10"
$headers = @{ Authorization = "Bearer $token" }

# 暖机
1..5 | ForEach-Object { Invoke-WebRequest -Uri $url -Headers $headers -UseBasicParsing | Out-Null }

$times = @()
1..50 | ForEach-Object {
  $sw = [System.Diagnostics.Stopwatch]::StartNew()
  Invoke-WebRequest -Uri $url -Headers $headers -UseBasicParsing | Out-Null
  $sw.Stop()
  $times += $sw.Elapsed.TotalMilliseconds
}

# "count=$($times.Count)"
# "avg_ms=[math]::Round((($times | Measure-Object -Average).Average), 2)"
# "min_ms=[math]::Round((($times | Measure-Object -Minimum).Minimum), 2)"
# "max_ms=[math]::Round((($times | Measure-Object -Maximum).Maximum), 2)"

"count=$($times.Count)"
"avg_ms=$([math]::Round(($times | Measure-Object -Average).Average, 2))"
"min_ms=$([math]::Round(($times | Measure-Object -Minimum).Minimum, 2))"
"max_ms=$([math]::Round(($times | Measure-Object -Maximum).Maximum, 2))"