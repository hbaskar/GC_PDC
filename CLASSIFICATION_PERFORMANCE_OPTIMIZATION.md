# Classification Performance Optimization Guide

## 📊 Current Performance Issues Identified

### 1. **Database Query Inefficiencies**
- **Mandatory JOIN with PDCRetentionPolicy**: Every query joins retention policy table
- **Multiple JOINs**: Retention policy + Template joins on every request
- **N+1 Query Problems**: Loading relationships separately
- **Inefficient Count Queries**: Separate count queries with same filters
- **Missing Index Optimization**: Some frequently filtered fields lack indexes

### 2. **Data Transfer Overhead**
- **Large Response Payloads**: Full model serialization including unused fields
- **No Response Compression**: Missing gzip compression
- **Inefficient JSON Serialization**: Using default serializers

### 3. **Caching Gaps**
- **No Query Result Caching**: Repeated identical queries
- **No Response Caching**: Static/semi-static data not cached
- **No Connection Pooling Optimization**: Database connections not optimized

## 🎯 Performance Improvement Strategy

### **Phase 1: Database Query Optimization (High Impact)**

#### 1.1 Implement Smart JOINs and Lazy Loading
```python
# Current (inefficient):
query = self.db.query(PDCClassification).join(PDCRetentionPolicy).outerjoin(PDCTemplate)

# Optimized (conditional joins):
query = self.db.query(PDCClassification)
if needs_retention_data:
    query = query.join(PDCRetentionPolicy)
if needs_template_data:
    query = query.outerjoin(PDCTemplate)
```

#### 1.2 Optimize Count Queries
```python
# Current (inefficient):
count_query = self._build_base_query(filters, search, include_deleted, include_template=False)
total = count_query.count()

# Optimized (single query with window function):
query_with_count = query.add_column(func.count().over().label('total_count'))
```

#### 1.3 Add Strategic Database Indexes
```sql
-- High-impact indexes for classifications
CREATE INDEX idx_pdc_classifications_active_level ON pdc_classifications(is_active, classification_level) WHERE is_deleted = 0;
CREATE INDEX idx_pdc_classifications_org_active ON pdc_classifications(organization_id, is_active) WHERE is_deleted = 0;
CREATE INDEX idx_pdc_classifications_created_desc ON pdc_classifications(created_at DESC) WHERE is_deleted = 0;
CREATE INDEX idx_pdc_classifications_name_search ON pdc_classifications(name) WHERE is_deleted = 0;
CREATE INDEX idx_pdc_classifications_code_unique ON pdc_classifications(code) WHERE is_deleted = 0;
```

### **Phase 2: Response Optimization (Medium Impact)**

#### 2.1 Implement Response Field Selection
```python
# Allow clients to specify needed fields
@bp.route(route="classifications", methods=["GET"])
def get_all_classifications(req: func.HttpRequest) -> func.HttpResponse:
    fields = req.params.get('fields', '').split(',') if req.params.get('fields') else None
    minimal = req.params.get('minimal', 'false').lower() == 'true'
```

#### 2.2 Create Lightweight Response Models
```python
class PDCClassificationMinimal(BaseModel):
    classification_id: int
    classification_code: str
    name: str
    is_active: bool

class PDCClassificationSummary(BaseModel):
    classification_id: int
    classification_code: str
    name: str
    classification_level: Optional[str]
    is_active: bool
    organization_id: int
```

#### 2.3 Enable Response Compression
```python
# Add to blueprint responses
def create_success_response(data: dict, status_code: int = 200, compress: bool = True) -> func.HttpResponse:
    response_body = json.dumps(data, default=str)
    
    if compress and len(response_body) > 1024:  # Compress responses > 1KB
        import gzip
        response_body = gzip.compress(response_body.encode('utf-8'))
        headers = {'Content-Encoding': 'gzip', 'Content-Type': 'application/json'}
    else:
        headers = {'Content-Type': 'application/json'}
    
    return func.HttpResponse(response_body, status_code=status_code, headers=headers)
```

### **Phase 3: Caching Strategy (High Impact)**

#### 3.1 Implement Query Result Caching
```python
from functools import lru_cache
import hashlib
import json

class CachedClassificationService(PDCClassificationService):
    def __init__(self, db: Session):
        super().__init__(db)
        self._cache = {}
        self._cache_ttl = 300  # 5 minutes
    
    def _get_cache_key(self, method_name: str, **kwargs) -> str:
        """Generate cache key from method and parameters."""
        cache_data = {'method': method_name, **kwargs}
        cache_str = json.dumps(cache_data, sort_keys=True, default=str)
        return hashlib.md5(cache_str.encode()).hexdigest()
    
    def get_all_paginated_cached(self, pagination, filters=None, search=None, include_deleted=False):
        """Cached version of get_all_paginated for frequently accessed data."""
        cache_key = self._get_cache_key('get_all_paginated', 
                                      page=pagination.page, 
                                      size=pagination.size,
                                      filters=filters,
                                      search=search)
        
        # Check cache first
        cached_result = self._get_from_cache(cache_key)
        if cached_result:
            return cached_result
        
        # Execute query and cache result
        result = self.get_all_paginated(pagination, filters, search, include_deleted)
        self._set_cache(cache_key, result)
        return result
```

#### 3.2 Add Redis Caching for Reference Data
```python
import redis
from datetime import timedelta

class RedisCacheService:
    def __init__(self):
        self.redis_client = redis.Redis(host='localhost', port=6379, db=0)
        self.default_ttl = 3600  # 1 hour
    
    def cache_classification_levels(self, levels: List[str]):
        """Cache classification levels (rarely change)."""
        key = "classification:levels"
        self.redis_client.setex(key, self.default_ttl, json.dumps(levels))
    
    def get_classification_levels(self) -> Optional[List[str]]:
        """Get cached classification levels."""
        key = "classification:levels"
        cached = self.redis_client.get(key)
        return json.loads(cached) if cached else None
```

### **Phase 4: Connection and Query Optimization (Medium Impact)**

#### 4.1 Implement Connection Pooling
```python
# In database/config.py
from sqlalchemy.pool import QueuePool

def create_engine_with_pool():
    return create_engine(
        connection_string,
        poolclass=QueuePool,
        pool_size=20,
        max_overflow=30,
        pool_timeout=30,
        pool_recycle=3600,
        pool_pre_ping=True
    )
```

#### 4.2 Add Query Optimization Hints
```python
def _build_optimized_query(self, use_index_hint: bool = False):
    """Build query with performance optimizations."""
    query = self.db.query(PDCClassification)
    
    if use_index_hint:
        # Force use of specific index for large datasets
        query = query.execution_options(
            compiled_cache={},
            isolation_level="READ_COMMITTED"
        )
    
    return query
```

### **Phase 5: Advanced Pagination Optimization (High Impact)**

#### 5.1 Implement Cursor-Based Pagination by Default for Large Datasets
```python
def get_all_smart_paginated(self, pagination: PaginationRequest, **kwargs):
    """Automatically choose optimal pagination strategy."""
    
    # Use cursor pagination for large datasets or later pages
    if pagination.page > 10 or pagination.size > 50:
        pagination.pagination_type = PaginationType.CURSOR
        return self._cursor_paginated_response(query, pagination)
    else:
        return self._offset_paginated_response(query, count_query, pagination, filters, search)
```

#### 5.2 Implement Parallel Count Queries
```python
import asyncio
from concurrent.futures import ThreadPoolExecutor

async def get_paginated_with_async_count(self, query, pagination):
    """Execute main query and count query in parallel."""
    
    with ThreadPoolExecutor() as executor:
        # Execute count and data queries in parallel
        count_future = executor.submit(query.count)
        data_future = executor.submit(lambda: query.offset(pagination.skip).limit(pagination.size).all())
        
        total = count_future.result()
        items = data_future.result()
    
    return items, total
```

## 📈 Implementation Priority

### **Immediate (Week 1-2):**
1. ✅ Add database indexes for frequently filtered fields
2. ✅ Implement conditional JOINs based on required data
3. ✅ Add minimal response option (`?minimal=true`)
4. ✅ Enable response compression for large payloads

### **Short-term (Week 3-4):**
1. ✅ Implement Redis caching for reference data
2. ✅ Add query result caching with TTL
3. ✅ Optimize count queries with window functions
4. ✅ Add field selection parameter (`?fields=id,name,code`)

### **Medium-term (Month 2):**
1. ✅ Implement smart pagination strategy switching
2. ✅ Add connection pooling optimization
3. ✅ Create specialized endpoints for common use cases
4. ✅ Add query performance monitoring

## 🎯 Expected Performance Improvements

| Optimization | Estimated Improvement |
|-------------|---------------------|
| Database Indexes | 60-80% faster queries |
| Conditional JOINs | 40-60% faster complex queries |
| Response Compression | 70-90% smaller payloads |
| Query Caching | 95%+ faster for repeated queries |
| Cursor Pagination | 80-95% faster for large datasets |
| Minimal Responses | 50-70% smaller response size |

## 🔧 Monitoring and Metrics

### Key Performance Indicators:
- Average response time per endpoint
- Database query execution time
- Cache hit/miss ratios  
- Response payload sizes
- Concurrent request handling capacity

### Monitoring Implementation:
```python
import time
from functools import wraps

def monitor_performance(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        execution_time = (time.time() - start_time) * 1000
        
        logging.info(f"Performance: {func.__name__} took {execution_time:.2f}ms")
        return result
    return wrapper
```