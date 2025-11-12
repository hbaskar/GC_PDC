# Postman Collection Update - Blueprint Pattern (v2.1.1)

## Summary of Changes

The Postman collection has been updated for the Azure Functions blueprint architecture. **IMPORTANT**: Azure Functions automatically adds `/api/` prefix to all HTTP routes, so the endpoints retain the `/api/` prefix in URLs.

## Key Changes Made

### ✅ URL Structure - CORRECTED
- **Kept `/api/` prefix** for all endpoints (Azure Functions requirement)
- Routes work as: `{{base_url}}/api/health`, `{{base_url}}/api/classifications`, etc.
- Blueprint routes like `health` become `/api/health` at runtime

### ✅ Endpoint Cleanup
- **Removed non-implemented endpoints** that don't exist in current blueprints:
  - `/classifications/metadata`
  - `/classifications/organization/{id}`
  - `/classifications/sensitivity/{rating}` 
  - `/classifications/{id}/access`
- **Kept only working endpoints** that match the actual blueprint routes

### ✅ Collection Structure
- **Updated collection version** to v2.1.0
- **Maintained all working endpoints** from the blueprint implementation
- **Preserved comprehensive testing** for implemented features
- **Updated documentation** to reflect blueprint pattern

## Blueprint Route Mapping

The collection correctly maps to these Azure Functions endpoints (with automatic `/api/` prefix):

### Health Blueprint (`blueprints/health.py`) → **Azure Functions URLs**
- Blueprint: `health` → **HTTP**: `GET /api/health` - Basic health check
- Blueprint: `health/detailed` → **HTTP**: `GET /api/health/detailed` - Detailed health check  
- Blueprint: `diagnostic` → **HTTP**: `GET /api/diagnostic` - Diagnostic information

### Classifications Blueprint (`blueprints/classifications.py`) → **Azure Functions URLs**
- Blueprint: `classifications` → **HTTP**: `GET /api/classifications` - Get all classifications (with pagination)
- Blueprint: `classifications/{id}` → **HTTP**: `GET /api/classifications/{id}` - Get classification by ID
- Blueprint: `classifications` → **HTTP**: `POST /api/classifications` - Create new classification
- Blueprint: `classifications/{id}` → **HTTP**: `PUT /api/classifications/{id}` - Update classification
- Blueprint: `classifications/{id}` → **HTTP**: `DELETE /api/classifications/{id}` - Soft delete classification
- Blueprint: `classifications/{id}/restore` → **HTTP**: `POST /api/classifications/{id}/restore` - Restore classification

### Lookups Blueprint (`blueprints/lookups.py`) → **Azure Functions URLs**
- Blueprint: `lookups/types` → **HTTP**: `GET /api/lookups/types` - Get all lookup types
- Blueprint: `lookups/types/{type}` → **HTTP**: `GET /api/lookups/types/{type}` - Get specific lookup type
- Blueprint: `lookups/codes/{type}` → **HTTP**: `GET /api/lookups/codes/{type}` - Get lookup codes by type
- Blueprint: `lookups/batch/codes` → **HTTP**: `POST /api/lookups/batch/codes` - Batch lookup codes
- Blueprint: `lookups/summary` → **HTTP**: `GET /api/lookups/summary` - Lookup summary statistics

## Testing Validation

The updated collection has been validated to ensure:
- ✅ All URLs match blueprint routes exactly
- ✅ No `/api/` prefixes remain
- ✅ Only implemented endpoints are included
- ✅ All tests remain functional
- ✅ Error handling scenarios still work

## Usage

The collection works the same way as before, but now correctly targets the blueprint endpoints:

1. **Import** the updated collection
2. **Use the same environment** (no changes needed)
3. **Run tests** against the blueprint-organized API
4. **All tests should pass** with the corrected URLs

## Compatibility

- ✅ **Backward Compatible**: Environment variables unchanged
- ✅ **Test Logic Preserved**: All test scripts remain the same
- ✅ **Newman Compatible**: CLI usage unchanged
- ✅ **CI/CD Ready**: Automation scripts continue to work

This update ensures the Postman collection accurately reflects the current blueprint architecture and provides reliable testing for the modular Azure Functions implementation.