# Insurance Claims Processing Platform API Documentation

## Overview

The Insurance Claims Processing Platform API provides endpoints for managing insurance claims, generating AI-powered suggestions, and processing video evidence. The API follows RESTful principles and uses FastAPI for implementation.

## Base URL

```
http://localhost:8000/api/v1
```

## Authentication

All endpoints require authentication using API keys. Include the API key in the request header:

```
Authorization: Bearer <your-api-key>
```

## API Endpoints

### Claims API

#### Create Claim
```http
POST /claims
```

Creates a new insurance claim.

**Request Body:**
```json
{
  "policy_number": "string",
  "policyholder_name": "string",
  "incident_date": "2024-03-20T00:00:00Z",
  "incident_description": "string",
  "incident_location": "string",
  "claim_items": [
    {
      "item_name": "string",
      "item_description": "string",
      "item_value": 0.0
    }
  ]
}
```

**Response:** `201 Created`
```json
{
  "id": "uuid",
  "policy_number": "string",
  "status": "SUBMITTED",
  "created_at": "2024-03-20T00:00:00Z",
  "updated_at": "2024-03-20T00:00:00Z"
}
```

#### Get Claim
```http
GET /claims/{claim_id}
```

Retrieves a specific claim by ID.

**Response:** `200 OK`
```json
{
  "id": "uuid",
  "policy_number": "string",
  "status": "string",
  "created_at": "2024-03-20T00:00:00Z",
  "updated_at": "2024-03-20T00:00:00Z"
}
```

#### List Claims
```http
GET /claims
```

Retrieves a list of claims with optional filtering.

**Query Parameters:**
- `skip` (integer, optional): Number of records to skip
- `limit` (integer, optional): Maximum number of records to return
- `status` (string, optional): Filter by claim status
- `policy_number` (string, optional): Filter by policy number
- `policyholder_name` (string, optional): Filter by policyholder name

**Response:** `200 OK`
```json
[
  {
    "id": "uuid",
    "policy_number": "string",
    "status": "string",
    "created_at": "2024-03-20T00:00:00Z",
    "updated_at": "2024-03-20T00:00:00Z"
  }
]
```

#### Update Claim
```http
PUT /claims/{claim_id}
```

Updates an existing claim.

**Request Body:**
```json
{
  "policy_number": "string",
  "policyholder_name": "string",
  "incident_description": "string"
}
```

**Response:** `200 OK`
```json
{
  "id": "uuid",
  "policy_number": "string",
  "status": "string",
  "updated_at": "2024-03-20T00:00:00Z"
}
```

#### Delete Claim
```http
DELETE /claims/{claim_id}
```

Deletes a claim.

**Response:** `200 OK`
```json
{
  "message": "Claim deleted successfully"
}
```

#### Update Claim Status
```http
PATCH /claims/{claim_id}/status
```

Updates the status of a claim.

**Request Body:**
```json
{
  "status": "APPROVED"
}
```

**Response:** `200 OK`
```json
{
  "id": "uuid",
  "status": "APPROVED",
  "updated_at": "2024-03-20T00:00:00Z"
}
```

#### Upload Video
```http
POST /claims/{claim_id}/video
```

Uploads and processes a video for a claim.

**Request Body:**
- `video` (file): Video file (MP4, QuickTime, AVI, MKV)
- Maximum file size: 100MB
- Maximum duration: 5 minutes

**Response:** `201 Created`
```json
{
  "message": "Video processed successfully",
  "analysis": {
    "damage_assessment": "string",
    "confidence_score": 0.95,
    "recommendations": ["string"]
  }
}
```

### Suggestions API

#### Create Suggestion
```http
POST /suggestions
```

Creates a new AI suggestion.

**Request Body:**
```json
{
  "claim_id": "uuid",
  "type": "FRAUD_DETECTION",
  "suggested_action": "string",
  "confidence_score": 0.95,
  "explanation": "string"
}
```

**Response:** `201 Created`
```json
{
  "id": "uuid",
  "claim_id": "uuid",
  "type": "string",
  "status": "PENDING",
  "created_at": "2024-03-20T00:00:00Z"
}
```

#### Get Suggestion
```http
GET /suggestions/{suggestion_id}
```

Retrieves a specific suggestion by ID.

**Response:** `200 OK`
```json
{
  "id": "uuid",
  "claim_id": "uuid",
  "type": "string",
  "status": "string",
  "created_at": "2024-03-20T00:00:00Z"
}
```

#### List Suggestions
```http
GET /suggestions
```

Retrieves a list of suggestions with optional filtering.

**Query Parameters:**
- `claim_id` (uuid, optional): Filter by claim ID
- `status` (string, optional): Filter by suggestion status
- `type` (string, optional): Filter by suggestion type

**Response:** `200 OK`
```json
[
  {
    "id": "uuid",
    "claim_id": "uuid",
    "type": "string",
    "status": "string",
    "created_at": "2024-03-20T00:00:00Z"
  }
]
```

#### Update Suggestion
```http
PUT /suggestions/{suggestion_id}
```

Updates an existing suggestion.

**Request Body:**
```json
{
  "suggested_action": "string",
  "confidence_score": 0.95,
  "explanation": "string"
}
```

**Response:** `200 OK`
```json
{
  "id": "uuid",
  "suggested_action": "string",
  "updated_at": "2024-03-20T00:00:00Z"
}
```

#### Update Suggestion Status
```http
PATCH /suggestions/{suggestion_id}/status
```

Updates the status of a suggestion.

**Request Body:**
```json
{
  "status": "ACCEPTED",
  "reviewer_id": "uuid",
  "reviewer_notes": "string",
  "modified_action": "string"
}
```

**Response:** `200 OK`
```json
{
  "id": "uuid",
  "status": "ACCEPTED",
  "reviewed_at": "2024-03-20T00:00:00Z"
}
```

#### Get Suggestion Metrics
```http
GET /suggestions/metrics
```

Retrieves metrics about suggestions.

**Response:** `200 OK`
```json
{
  "total_suggestions": 100,
  "acceptance_rate": 0.75,
  "rejection_rate": 0.15,
  "modification_rate": 0.10,
  "suggestions_by_type": [
    ["FRAUD_DETECTION", 50],
    ["DAMAGE_ASSESSMENT", 30],
    ["SETTLEMENT_RECOMMENDATION", 20]
  ]
}
```

#### Get High Confidence Suggestions
```http
GET /suggestions/high-confidence
```

Retrieves suggestions with confidence score above threshold.

**Query Parameters:**
- `threshold` (float, optional): Confidence score threshold (default: 0.8)

**Response:** `200 OK`
```json
[
  {
    "id": "uuid",
    "claim_id": "uuid",
    "type": "string",
    "confidence_score": 0.95
  }
]
```

#### Regenerate Suggestions
```http
POST /suggestions/{claim_id}/regenerate
```

Regenerates AI suggestions for a claim.

**Response:** `200 OK`
```json
[
  {
    "id": "uuid",
    "claim_id": "uuid",
    "type": "string",
    "status": "PENDING"
  }
]
```

## Error Responses

All endpoints may return the following error responses:

### 400 Bad Request
```json
{
  "detail": "Invalid request parameters"
}
```

### 401 Unauthorized
```json
{
  "detail": "Invalid API key"
}
```

### 404 Not Found
```json
{
  "detail": "Resource not found"
}
```

### 500 Internal Server Error
```json
{
  "detail": "Internal server error"
}
```

## Rate Limiting

The API implements rate limiting:
- 100 requests per minute per API key
- Rate limit headers included in responses:
  - `X-RateLimit-Limit`
  - `X-RateLimit-Remaining`
  - `X-RateLimit-Reset` 