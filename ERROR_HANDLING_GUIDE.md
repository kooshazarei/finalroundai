# OpenAI Error Handling & Latency Configuration

## Error Handling Configuration

### Retry Logic
- `OPENAI_MAX_RETRIES=3` - Maximum number of retry attempts for failed requests
- `OPENAI_INITIAL_DELAY=1.0` - Initial delay in seconds before first retry
- `OPENAI_MAX_DELAY=60.0` - Maximum delay in seconds between retries
- `OPENAI_TIMEOUT=30.0` - Request timeout in seconds

### Circuit Breaker Configuration
- `CIRCUIT_BREAKER_FAILURE_THRESHOLD=5` - Number of failures before opening circuit
- `CIRCUIT_BREAKER_RECOVERY_TIMEOUT=60.0` - Time in seconds before attempting recovery

## Latency Optimization Configuration

### Response Streaming
- `STREAM_TIMEOUT=5.0` - Maximum time in seconds between stream chunks
- `MAX_RESPONSE_TIME=45.0` - Maximum total response time in seconds

## Usage Examples

### Environment File (.env)
```bash
# OpenAI Configuration
OPENAI_API_KEY=your_api_key_here
OPENAI_MAX_RETRIES=3
OPENAI_INITIAL_DELAY=1.0
OPENAI_MAX_DELAY=60.0
OPENAI_TIMEOUT=30.0

# Circuit Breaker Configuration
CIRCUIT_BREAKER_FAILURE_THRESHOLD=5
CIRCUIT_BREAKER_RECOVERY_TIMEOUT=60.0

# Latency Configuration
STREAM_TIMEOUT=5.0
MAX_RESPONSE_TIME=45.0
```

### Docker Configuration
```yaml
environment:
  - OPENAI_API_KEY=${OPENAI_API_KEY}
  - OPENAI_MAX_RETRIES=3
  - OPENAI_TIMEOUT=30.0
  - CIRCUIT_BREAKER_FAILURE_THRESHOLD=5
  - MAX_RESPONSE_TIME=45.0
```

## Monitoring Endpoints

### Health Check with Performance Metrics
- `GET /health/detailed` - Returns circuit breaker state and performance metrics

### Interview Status with Performance
- `GET /api/chat/status` - Returns interview status with latency statistics

## Performance Grades

The system automatically calculates performance grades:
- **Grade A**: < 2s avg response, < 5% slow requests
- **Grade B**: < 5s avg response, < 15% slow requests
- **Grade C**: < 10s avg response, < 30% slow requests
- **Grade D**: > 10s avg response or > 30% slow requests

## Circuit Breaker States

- **CLOSED**: Normal operation, all requests proceed
- **HALF_OPEN**: Testing recovery, limited requests allowed
- **OPEN**: Service degraded, requests fail immediately with fallback message

## Best Practices

1. **Monitor circuit breaker state** - If frequently open, investigate underlying issues
2. **Adjust timeouts** based on your use case - interview systems can tolerate higher latency
3. **Use performance metrics** to identify optimization opportunities
4. **Configure alerts** on Grade D performance or circuit breaker opening
5. **Test with load** to validate configuration under realistic conditions
