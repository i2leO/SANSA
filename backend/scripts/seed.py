#!/usr/bin/env python3
"""
Seed script to initialize the database with:
- Default admin user
- Default SANSA scoring version
- Default MNA scoring version
- Sample facilities
"""

import sys
import os
from datetime import date

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.database import SessionLocal
from app.models import User, ScoringRuleVersion, ScoringRuleValue, Facility
from app.auth import get_password_hash
from app.config import get_settings

settings = get_settings()


def seed_database():
    db = SessionLocal()
    
    try:
        print("🌱 Seeding database...")
        
        # 1. Create default admin user
        admin_username = os.getenv("ADMIN_USERNAME", "admin")
        admin_password = os.getenv("ADMIN_PASSWORD", "admin123")
        admin_email = os.getenv("ADMIN_EMAIL", "admin@sansa.local")
        
        existing_admin = db.query(User).filter(User.username == admin_username).first()
        if not existing_admin:
            admin_user = User(
                username=admin_username,
                email=admin_email,
                hashed_password=get_password_hash(admin_password),
                full_name="System Administrator",
                role="admin",
                is_active=True
            )
            db.add(admin_user)
            db.commit()
            print(f"✓ Created admin user: {admin_username}")
        else:
            print(f"✓ Admin user already exists: {admin_username}")
            admin_user = existing_admin
        
        # 2. Create SANSA scoring version
        sansa_version = db.query(ScoringRuleVersion).filter(
            ScoringRuleVersion.instrument_name == "SANSA",
            ScoringRuleVersion.version_number == "1.0"
        ).first()
        
        if not sansa_version:
            sansa_version = ScoringRuleVersion(
                instrument_name="SANSA",
                version_number="1.0",
                version_name="SANSA v1.0 - Default Thresholds",
                description="Default scoring thresholds for SANSA instrument",
                is_active=True,
                effective_date=date.today(),
                created_by=admin_user.id
            )
            db.add(sansa_version)
            db.flush()
            
            # Create classification levels for SANSA
            # Total score range: 0-52 (4 screening + 12 dietary items, max 4 points each)
            sansa_levels = [
                {
                    "level_code": "normal",
                    "level_name": "Normal Nutritional Status",
                    "min_score": 37,
                    "max_score": 52,
                    "level_order": 1,
                    "advice_text": "Your nutritional status is good. Continue maintaining a balanced diet and healthy lifestyle."
                },
                {
                    "level_code": "at_risk",
                    "level_name": "At Risk of Malnutrition",
                    "min_score": 24,
                    "max_score": 36,
                    "level_order": 2,
                    "advice_text": "You may be at risk of malnutrition. Consider consulting with a healthcare provider or nutritionist for personalized advice."
                },
                {
                    "level_code": "malnourished",
                    "level_name": "Malnourished",
                    "min_score": 0,
                    "max_score": 23,
                    "level_order": 3,
                    "advice_text": "Your screening indicates possible malnutrition. Please consult with a healthcare provider for further assessment and intervention."
                }
            ]
            
            for level_data in sansa_levels:
                level = ScoringRuleValue(
                    version_id=sansa_version.id,
                    **level_data
                )
                db.add(level)
            
            db.commit()
            print("✓ Created SANSA scoring version with thresholds")
        else:
            print("✓ SANSA scoring version already exists")
        
        # 3. Create MNA scoring version
        mna_version = db.query(ScoringRuleVersion).filter(
            ScoringRuleVersion.instrument_name == "MNA",
            ScoringRuleVersion.version_number == "1.0"
        ).first()
        
        if not mna_version:
            mna_version = ScoringRuleVersion(
                instrument_name="MNA",
                version_number="1.0",
                version_name="MNA v1.0 - Standard Thresholds",
                description="Standard MNA scoring thresholds",
                is_active=True,
                effective_date=date.today(),
                created_by=admin_user.id
            )
            db.add(mna_version)
            db.flush()
            
            # Create classification levels for MNA
            # MNA total score range: 0-30
            mna_levels = [
                {
                    "level_code": "normal",
                    "level_name": "Normal Nutritional Status",
                    "min_score": 24,
                    "max_score": 30,
                    "level_order": 1,
                    "advice_text": "Normal nutritional status. Continue with current diet and lifestyle."
                },
                {
                    "level_code": "at_risk",
                    "level_name": "At Risk of Malnutrition",
                    "min_score": 17,
                    "max_score": 23.5,
                    "level_order": 2,
                    "advice_text": "At risk of malnutrition. Consider nutritional counseling."
                },
                {
                    "level_code": "malnourished",
                    "level_name": "Malnourished",
                    "min_score": 0,
                    "max_score": 16.5,
                    "level_order": 3,
                    "advice_text": "Malnourished. Medical nutrition therapy recommended."
                }
            ]
            
            for level_data in mna_levels:
                level = ScoringRuleValue(
                    version_id=mna_version.id,
                    **level_data
                )
                db.add(level)
            
            db.commit()
            print("✓ Created MNA scoring version with thresholds")
        else:
            print("✓ MNA scoring version already exists")
        
        # 4. Create sample facilities
        facility_count = db.query(Facility).count()
        if facility_count == 0:
            sample_facilities = [
                {
                    "name": "Central Community Health Center",
                    "code": "CCHC001",
                    "type": "Community Health Center",
                    "description": "Primary healthcare services for the community",
                    "address": "123 Main Street, Bangkok 10100",
                    "phone": "02-123-4567",
                    "is_active": True,
                    "display_order": 1,
                    "created_by": admin_user.id
                },
                {
                    "name": "University Hospital Nutrition Clinic",
                    "code": "UHNC001",
                    "type": "Hospital Clinic",
                    "description": "Specialized nutrition assessment and counseling",
                    "address": "456 University Ave, Bangkok 10120",
                    "phone": "02-234-5678",
                    "is_active": True,
                    "display_order": 2,
                    "created_by": admin_user.id
                }
            ]
            
            for facility_data in sample_facilities:
                facility = Facility(**facility_data)
                db.add(facility)
            
            db.commit()
            print(f"✓ Created {len(sample_facilities)} sample facilities")
        else:
            print(f"✓ Facilities already exist ({facility_count} found)")
        
        print("\n✅ Database seeding completed successfully!")
        print(f"\n📝 Admin credentials:")
        print(f"   Username: {admin_username}")
        print(f"   Password: {admin_password}")
        print(f"\n🔗 You can now start the server and login at /docs")
        
    except Exception as e:
        print(f"\n❌ Error seeding database: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
