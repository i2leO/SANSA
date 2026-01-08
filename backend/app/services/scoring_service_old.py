from decimal import Decimal
from typing import Optional, Dict, List
from sqlalchemy.orm import Session
from app.models import ScoringRuleVersion, ScoringRuleValue
from app.schemas import SANSAItemInput, MNAItemInput


class ScoringService:
    """Service for calculating scores and classifications"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_active_scoring_version(self, instrument_name: str) -> Optional[ScoringRuleVersion]:
        """Get the currently active scoring version for an instrument"""
        return self.db.query(ScoringRuleVersion).filter(
            ScoringRuleVersion.instrument_name == instrument_name,
            ScoringRuleVersion.is_active == True
        ).order_by(ScoringRuleVersion.created_at.desc()).first()
    
    def get_scoring_version(self, version_id: int) -> Optional[ScoringRuleVersion]:
        """Get a specific scoring version by ID"""
        return self.db.query(ScoringRuleVersion).filter(
            ScoringRuleVersion.id == version_id
        ).first()
    
    def get_classification_level(
        self, 
        version_id: int, 
        total_score: Decimal
    ) -> Optional[str]:
        """Determine classification level based on score and thresholds"""
        rule_values = self.db.query(ScoringRuleValue).filter(
            ScoringRuleValue.version_id == version_id
        ).order_by(ScoringRuleValue.level_order).all()
        
        for rule_value in rule_values:
            # Handle different threshold configurations
            if rule_value.min_score is not None and rule_value.max_score is not None:
                if rule_value.min_score <= total_score <= rule_value.max_score:
                    return rule_value.level_code
            elif rule_value.min_score is not None:
                if total_score >= rule_value.min_score:
                    return rule_value.level_code
            elif rule_value.max_score is not None:
                if total_score <= rule_value.max_score:
                    return rule_value.level_code
        
        return None
    
    def get_advice_text(self, version_id: int, level_code: str) -> Optional[str]:
        """Get advice text for a classification level"""
        rule_value = self.db.query(ScoringRuleValue).filter(
            ScoringRuleValue.version_id == version_id,
            ScoringRuleValue.level_code == level_code
        ).first()
        
        return rule_value.advice_text if rule_value else None
    
    def calculate_sansa_scores(
        self, 
        items: List[SANSAItemInput],
        version_id: Optional[int] = None
    ) -> Dict:
        """
        Calculate SANSA screening, dietary, and total scores
        
        Args:
            items: List of SANSA item responses
            version_id: Optional specific version ID (uses active if not provided)
        
        Returns:
            Dict with screening_total, diet_total, total_score, result_level, version_id
        """
        if version_id is None:
            version = self.get_active_scoring_version("SANSA")
            if not version:
                raise ValueError("No active SANSA scoring version found")
            version_id = version.id
        
        # Calculate subscore totals
        screening_total = Decimal('0')
        diet_total = Decimal('0')
        
        for item in items:
            if item.item_type == "screening":
                screening_total += Decimal(str(item.item_score))
            elif item.item_type == "dietary":
                diet_total += Decimal(str(item.item_score))
        
        # Calculate overall total score
        total_score = screening_total + diet_total
        
        # Determine classification level
        result_level = self.get_classification_level(version_id, total_score)
        
        return {
            "screening_total": screening_total,
            "diet_total": diet_total,
            "total_score": total_score,
            "result_level": result_level,
            "scoring_version_id": version_id
        }
    
    def calculate_mna_score(
        self,
        items: List[MNAItemInput],
        version_id: Optional[int] = None
    ) -> Dict:
        """
        Calculate MNA total score and category
        
        Args:
            items: List of MNA item responses
            version_id: Optional specific version ID (uses active if not provided)
        
        Returns:
            Dict with total_score, result_category, version_id
        """
        if version_id is None:
            version = self.get_active_scoring_version("MNA")
            if not version:
                raise ValueError("No active MNA scoring version found")
            version_id = version.id
        
        # Calculate total score
        total_score = Decimal('0')
        for item in items:
            total_score += Decimal(str(item.item_score))
        
        # Determine category
        result_category = self.get_classification_level(version_id, total_score)
        
        return {
            "total_score": total_score,
            "result_category": result_category,
            "scoring_version_id": version_id
        }
    
    def calculate_bmi(self, weight_kg: Decimal, height_cm: Decimal) -> Decimal:
        """Calculate BMI from weight and height"""
        if weight_kg and height_cm and height_cm > 0:
            height_m = height_cm / 100
            bmi = weight_kg / (height_m * height_m)
            return round(bmi, 2)
        return None
    
    def calculate_waist_hip_ratio(
        self, 
        waist_cm: Decimal, 
        hip_cm: Decimal
    ) -> Optional[Decimal]:
        """Calculate waist-to-hip ratio"""
        if waist_cm and hip_cm and hip_cm > 0:
            ratio = waist_cm / hip_cm
            return round(ratio, 3)
        return None
