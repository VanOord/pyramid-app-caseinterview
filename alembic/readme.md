# How to use alembic

1. Generate update with:

   `alembic revision --autogenerate -m "v1.0.0"`
    
1. Check warnings and manually edit migration file.

2. Apply the update with:
    
   `alembic upgrade head`

    Alternatively point to specific version:

    `alembic upgrade c2dbbd712751`

