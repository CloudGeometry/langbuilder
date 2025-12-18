"""
HubSpot Note Creator - LangBuilder Custom Component

Creates NOTE engagements in HubSpot CRM, associating AI-generated
email drafts with contact records.

Author: CloudGeometry
Project: Carter's Agents - Email Copywriter
"""

from langbuilder.custom import Component
from langbuilder.io import StrInput, SecretStrInput, Output
from langbuilder.schema import Data
import httpx
import time


class HubSpotNoteCreator(Component):
    """
    Creates a NOTE in HubSpot contact timeline with AI-generated email draft.

    This component is used by the Email Copywriter agent to save generated
    email drafts to HubSpot so sales reps can review and send them.
    """

    display_name = "HubSpot Note Creator"
    description = "Creates a NOTE in HubSpot contact timeline with AI-generated email draft"
    icon = "mail"
    name = "HubSpotNoteCreator"

    inputs = [
        SecretStrInput(
            name="hubspot_api_key",
            display_name="HubSpot API Key",
            required=True,
            info="HubSpot Private App API key with crm.objects.contacts.write scope"
        ),
        StrInput(
            name="contact_id",
            display_name="Contact ID",
            required=True,
            info="HubSpot contact ID to associate the note with"
        ),
        StrInput(
            name="subject_line",
            display_name="Subject Line",
            required=True,
            info="Email draft subject line"
        ),
        StrInput(
            name="email_body",
            display_name="Email Body",
            required=True,
            info="Email draft body content"
        ),
        StrInput(
            name="source_cited",
            display_name="Source Cited",
            required=False,
            advanced=True,
            info="Case study or source referenced in the email"
        ),
    ]

    outputs = [
        Output(
            name="result",
            display_name="Result",
            method="create_note",
        ),
    ]

    async def create_note(self) -> Data:
        """
        Create a NOTE engagement in HubSpot with the email draft.

        Returns:
            Data object with success status, engagement ID, and HubSpot URL
        """
        url = "https://api.hubapi.com/crm/v3/objects/notes"

        # Build note body with clear formatting
        note_body = f"""🤖 AI-GENERATED EMAIL DRAFT

SUBJECT: {self.subject_line}

BODY:
{self.email_body}
"""

        # Add source citation if provided
        if self.source_cited:
            note_body += f"\n---\nSource: {self.source_cited}"

        # Build request payload with association
        payload = {
            "properties": {
                "hs_note_body": note_body,
                "hs_timestamp": str(int(time.time() * 1000))
            },
            "associations": [
                {
                    "to": {"id": self.contact_id},
                    "types": [
                        {
                            "associationCategory": "HUBSPOT_DEFINED",
                            "associationTypeId": 202  # Note to Contact
                        }
                    ]
                }
            ]
        }

        headers = {
            "Authorization": f"Bearer {self.hubspot_api_key}",
            "Content-Type": "application/json"
        }

        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.post(url, headers=headers, json=payload)

                if response.status_code in [200, 201]:
                    result = response.json()
                    engagement_id = result.get("id")

                    # Build HubSpot contact URL
                    hubspot_url = f"https://app.hubspot.com/contacts/contacts/{self.contact_id}"

                    self.status = f"✅ Note created: {engagement_id}"

                    return Data(data={
                        "success": True,
                        "engagement_id": engagement_id,
                        "hubspot_url": hubspot_url,
                        "note_body_preview": note_body[:200] + "..." if len(note_body) > 200 else note_body
                    })
                else:
                    error_text = response.text
                    self.status = f"❌ Error: {response.status_code}"

                    return Data(data={
                        "success": False,
                        "error": error_text,
                        "status_code": response.status_code
                    })

        except httpx.TimeoutException:
            self.status = "❌ Request timeout"
            return Data(data={
                "success": False,
                "error": "Request timed out after 15 seconds"
            })
        except Exception as e:
            self.status = f"❌ Error: {str(e)}"
            return Data(data={
                "success": False,
                "error": str(e)
            })
