# Novita API 500 Error Analysis

## Error Summary
**Status:** Intermittent 500 Internal Server Errors
**API Endpoint:** `https://api.novita.ai/v3/gemini-2.5-flash-image-text-to-image`
**Error Frequency:** 3 consecutive failures on 2026-03-16 18:25:52-53

## Detailed Error Timeline

### Successful Requests (Baseline)
| Timestamp | Prompt Size | Modules | Duration | Status |
|-----------|-------------|---------|----------|--------|
| 18:08:24 | 5925 chars | 8 | 13s | ✅ 200 OK |
| 18:15:36 | 7185 chars | 10 | 23s | ✅ 200 OK |
| 18:06:46 | ~6000 chars | 8 | ~15s | ✅ 200 OK |

### Failed Requests (500 Errors)
| Timestamp | Prompt Size | Modules | Duration | Status |
|-----------|-------------|---------|----------|--------|
| 18:25:52 | 7112 chars | 10 | <1s | ❌ 500 Error |
| 18:25:52 | 7112 chars | 10 | <1s | ❌ 500 Error (retry 1) |
| 18:25:53 | 7112 chars | 10 | <1s | ❌ 500 Error (retry 2) |

## Root Cause Analysis

### Observation 1: Response Time Pattern
- **Successful requests:** 13-23 seconds (normal image generation time)
- **Failed requests:** <1 second (immediate rejection)
- **Pattern:** 500 errors return instantly, indicating server-side rejection before processing

### Observation 2: Payload Size
- **Successful:** 5925-7185 characters
- **Failed:** 7112 characters
- **Conclusion:** Payload size is NOT the cause (7185 succeeded, 7112 failed)

### Observation 3: Request Pattern
```
18:15:36 - Success (23s generation)
[19 minute gap with no requests]
18:25:52 - Failure (immediate 500)
18:25:52 - Retry 1 (immediate 500)
18:25:53 - Retry 2 (immediate 500)
```

### Most Likely Causes

1. **Rate Limiting (70% probability)**
   - 19-minute gap may have caused API session timeout
   - Immediate rejection suggests request was blocked at gateway/load balancer
   - Novita API may have rate limits per time window

2. **Temporary API Outage (20% probability)**
   - All 3 retries failed within 1 second
   - No exponential backoff time between failures
   - Suggests API service was down momentarily

3. **Account/Key Issues (10% probability)**
   - API key may have temporary throttling
   - Account-level rate limiting
   - Concurrent request limits

## Error Logs

### Full Error Trace
```
2026-03-16 18:25:51 | INFO | Generating image with prompt length: 7112 chars
2026-03-16 18:25:51 | INFO | Calling Novita API: https://api.novita.ai/v3/gemini-2.5-flash-image-text-to-image
2026-03-16 18:25:52 | INFO | HTTP Request: POST ... "HTTP/1.1 500 Internal Server Error"
2026-03-16 18:25:52 | WARNING | Generation attempt 1 failed: Server error '500 Internal Server Error'
2026-03-16 18:25:52 | INFO | Retrying... (1/3)
2026-03-16 18:25:52 | INFO | Calling Novita API: https://api.novita.ai/v3/gemini-2.5-flash-image-text-to-image
2026-03-16 18:25:52 | INFO | HTTP Request: POST ... "HTTP/1.1 500 Internal Server Error"
2026-03-16 18:25:52 | WARNING | Generation attempt 2 failed: Server error '500 Internal Server Error'
2026-03-16 18:25:52 | INFO | Retrying... (2/3)
2026-03-16 18:25:53 | INFO | Calling Novita API: https://api.novita.ai/v3/gemini-2.5-flash-image-text-to-image
2026-03-16 18:25:53 | INFO | HTTP Request: POST ... "HTTP/1.1 500 Internal Server Error"
2026-03-16 18:25:53 | WARNING | Generation attempt 3 failed: Server error '500 Internal Server Error'
2026-03-16 18:25:53 | ERROR | Image generation failed after 3 attempts: Server error '500 Internal Server Error'
```

## Recommendations

### Immediate Actions
1. **Add Rate Limiting:** Implement backoff logic with longer delays (exponential: 2s, 4s, 8s)
2. **Circuit Breaker:** Temporarily stop requests after 3 consecutive failures
3. **Better Error Handling:** Detect 500 errors and wait before retrying

### Long-term Solutions
1. **Fallback Model:** Configure alternative image generation model
2. **Queue System:** Implement request queue with rate limiting
3. **Monitoring:** Alert on 500 error patterns
4. **API Status Check:** Add health check endpoint for Novita API

### Configuration Changes
```python
# Recommended retry configuration
self.max_retries = 3
self.initial_backoff = 5.0  # Increase from 2s
self.backoff_multiplier = 2.0  # Exponential backoff
self.circuit_breaker_threshold = 3  # Stop after 3 consecutive failures
self.circuit_breaker_timeout = 60  # Wait 60s before retrying
```

## Testing Protocol

To validate fixes:
1. Test successful request pattern
2. Simulate rate limiting with rapid requests
3. Verify circuit breaker activates
4. Test recovery after timeout
5. Monitor error logs for new patterns

## Related Files
- Error logs: `backend/logs/avery.log`
- Image generator: `backend/api/services/infographic/image_generator.py`
- Retry logic: Lines 82-108 in image_generator.py

---
**Last Updated:** 2026-03-16 18:30
**Status:** Monitoring required for recurrence patterns
