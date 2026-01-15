# Data Models

This directory contains database schemas, data models, and data contracts.

## Contents

- Database schemas
- Entity relationship diagrams (ERD)
- Data contracts
- Migration history
- Data validation rules
- Data lifecycle policies

## Maintenance

- Update with every schema change
- All changes require data team review
- Document migration strategies
- Maintain backward compatibility

## Schema Versioning

- Use semantic versioning for schemas
- Document breaking changes
- Provide migration scripts
- Test migrations in staging

## Examples

```
data_model/
  schemas/
    user_schema.sql
    transaction_schema.sql
  erd/
    database_erd.mmd
    entity_relationships.png
  migrations/
    001_initial_schema.sql
    002_add_user_preferences.sql
  contracts/
    api_data_contracts.yaml
```

## Best Practices

- Always use transactions for schema changes
- Test migrations with production-like data
- Document rollback procedures
- Consider data retention policies
