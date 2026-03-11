"""Request Validation Example."""
from engineering_framework.backend.request_validation.core import SchemaValidator, FieldRule

validator = SchemaValidator([
    FieldRule("email", required=True, pattern=r".+@.+\..+"),
    FieldRule("name", required=True, min_length=2, max_length=100),
    FieldRule("age", field_type=int),
])

result = validator.validate({"email": "alice@example.com", "name": "Alice", "age": 30})
print(f"Valid: {result.valid}, Errors: {result.errors}")

result2 = validator.validate({"email": "bad-email", "name": "A"})
print(f"Valid: {result2.valid}, Errors: {result2.errors}")
