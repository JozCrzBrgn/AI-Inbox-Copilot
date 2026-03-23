from typing import Annotated, List

from fastapi import APIRouter, Depends, Request

#TODO: from ..services.email_analizer import analyze_email
from mocks.mock_email_analizer import analyze_email

from ..middleware.rate_limiter import limiter
from ..schemas.email_analizer import (
    EmailAnalizerResponse,
    EmailAnalizerResquest,
    EmailResponse,
)
from ..services.database import get_all_emails, save_email
from ..services.dependencies import get_current_user
from ..services.slack import send_slack_alert

router = APIRouter()


@router.post(
    "/analyze",
    response_model=EmailAnalizerResponse,
    summary="API that automatically analyzes emails to prioritize responses in CS teams.",
    description="API to automatically analyze emails and help Customer Service (CS) teams prioritize and respond faster",
    tags=["Email analyzer"],
)
@limiter.limit("2/minute")
async def analyze_email_endpoint(
    request: Request,
    payload: EmailAnalizerResquest,
    username: Annotated[str, Depends(get_current_user)],
):
    """
    Analyze a customer support email using AI.

    This endpoint processes an email content and returns structured insights
    including customer information, intent, priority, sentiment, and suggested
    replies to help customer service teams respond faster and more effectively.

    Args:
        request (Request): The HTTP request object (used for rate limiting).
        payload (EmailAnalizerResquest): Request body containing the email content to analyze.
        username (str): Authenticated username from JWT token (via dependency injection).

    Returns:
        EmailAnalizerResponse: Structured analysis of the email containing:
            - customer_name: Name of the customer (extracted)
            - intent: Main purpose of the email (e.g., complaint, refund, question)
            - summary: Brief 2-3 sentence summary
            - priority: Priority level (low, medium, high)
            - sentiment: Emotional tone (positive, neutral, negative)
            - suggested_subject: Recommended email subject line
            - suggested_reply: Draft response for the CS agent

    Notes:
        - Rate limited to 2 requests per minute per user
        - High priority emails trigger Slack alerts (if configured)
        - Uses few-shot examples for better accuracy
        - Results are automatically saved to PostgreSQL database
    """

    # Analyze email with OpenAI
    result = analyze_email(email_content=payload.email_content, use_examples=True)

    # Save in PostgreSQL
    save_email(
        customer_name=result["customer_name"],
        intent=result["intent"],
        priority=result["priority"],
        sentiment=result["sentiment"],
        summary=result["summary"],
        reply=result["suggested_reply"]
    )

    # Send alert to Slack if it's high priority
    if result["priority"].lower() == "high":
        send_slack_alert(result)
    
    # Build response with metadata
    return result


@router.get(
    "/emails",
    response_model=List[EmailResponse],
    summary="Retrieve all analyzed emails from history",
    description="Get all emails that have been analyzed and stored in the database, ordered by most recent",
    tags=["Email analyzer"],
)
@limiter.limit("2/minute")
async def get_all_emails_endpoint(
    request: Request,
    username: Annotated[str, Depends(get_current_user)],
):
    """
    Retrieve all analyzed emails from the database.

    This endpoint returns all emails that have been previously analyzed,
    including their analysis results (priority, sentiment, intent, etc.).
    Results are ordered by most recent first.

    Args:
        username (str): Authenticated username from JWT token (via dependency injection).

    Returns:
        List[EmailResponse]: List of all emails with:
            - id: Email ID in database
            - date: Analysis timestamp
            - customer_name: Customer name extracted from email
            - intent: Main intent of the email
            - priority: Priority level (low, medium, high)
            - sentiment: Sentiment analysis result (positive, neutral, negative)
            - summary: Summary of the email
            - reply: Suggested reply

    Notes:
        - Rate limited to 2 requests per minute per user
        - Requires authentication via JWT token
        - Results are ordered by date (most recent first)
    """
    return get_all_emails()
