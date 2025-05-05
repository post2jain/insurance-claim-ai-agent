# Insurance Claims Processing Platform - User Guide

## Introduction

This guide will help you understand how to use the Insurance Claims Processing Platform effectively. The platform provides a streamlined process for handling insurance claims with AI-powered suggestions and video analysis capabilities.

## Getting Started

### Prerequisites
- API access credentials
- Basic understanding of REST APIs
- Video files in supported formats (MP4, QuickTime, AVI, MKV)

### API Base URL
```
https://api.insurance-claims.com/v1
```

## Claim Management

### 1. Creating a New Claim

To create a new insurance claim:

```http
POST /claims
Content-Type: application/json

{
    "policy_number": "POL123",
    "policyholder_name": "John Doe",
    "loss_date": "2024-03-15T10:30:00Z",
    "loss_description": "Water damage in kitchen",
    "loss_amount": 5000.00,
    "incident_location": "123 Main St"
}
```

Response:
```json
{
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "status": "SUBMITTED",
    "created_at": "2024-03-15T10:35:00Z",
    "updated_at": "2024-03-15T10:35:00Z",
    ...
}
```

### 2. Viewing Claims

#### List All Claims
```http
GET /claims
```

Optional filters:
- `status`: Filter by claim status
- `policyholder_name`: Search by name
- `limit`: Number of results (default: 100)
- `offset`: Pagination offset

#### Get Specific Claim
```http
GET /claims/{claim_id}
```

### 3. Updating a Claim
```http
PATCH /claims/{claim_id}
Content-Type: application/json

{
    "status": "UNDER_REVIEW",
    "loss_amount": 6000.00
}
```

## Video Upload and Analysis

### 1. Uploading a Video

```http
POST /claims/{claim_id}/upload_video
Content-Type: multipart/form-data

file: [video_file]
```

Supported formats:
- MP4
- QuickTime
- AVI
- MKV

Limits:
- Maximum file size: 100MB
- Maximum duration: 5 minutes

### 2. Understanding Video Analysis

After upload, the system will:
1. Validate the video
2. Analyze content using AI
3. Generate suggestions
4. Update claim with analysis results

## AI Suggestions

### 1. Generating Suggestions

```http
POST /suggestions/claims/{claim_id}/suggestions
```

This will generate AI-powered suggestions based on:
- Claim details
- Policy information
- Video analysis (if available)

### 2. Viewing Suggestions

#### List All Suggestions for a Claim
```http
GET /suggestions/claims/{claim_id}/suggestions
```

Optional filter:
- `status`: Filter by suggestion status

#### Get Specific Suggestion
```http
GET /suggestions/{suggestion_id}
```

### 3. Reviewing Suggestions

```http
POST /suggestions/{suggestion_id}/review
Content-Type: application/json

{
    "status": "ACCEPTED",
    "reviewer_id": "user123",
    "reviewer_notes": "Looks good",
    "modified_action": null
}
```

Review options:
- `ACCEPTED`: Accept as-is
- `REJECTED`: Reject the suggestion
- `MODIFIED`: Accept with modifications

### 4. Viewing Suggestion Metrics

```http
GET /suggestions/metrics
```

Returns:
- Total suggestions
- Acceptance rate
- Rejection rate
- Modification rate
- Suggestions by type

## Best Practices

### 1. Claim Submission
- Provide detailed loss descriptions
- Include accurate policy information
- Upload clear video evidence when available

### 2. Video Upload
- Use supported formats
- Keep videos under 5 minutes
- Ensure good lighting and clarity
- Focus on damage areas

### 3. Suggestion Review
- Review all suggestions promptly
- Provide clear feedback
- Use modification option when needed
- Document review decisions

## Error Handling

### Common Error Codes
- `400`: Bad Request - Invalid input
- `404`: Not Found - Resource doesn't exist
- `413`: Payload Too Large - Video too big
- `415`: Unsupported Media Type - Invalid video format
- `500`: Internal Server Error - System issue

### Error Response Format
```json
{
    "detail": "Error message",
    "code": "ERROR_CODE"
}
```

## Rate Limits

- 100 requests per minute per API key
- 10 video uploads per hour per claim
- 50 suggestion generations per hour per claim

## Support

For technical support:
- Email: support@insurance-claims.com
- Phone: 1-800-CLAIMS
- Documentation: docs.insurance-claims.com

## Security Guidelines

1. **API Key Management**
   - Keep API keys secure
   - Rotate keys regularly
   - Use different keys for different environments

2. **Data Protection**
   - Don't share claim IDs publicly
   - Secure video storage
   - Follow data retention policies

3. **Access Control**
   - Use appropriate user roles
   - Implement proper authentication
   - Monitor API usage

## Troubleshooting

### Common Issues

1. **Video Upload Fails**
   - Check file format
   - Verify file size
   - Ensure stable connection

2. **Suggestions Not Generated**
   - Verify claim status
   - Check video analysis results
   - Ensure sufficient claim details

3. **API Errors**
   - Validate request format
   - Check rate limits
   - Verify API key

### Getting Help
- Check error messages
- Review documentation
- Contact support
- Check system status page 