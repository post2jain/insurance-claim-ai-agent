from enum import StrEnum

class ClaimStatus(StrEnum):
    SUBMITTED = "submitted"  # Initial claim submission
    UNDER_REVIEW = "under_review"  # Claim is being reviewed
    ADDITIONAL_INFO_NEEDED = "additional_info_needed"  # More information required
    APPROVED = "approved"  # Claim has been approved
    PARTIALLY_APPROVED = "partially_approved"  # Some items approved, others denied
    DENIED = "denied"  # Claim has been denied
    APPEALED = "appealed"  # Denial is being appealed
    SETTLED = "settled"  # Claim has been settled and payment issued
    CLOSED = "closed"  # Claim process is complete


class SuggestionType(StrEnum):
    APPROVE_CLAIM = "approve_claim"
    DENY_CLAIM = "deny_claim"
    REQUEST_INFO = "request_info"
    FLAG_FRAUD = "flag_fraud"
    ADJUST_AMOUNT = "adjust_amount"
    REPLACE_ITEM = "replace_item"
    REPAIR_ITEM = "repair_item"


class SuggestionStatus(StrEnum):
    PENDING = "pending"  # Awaiting adjuster review
    ACCEPTED = "accepted"  # Adjuster accepted the suggestion
    REJECTED = "rejected"  # Adjuster rejected the suggestion
    MODIFIED = "modified"  # Adjuster modified and then accepted
