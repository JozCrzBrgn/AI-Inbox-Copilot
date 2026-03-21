from fastapi import APIRouter, Depends, Request

from ..middleware.rate_limiter import limiter

#TODO: from ..services.email_analizer import analyze_email
from ..mock.mock_email_analizer import analyze_email
from ..schemas.email_analizer import EmailAnalizerResponse, EmailAnalizerResquest
from ..services.database import save_email
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
    username: str = Depends(get_current_user),
) -> EmailAnalizerResponse:
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
