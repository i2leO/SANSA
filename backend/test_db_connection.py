"""
Test database connection script
"""

import sys
from sqlalchemy import create_engine, text
from app.config import get_settings


def test_connection():
    settings = get_settings()
    print(
        f"🔍 Testing connection to: {settings.DATABASE_URL.replace('password', '****')}"
    )

    try:
        # Create engine
        engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True)

        # Test connection
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            result.fetchone()
            print("✅ Database connection successful!")

            # Check database exists
            result = connection.execute(text("SELECT DATABASE()"))
            db_name = result.fetchone()[0]
            print(f"✅ Connected to database: {db_name}")

            # List tables
            result = connection.execute(
                text(
                    """
                SELECT TABLE_NAME
                FROM information_schema.TABLES
                WHERE TABLE_SCHEMA = DATABASE()
            """
                )
            )
            tables = [row[0] for row in result.fetchall()]

            if tables:
                print(f"✅ Found {len(tables)} tables:")
                for table in tables:
                    print(f"   - {table}")
            else:
                print("⚠️  No tables found (database is empty)")

            return True

    except Exception as e:
        print(f"❌ Connection failed: {str(e)}")
        print("\n💡 Troubleshooting tips:")
        print("   1. Check if MAMP MySQL is running")
        print("   2. Verify MySQL port (default MAMP: 8889 or 3306)")
        print("   3. Check username/password in config.py")
        print("   4. Ensure database 'sansa_db' exists")
        return False


if __name__ == "__main__":
    success = test_connection()
    sys.exit(0 if success else 1)
