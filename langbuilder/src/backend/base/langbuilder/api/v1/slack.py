"""Slack Events API endpoint for LangBuilder.

Handles Slack Event Subscriptions including URL verification challenges.
"""

import json
import logging
from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request
from fastapi.responses import JSONResponse

from langbuilder.api.v1.endpoints import simple_run_flow_task
from langbuilder.api.v1.schemas import SimplifiedAPIRequest
from langbuilder.helpers.flow import get_flow_by_id_or_endpoint_name
from langbuilder.helpers.user import get_user_by_flow_id_or_endpoint_name
from langbuilder.services.database.models.flow.model import Flow
from langbuilder.services.database.models.user.model import User
from langbuilder.services.database.models.flow.utils import get_all_webhook_components_in_flow

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/slack", tags=["Slack"])


@router.post("/events/{flow_id_or_name}")
async def slack_events(
    flow: Annotated[Flow, Depends(get_flow_by_id_or_endpoint_name)],
    user: Annotated[User, Depends(get_user_by_flow_id_or_endpoint_name)],
    request: Request,
    background_tasks: BackgroundTasks,
):
    """Handle Slack Event Subscriptions.

    This endpoint handles:
    1. URL verification challenges (responds synchronously)
    2. Event callbacks (processes in background)

    Args:
        flow: The flow to execute for events
        user: The flow owner
        request: The incoming Slack event
        background_tasks: Background task manager

    Returns:
        For url_verification: {"challenge": "<challenge_value>"}
        For events: {"ok": true}
    """
    try:
        body = await request.body()
        data = json.loads(body.decode()) if body else {}
    except json.JSONDecodeError as exc:
        logger.error(f"Invalid JSON in Slack request: {exc}")
        raise HTTPException(status_code=400, detail="Invalid JSON") from exc

    event_type = data.get("type")

    # Handle URL verification challenge (must respond synchronously)
    if event_type == "url_verification":
        challenge = data.get("challenge", "")
        logger.info(f"Slack URL verification challenge received")
        return JSONResponse(
            content={"challenge": challenge},
            status_code=200,
        )

    # Handle event callbacks
    if event_type == "event_callback":
        event = data.get("event", {})
        event_subtype = event.get("type", "unknown")
        logger.info(f"Slack event received: {event_subtype}")

        # Skip bot messages to prevent loops
        if event.get("bot_id") or event.get("subtype") == "bot_message":
            logger.debug("Skipping bot message")
            return {"ok": True, "skipped": "bot_message"}

        # Run the flow in background
        try:
            webhook_components = get_all_webhook_components_in_flow(flow.data)
            tweaks = {}

            for component in webhook_components:
                tweaks[component["id"]] = {"data": json.dumps(data)}

            input_request = SimplifiedAPIRequest(
                input_value="",
                input_type="chat",
                output_type="chat",
                tweaks=tweaks,
                session_id=None,
            )

            background_tasks.add_task(
                simple_run_flow_task,
                flow=flow,
                input_request=input_request,
                api_key_user=user,
            )
        except Exception as exc:
            logger.error(f"Error processing Slack event: {exc}")
            # Still return 200 to Slack to prevent retries
            return {"ok": False, "error": str(exc)}

        return {"ok": True}

    # Unknown event type
    logger.warning(f"Unknown Slack event type: {event_type}")
    return {"ok": True, "unknown_type": event_type}
