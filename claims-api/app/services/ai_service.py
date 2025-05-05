from typing import List, Dict, Any
from datetime import datetime
import uuid
import os
import json
from openai import OpenAI
from app.models.schemas import Claim, AISuggestion
from app.models.enums import SuggestionType, SuggestionStatus

class AIService:
    def __init__(self):
        # Initialize OpenAI client
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model_version = "gpt-4-turbo-preview"
        
    def analyze_claim(self, claim: Claim) -> List[AISuggestion]:
        """
        Analyze a claim and generate AI suggestions using OpenAI.
        """
        # Prepare claim data for the AI
        claim_data = {
            "policy_number": claim.policy_number,
            "policyholder_name": claim.policyholder_name,
            "date_of_loss": claim.date_of_loss.isoformat(),
            "description": claim.description,
            "total_amount": claim.total_amount,
            "incident_location": claim.incident_location,
            "items": [
                {
                    "name": item.name,
                    "description": item.description,
                    "category": item.category,
                    "estimated_value": item.estimated_value,
                    "purchase_date": item.purchase_date.isoformat() if item.purchase_date else None,
                    "replacement_cost": item.replacement_cost
                }
                for item in claim.items
            ]
        }
        # Include video analysis if available
        if getattr(claim, 'ml_processing_results', None):
            claim_data['video_analysis'] = claim.ml_processing_results
        
        # Create the system prompt
        system_prompt = """You are an expert insurance claims analyst. Analyze the provided claim data and generate detailed suggestions.
        Consider the following aspects:
        1. Claim amount and policy history
        2. Potential fraud indicators
        3. Individual item analysis
        4. Overall claim recommendation
        If 'video_analysis' field is provided, incorporate those findings into your suggestions.
        
        For each suggestion, provide:
        - Type of suggestion (approve_claim, deny_claim, adjust_amount, flag_fraud, replace_item, repair_item)
        - Description
        - Confidence score (0.0 to 1.0)
        - Detailed explanation
        - Specific suggested action
        
        Format your response as a JSON array of suggestions."""

        try:
            # Call OpenAI API
            response = self.client.chat.completions.create(
                model=self.model_version,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": json.dumps(claim_data, indent=2)}
                ],
                temperature=0.3,  # Lower temperature for more consistent results
                response_format={"type": "json_object"}
            )
            
            # Parse the AI response
            ai_suggestions = json.loads(response.choices[0].message.content)
            
            # Convert AI suggestions to AISuggestion objects
            suggestions = []
            for suggestion_data in ai_suggestions["suggestions"]:
                suggestion = AISuggestion(
                    id=uuid.uuid4(),
                    claim_id=claim.id,
                    type=SuggestionType(suggestion_data["type"]),
                    description=suggestion_data["description"],
                    confidence_score=float(suggestion_data["confidence_score"]),
                    ai_explanation=suggestion_data["explanation"],
                    suggested_action=suggestion_data["suggested_action"],
                    status=SuggestionStatus.PENDING,
                    created_at=datetime.utcnow(),
                    model_version=self.model_version
                )
                suggestions.append(suggestion)
            
            return suggestions
            
        except Exception as e:
            # Fallback to rule-based analysis if AI fails
            return self._fallback_analysis(claim)
    
    def _fallback_analysis(self, claim: Claim) -> List[AISuggestion]:
        """Fallback to rule-based analysis if AI service fails"""
        suggestions = []
        
        # Basic amount analysis
        if claim.total_amount > 10000:
            suggestions.append(AISuggestion(
                id=uuid.uuid4(),
                claim_id=claim.id,
                type=SuggestionType.ADJUST_AMOUNT,
                description="High-value claim detected",
                confidence_score=0.85,
                ai_explanation="Claim amount exceeds normal threshold",
                suggested_action={
                    "action": "review",
                    "reason": "high_value",
                    "threshold": 10000,
                    "current_amount": claim.total_amount
                },
                status=SuggestionStatus.PENDING,
                created_at=datetime.utcnow(),
                model_version="fallback-v1"
            ))
        
        # Basic fraud check
        if claim.total_amount > 50000 or len(claim.items) > 10:
            suggestions.append(AISuggestion(
                id=uuid.uuid4(),
                claim_id=claim.id,
                type=SuggestionType.FLAG_FRAUD,
                description="Potential fraud indicators detected",
                confidence_score=0.75,
                ai_explanation="Unusual claim characteristics detected",
                suggested_action={
                    "action": "investigate",
                    "indicators": ["high_amount" if claim.total_amount > 50000 else "excessive_items"],
                    "risk_level": "medium"
                },
                status=SuggestionStatus.PENDING,
                created_at=datetime.utcnow(),
                model_version="fallback-v1"
            ))
        
        # Basic overall recommendation
        suggestions.append(AISuggestion(
            id=uuid.uuid4(),
            claim_id=claim.id,
            type=SuggestionType.APPROVE_CLAIM,
            description="Basic claim recommendation",
            confidence_score=0.80,
            ai_explanation="Initial review suggests approval pending detailed analysis",
            suggested_action={
                "action": "approve",
                "total_amount": claim.total_amount
            },
            status=SuggestionStatus.PENDING,
            created_at=datetime.utcnow(),
            model_version="fallback-v1"
        ))
        
        return suggestions 