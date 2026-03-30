"""Health check endpoint for Vercel serverless function."""

import json


def handler(request):
    """Return API health status."""
    return {
        "statusCode": 200,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps({
            "status": "healthy",
            "service": "ZzARA Dream Maker",
            "version": "1.0.0",
        }),
    }
