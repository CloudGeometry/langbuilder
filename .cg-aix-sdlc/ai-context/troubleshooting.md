# LangBuilder - Troubleshooting Guide

## Common Error Patterns

### Database Errors

#### UNIQUE constraint failed
```
sqlalchemy.exc.IntegrityError: UNIQUE constraint failed: flow.user_id, flow.name
```
**Cause**: Attempting to create a flow with a name that already exists for the user.
**Solution**: The API auto-handles this by appending "(1)", "(2)" etc. If you see this error, check if custom code is bypassing the `_new_flow` function.

#### Table not found
```
sqlalchemy.exc.NoSuchTableError: flow
```
**Cause**: Migrations haven't been run.
**Solution**:
```bash
cd langbuilder/src/backend/base
uv run alembic upgrade head
```

#### Async session error
```
sqlalchemy.exc.InvalidRequestError: This Session's transaction has been rolled back
```
**Cause**: Using session after an exception without proper handling.
**Solution**: Use context manager or ensure proper commit/rollback:
```python
async with session_scope() as session:
    try:
        # operations
        await session.commit()
    except Exception:
        await session.rollback()
        raise
```

### Authentication Errors

#### 401 Unauthorized
```json
{"detail": "Could not validate credentials"}
```
**Causes**:
- Expired access token
- Missing/malformed Authorization header
- Invalid API key

**Solutions**:
1. Check token expiration (default: 15 minutes)
2. Use refresh endpoint: `POST /api/v1/refresh`
3. Verify header format: `Authorization: Bearer <token>`

#### 403 Forbidden
```json
{"detail": "Access denied"}
```
**Cause**: User doesn't own the resource or isn't superuser.
**Solution**: Check `flow.user_id == current_user.id` or use superuser account.

### Flow Execution Errors

#### Component build failed
```
ComponentBuildError: Failed to build vertex 'OpenAI-xxxxx'
```
**Causes**:
- Missing API key
- Invalid input values
- Network timeout

**Debug**:
1. Check component logs in the build response
2. Verify all required inputs are connected
3. Test component in isolation

#### Graph cycle detected
```
ValueError: Graph contains a cycle
```
**Cause**: Flow has circular dependencies.
**Solution**: Review flow design; remove cycles or use CycleEdge for intentional loops.

#### Vertex not found
```
KeyError: 'vertex-xxxxx'
```
**Cause**: Reference to deleted or renamed vertex.
**Solution**: Re-save the flow to regenerate vertex IDs.

### Frontend Errors

#### Node not rendering
**Cause**: Component type not registered in frontend.
**Debug**:
1. Check browser console for errors
2. Verify component is in `useTypesStore`
3. Refresh component types: clear cache and reload

#### State not updating
**Cause**: Zustand store mutation issue.
**Solution**: Always return new objects in store updates:
```typescript
// Wrong
set((state) => { state.nodes.push(node); return state; });

// Correct
set((state) => ({ nodes: [...state.nodes, node] }));
```

### LLM Provider Errors

#### OpenAI rate limit
```
openai.RateLimitError: Rate limit reached
```
**Solution**:
1. Implement exponential backoff (default: 5 retries)
2. Reduce request frequency
3. Upgrade API tier

#### Model not found
```
openai.NotFoundError: The model 'gpt-5' does not exist
```
**Solution**: Check model name in component configuration. Use dropdown options.

#### Context length exceeded
```
openai.BadRequestError: max tokens (xxx) plus messages tokens (yyy) exceeds context
```
**Solution**: Reduce input size or use model with larger context window.

## Debugging Tips

### Enable Debug Logging
```bash
export LANGBUILDER_LOG_LEVEL=DEBUG
uv run langbuilder run
```

### Inspect API Requests
```python
# Add to router for debugging
import logging
logging.getLogger("httpx").setLevel(logging.DEBUG)
```

### Check Graph Execution
```python
# In graph/graph/base.py, add logging:
logger.debug(f"Executing vertex: {vertex.id}")
logger.debug(f"Vertex inputs: {vertex_inputs}")
logger.debug(f"Vertex result: {result}")
```

### Frontend Debug
```typescript
// In stores, add logging:
console.log('Store update:', { nodes, edges });

// Enable React DevTools
// Install: https://react.dev/learn/react-developer-tools
```

### Database Query Logging
```python
# In services/database/session.py
import logging
logging.getLogger("sqlalchemy.engine").setLevel(logging.DEBUG)
```

## Performance Troubleshooting

### Slow Flow Execution
1. **Check parallel execution**: Verify independent vertices run in parallel
2. **Profile LLM calls**: Most time is often in external API calls
3. **Enable caching**: Use `cache=True` in component outputs

### High Memory Usage
1. **Large flow data**: Compress flow JSON before storing
2. **Memory leaks**: Check for unclosed sessions/connections
3. **Component cleanup**: Implement `__del__` in components if needed

### Slow API Responses
1. **Add indexes**: Check database query plans
2. **Enable pagination**: Use `get_all=False` for large datasets
3. **Cache responses**: Use Redis for frequently accessed data

## Recovery Procedures

### Reset Database
```bash
# Backup first!
cp langbuilder.db langbuilder.db.bak

# Reset
rm langbuilder.db
uv run langbuilder run  # Creates fresh DB
```

### Clear Cache
```bash
# Redis cache
redis-cli FLUSHDB

# File cache
rm -rf ~/.langbuilder/cache/
```

### Regenerate Frontend Types
```bash
cd langbuilder/src/frontend
rm -rf node_modules/.cache
npm run build
```

## Health Checks

### Backend Health
```bash
curl http://localhost:8002/health
# Expected: {"status": "ok"}
```

### Database Connection
```python
from langbuilder.services.deps import get_db_service
db = get_db_service()
# If this fails, check DATABASE_URL
```

### Component Registry
```python
from langbuilder.interface.custom_lists import CUSTOM_NODES
print(len(CUSTOM_NODES))  # Should show 455+ components
```

---
*AI Context Document - CloudGeometry AIx SDLC*
