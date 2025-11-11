# Quick script to add zone columns manually
# Run this in Django shell: python manage.py shell < ADD_ZONE_COLUMNS_MANUAL.py

from django.db import connection

with connection.cursor() as cursor:
    # Add zone_type column
    try:
        cursor.execute("""
            ALTER TABLE projeng_project 
            ADD COLUMN zone_type VARCHAR(20) NULL;
        """)
        print("✓ Added zone_type column")
    except Exception as e:
        if 'already exists' in str(e).lower() or 'duplicate' in str(e).lower():
            print("✓ zone_type column already exists")
        else:
            print(f"Error adding zone_type: {e}")
    
    # Add zone_validated column
    try:
        cursor.execute("""
            ALTER TABLE projeng_project 
            ADD COLUMN zone_validated BOOLEAN DEFAULT FALSE;
        """)
        print("✓ Added zone_validated column")
    except Exception as e:
        if 'already exists' in str(e).lower() or 'duplicate' in str(e).lower():
            print("✓ zone_validated column already exists")
        else:
            print(f"Error adding zone_validated: {e}")
    
    # Create ZoningZone table if it doesn't exist
    try:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS projeng_zoningzone (
                id BIGSERIAL PRIMARY KEY,
                zone_type VARCHAR(20) NOT NULL,
                barangay VARCHAR(255) NOT NULL,
                location_description TEXT NOT NULL,
                keywords JSONB DEFAULT '[]'::jsonb,
                is_active BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            );
        """)
        print("✓ Created projeng_zoningzone table")
    except Exception as e:
        print(f"Note: {e}")
    
    # Create indexes
    try:
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS projeng_zon_baranga_8c8025_idx 
            ON projeng_zoningzone(barangay, zone_type);
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS projeng_zon_is_acti_1819c4_idx 
            ON projeng_zoningzone(is_active);
        """)
        print("✓ Created indexes")
    except Exception as e:
        print(f"Note: {e}")

print("\n✅ Done! Now run: python manage.py migrate --fake projeng 0014")

