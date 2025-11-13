# Advanced Pagination Guide for PDC API

## Overview

The PDC API now supports advanced server-level pagination with multiple strategies and comprehensive filtering capabilities. This guide covers all the features and usage patterns.

## Pagination Types

### 1. Offset-Based Pagination (Default)
- Traditional page-based pagination
- Best for: User interfaces with page numbers
- Performance: Good for small to medium datasets

### 2. Cursor-Based Pagination
- High-performance pagination using cursor tokens
- Best for: Large datasets, real-time data, mobile APIs
- Performance: Consistent performance regardless of dataset size

## Basic Usage

### Offset Pagination
```
GET /api/classifications?page=1&size=20
GET /api/lookups/codes?page=2&size=50
```

### Cursor Pagination
```
GET /api/classifications?pagination_type=cursor&size=20
GET /api/classifications?pagination_type=cursor&size=20&cursor=12345
```

## Pagination Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `page` | int | 1 | Page number (offset pagination) |
| `size` | int | 20 | Items per page (1-100) |
| `pagination_type` | string | "offset" | "offset" or "cursor" |
| `cursor` | string | null | Cursor token for cursor pagination |
| `sort_by` | string | "created_at" | Field to sort by |
| `sort_order` | string | "desc" | "asc" or "desc" |

## Sorting

### Available Sort Fields

**Classifications:**
- `classification_id`, `name`, `code`, `created_at`, `modified_at`
- `sensitivity_rating`, `organization_id`

**Lookups:**
- `lookup_code_id`, `code`, `name`, `created_at`, `modified_at`
- `sort_order`, `organization_id`

### Examples
```
GET /api/classifications?sort_by=name&sort_order=asc
GET /api/lookups/codes?sort_by=sort_order&sort_order=asc
```

## Filtering

### Classification Filters

| Filter | Type | Example | Description |
|--------|------|---------|-------------|
| `is_active` | boolean | `true`/`false` | Active status |
| `classification_level` | string | `SECRET` | Exact classification level |
| `media_type` | string | `ELECTRONIC` | Exact media type |
| `file_type` | string | `PDF` | Exact file type |
| `series` | string | `A1` | Exact series |
| `organization_id` | int | `123` | Exact organization ID |
| `sensitivity_rating` | int | `5` | Exact sensitivity rating |
| `sensitivity_min` | int | `3` | Minimum sensitivity rating |
| `sensitivity_max` | int | `7` | Maximum sensitivity rating |
| `created_after` | ISO date | `2023-01-01T00:00:00Z` | Created after date |
| `created_before` | ISO date | `2023-12-31T23:59:59Z` | Created before date |
| `organization_ids` | comma-separated | `123,456,789` | Multiple organization IDs |
| `classification_levels` | comma-separated | `SECRET,TOP_SECRET` | Multiple levels |

### Lookup Filters

| Filter | Type | Example | Description |
|--------|------|---------|-------------|
| `is_active` | boolean | `true`/`false` | Active status |
| `lookup_type` | string | `COUNTRY` | Exact lookup type |
| `parent_lookup_code_id` | int | `123` | Parent code ID |
| `organization_id` | int | `123` | Exact organization ID |
| `sort_order_min` | int | `10` | Minimum sort order |
| `sort_order_max` | int | `50` | Maximum sort order |
| `parent_codes_only` | boolean | `true` | Only parent codes |
| `child_codes_only` | boolean | `true` | Only child codes |
| `lookup_types` | comma-separated | `COUNTRY,STATE` | Multiple lookup types |
| `organization_ids` | comma-separated | `123,456` | Multiple organization IDs |

## Search

Full-text search across multiple fields:

### Classifications Search Fields
- `name`, `description`, `code`, `series`, `classification_purpose`
- `classification_level`, `media_type`, `file_type`

### Lookups Search Fields
- `code`, `name`, `description`, `lookup_type`, `additional_info`

### Examples
```
GET /api/classifications?search=secret
GET /api/lookups/codes?search=country&lookup_type=GEOGRAPHY
```

## Complex Queries

### Example 1: Active Classifications with Filtering
```
GET /api/classifications?page=1&size=25&is_active=true&classification_level=SECRET&sensitivity_min=3&sort_by=name&sort_order=asc
```

### Example 2: Search with Pagination
```
GET /api/classifications?search=document&page=2&size=10&pagination_type=offset
```

### Example 3: Cursor Pagination for Performance
```
GET /api/classifications?pagination_type=cursor&size=50&sort_by=classification_id&sort_order=desc
```

### Example 4: Lookups by Type with Filters
```
GET /api/lookups/codes/COUNTRY?is_active=true&sort_by=sort_order&sort_order=asc&page=1&size=100
```

### Example 5: Multiple Organization Filter
```
GET /api/classifications?organization_ids=1,2,3&is_active=true&size=50
```

## Response Format

### Standard Paginated Response
```json
{
  "items": [...],
  "pagination": {
    "page": 1,
    "size": 20,
    "total": 150,
    "pages": 8,
    "has_next": true,
    "has_previous": false,
    "next_cursor": null,
    "previous_cursor": null
  },
  "metadata": {
    "filters_applied": {
      "is_active": true,
      "classification_level": "SECRET"
    },
    "sort_info": {
      "sort_by": "name",
      "sort_order": "asc"
    },
    "search_term": null,
    "total_filtered": 150,
    "execution_time_ms": 45.2
  }
}
```

### Cursor Pagination Response
```json
{
  "items": [...],
  "pagination": {
    "page": 1,
    "size": 20,
    "total": -1,
    "pages": -1,
    "has_next": true,
    "has_previous": false,
    "next_cursor": "eyJpZCI6MTIzNDV9",
    "previous_cursor": null
  },
  "metadata": {
    "sort_info": {
      "sort_by": "classification_id",
      "sort_order": "desc",
      "pagination_type": "cursor"
    },
    "execution_time_ms": 12.8
  }
}
```

## Performance Guidelines

### When to Use Offset Pagination
- Small to medium datasets (< 10,000 records)
- User interfaces requiring page numbers
- Simple sorting and filtering
- When total count is needed

### When to Use Cursor Pagination
- Large datasets (> 10,000 records)
- Real-time data feeds
- Mobile applications
- High-frequency API calls
- When consistent performance is critical

### Performance Tips
1. **Use specific filters** to reduce dataset size
2. **Avoid large page sizes** (keep under 100 items)
3. **Use cursor pagination** for large datasets
4. **Limit sorting fields** to indexed columns
5. **Cache frequently accessed data** at the application level

## Special Endpoints

### Summary Endpoints
```
GET /api/classifications/summary
GET /api/lookups/types/summary
```

Returns aggregate statistics and counts without full data.

### Batch Endpoints
```
POST /api/lookups/batch/codes
{
  "lookup_types": ["COUNTRY", "STATE", "PRIORITY"],
  "active_only": true
}
```

Get multiple lookup types in a single request.

## Error Handling

### Common Errors
- **400**: Invalid pagination parameters (page < 1, size > 100)
- **400**: Invalid filter values (non-numeric for numeric fields)
- **400**: Invalid sort field
- **404**: Resource not found (for type-specific endpoints)
- **500**: Database or server errors

### Example Error Response
```json
{
  "error": "Invalid pagination parameters",
  "detail": "Page size must be between 1 and 100",
  "status_code": 400
}
```

## Migration from Simple Pagination

### Old Format
```
GET /api/classifications
```

### New Format (Backward Compatible)
```
GET /api/classifications?page=1&size=20
```

The new pagination system maintains backward compatibility while adding advanced features. Existing clients will continue to work with default pagination settings.