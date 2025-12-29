"""
Contact Parser Agent Component for LangBuilder

Parses free-form contact info and saves complete session to DynamoDB.
Called by Main Agent after Q8 when user provides contact details.

Uses GPT-4.1 for contact parsing and aget_messages for conversation history.
"""

import json
import uuid
from datetime import datetime, timedelta

from langchain_core.tools import StructuredTool
from pydantic import BaseModel, Field

from langbuilder.base.langchain_utilities.model import LCToolComponent
from langbuilder.field_typing import Tool
from langbuilder.io import (
    BoolInput,
    DropdownInput,
    IntInput,
    MessageTextInput,
    Output,
    SecretStrInput,
    StrInput,
)
from langbuilder.memory import aget_messages
from langbuilder.schema.data import Data

# AWS region options for dropdown
AWS_REGIONS = [
    "us-east-1", "us-east-2", "us-west-1", "us-west-2",
    "ca-central-1", "eu-west-1", "eu-west-2", "eu-west-3",
    "eu-central-1", "eu-north-1", "ap-south-1", "ap-northeast-1",
    "ap-northeast-2", "ap-northeast-3", "ap-southeast-1",
    "ap-southeast-2", "sa-east-1"
]


class ContactParserAgentComponent(LCToolComponent):
    """
    Parse contact info from free-form text and save complete session to DynamoDB.

    This component is called by the Main Agent after Q8 when the user provides
    their contact information. It:
    1. Receives free-form contact text from Main Agent
    2. Uses GPT-4.1 to parse name, email, company
    3. Gets full conversation history via aget_messages
    4. Saves structured data to DynamoDB
    5. Returns confirmation/structured response
    """

    display_name = "Contact Parser Agent"
    description = (
        "Parse contact info from free-form text and save complete session to DynamoDB. "
        "Call this after collecting contact information to save the full session."
    )
    icon = "user-check"
    name = "ContactParserAgent"

    inputs = [
        # Main inputs that Agent can set
        MessageTextInput(
            name="contact_input",
            display_name="Contact Info Text",
            info="The user's free-form contact information (e.g., 'John Doe, john@example.com, Acme Corp')",
            required=True,
            tool_mode=True,
        ),
        MessageTextInput(
            name="blueprint_text",
            display_name="Blueprint Text",
            info="The generated blueprint/proposal (if Option D was selected)",
            required=False,
            tool_mode=True,
        ),
        MessageTextInput(
            name="answers_json",
            display_name="Answers JSON",
            info="JSON string of Q1-Q8 answers (e.g., '{\"q1\": \"answer1\", \"q2\": \"answer2\"}')",
            required=False,
            tool_mode=True,
        ),

        # OpenAI configuration for GPT-4.1
        SecretStrInput(
            name="openai_api_key",
            display_name="OpenAI API Key",
            info="OpenAI API key for GPT-4.1 contact parsing",
            required=False,
        ),
        StrInput(
            name="model_name",
            display_name="Model Name",
            info="OpenAI model to use for parsing",
            value="gpt-4.1",
            required=True,
            advanced=True,
        ),

        # DynamoDB configuration
        StrInput(
            name="table_name",
            display_name="Table Name",
            info="DynamoDB table name",
            value="langbuilder_sessions",
            required=True,
        ),
        SecretStrInput(
            name="aws_access_key_id",
            display_name="AWS Access Key ID",
            info="AWS Access Key ID (leave empty to use environment credentials)",
            required=False,
        ),
        SecretStrInput(
            name="aws_secret_access_key",
            display_name="AWS Secret Access Key",
            info="AWS Secret Access Key (leave empty to use environment credentials)",
            required=False,
        ),
        SecretStrInput(
            name="aws_session_token",
            display_name="AWS Session Token",
            info="AWS Session Token for temporary credentials (optional)",
            required=False,
            advanced=True,
        ),
        DropdownInput(
            name="region_name",
            display_name="AWS Region",
            info="AWS region where DynamoDB table is located",
            options=AWS_REGIONS,
            value="us-east-1",
            required=True,
        ),
        IntInput(
            name="ttl_days",
            display_name="TTL (Days)",
            info="Time To Live in days - sessions auto-delete after this period",
            value=30,
            required=False,
            advanced=True,
        ),
        BoolInput(
            name="auto_create_table",
            display_name="Auto Create Table",
            info="Automatically create the DynamoDB table if it doesn't exist",
            value=True,
            advanced=True,
        ),
    ]

    async def _parse_contact_with_llm(self, contact_text: str) -> dict:
        """
        Use GPT-4.1 to parse contact info from free-form text.

        Args:
            contact_text: Free-form contact information text

        Returns:
            dict with name, email, company fields
        """
        try:
            from openai import OpenAI
        except ImportError as e:
            msg = "openai is not installed. Please install it using: pip install openai"
            raise ImportError(msg) from e

        # Get API key from input or environment
        api_key = self.openai_api_key
        if not api_key:
            import os
            api_key = os.environ.get("OPENAI_API_KEY")

        if not api_key:
            # Fall back to simple regex parsing
            self.log("No OpenAI API key - using simple parsing")
            return self._simple_parse_contact(contact_text)

        client = OpenAI(api_key=api_key)

        try:
            response = client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are a contact information parser. Extract name, email, and company "
                            "from the given text. Return ONLY a JSON object with these fields:\n"
                            '{"name": "...", "email": "...", "company": "..."}\n'
                            "If a field cannot be determined, use empty string."
                        )
                    },
                    {
                        "role": "user",
                        "content": f"Parse this contact info: {contact_text}"
                    }
                ],
                temperature=0,
                max_tokens=200,
            )

            result_text = response.choices[0].message.content.strip()

            # Parse JSON from response
            try:
                # Handle markdown code blocks
                if "```" in result_text:
                    result_text = result_text.split("```")[1]
                    if result_text.startswith("json"):
                        result_text = result_text[4:]
                    result_text = result_text.strip()

                contact = json.loads(result_text)
                return {
                    "name": contact.get("name", ""),
                    "email": contact.get("email", ""),
                    "company": contact.get("company", ""),
                }
            except json.JSONDecodeError:
                self.log(f"Failed to parse LLM response as JSON: {result_text}")
                return self._simple_parse_contact(contact_text)

        except Exception as e:
            self.log(f"OpenAI API error: {e}")
            return self._simple_parse_contact(contact_text)

    def _simple_parse_contact(self, contact_text: str) -> dict:
        """
        Simple regex-based contact parsing as fallback.
        """
        import re

        contact = {"name": "", "email": "", "company": ""}

        # Extract email
        email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', contact_text)
        if email_match:
            contact["email"] = email_match.group()

        # Try to extract name (first part before email or comma)
        parts = re.split(r'[,\n]', contact_text)
        if parts:
            first_part = parts[0].strip()
            # If it doesn't look like an email, use as name
            if "@" not in first_part:
                contact["name"] = first_part

        # Try to extract company (often after name and email)
        if len(parts) >= 3:
            contact["company"] = parts[2].strip()
        elif len(parts) >= 2 and "@" not in parts[1]:
            contact["company"] = parts[1].strip()

        return contact

    def _ensure_table_exists(self, dynamodb, table):
        """Check if DynamoDB table exists, create it if not."""
        from botocore.exceptions import ClientError

        try:
            table.load()
            self.log(f"Table {self.table_name} exists (status: {table.table_status})")
            return table
        except ClientError as e:
            error_code = e.response.get("Error", {}).get("Code", "")
            if error_code == "ResourceNotFoundException":
                self.log(f"Table {self.table_name} not found, creating...")
                try:
                    new_table = dynamodb.create_table(
                        TableName=self.table_name,
                        KeySchema=[{"AttributeName": "session_id", "KeyType": "HASH"}],
                        AttributeDefinitions=[{"AttributeName": "session_id", "AttributeType": "S"}],
                        BillingMode="PAY_PER_REQUEST"
                    )
                    new_table.wait_until_exists()
                    self.log(f"Table {self.table_name} created successfully")

                    # Enable TTL
                    try:
                        client = dynamodb.meta.client
                        client.update_time_to_live(
                            TableName=self.table_name,
                            TimeToLiveSpecification={"Enabled": True, "AttributeName": "ttl"}
                        )
                        self.log(f"TTL enabled on table {self.table_name}")
                    except Exception as ttl_error:
                        self.log(f"Warning: Could not enable TTL: {ttl_error}")

                    return new_table
                except Exception as create_error:
                    msg = f"Failed to create table {self.table_name}: {create_error}"
                    raise ValueError(msg) from create_error
            else:
                raise

    async def run_model(self) -> Data:
        """
        Parse contact info and save complete session to DynamoDB.

        Returns:
            Data object with confirmation and stored data
        """
        try:
            import boto3
            from botocore.exceptions import ClientError
        except ImportError as e:
            msg = "boto3 is not installed. Please install it using: pip install boto3"
            raise ImportError(msg) from e

        # 1. Parse contact info using GPT-4.1
        self.log(f"Parsing contact info: {self.contact_input[:100]}...")
        contact = await self._parse_contact_with_llm(str(self.contact_input))
        self.log(f"Parsed contact: {contact}")

        # 2. Get conversation history
        session_id = ""
        if hasattr(self, 'graph') and hasattr(self.graph, 'session_id') and self.graph.session_id:
            session_id = str(self.graph.session_id)

        conversation_transcript = []
        try:
            if session_id:
                messages = await aget_messages(
                    session_id=session_id,
                    order="ASC",
                    limit=100
                )
                conversation_transcript = [
                    {
                        "role": "assistant" if m.sender == "Machine" else "user",
                        "content": m.text
                    }
                    for m in messages
                ]
                self.log(f"Retrieved {len(conversation_transcript)} messages from conversation history")
            else:
                self.log("No session_id available for conversation history")
        except Exception as e:
            self.log(f"Warning: Could not retrieve conversation history: {e}")

        # 3. Parse answers JSON
        answers = {}
        if self.answers_json:
            try:
                answers = json.loads(str(self.answers_json))
            except json.JSONDecodeError:
                answers = {"raw": str(self.answers_json)}

        # 4. Get flow_id
        flow_id = ""
        if hasattr(self, 'graph') and hasattr(self.graph, 'flow_id') and self.graph.flow_id:
            flow_id = str(self.graph.flow_id)

        # 5. Initialize DynamoDB
        try:
            if self.aws_access_key_id and self.aws_secret_access_key:
                client_kwargs = {
                    "region_name": self.region_name,
                    "aws_access_key_id": self.aws_access_key_id,
                    "aws_secret_access_key": self.aws_secret_access_key,
                }
                if self.aws_session_token:
                    client_kwargs["aws_session_token"] = self.aws_session_token
                dynamodb = boto3.resource("dynamodb", **client_kwargs)
            else:
                dynamodb = boto3.resource("dynamodb", region_name=self.region_name)

            table = dynamodb.Table(self.table_name)
            if self.auto_create_table:
                table = self._ensure_table_exists(dynamodb, table)
        except Exception as e:
            msg = f"Failed to initialize DynamoDB: {e}"
            raise ValueError(msg) from e

        # 6. Calculate TTL
        now = datetime.utcnow()
        ttl_timestamp = int((now + timedelta(days=self.ttl_days)).timestamp())

        # 7. Generate session_id if empty
        if not session_id:
            session_id = str(uuid.uuid4())
            self.log("WARNING: Auto-generated session_id")

        # 8. Build complete session data
        session_data = {
            "session_id": session_id,
            "timestamp": now.isoformat() + "Z",
            "ttl": ttl_timestamp,
            "contact": contact,
            "answers": answers,
            "blueprint": str(self.blueprint_text) if self.blueprint_text else "",
            "conversation_transcript": conversation_transcript,
            "metadata": {
                "flow_id": flow_id,
                "phase": "completed",
                "questions_answered": list(answers.keys()) if answers else [],
            }
        }

        # 9. Save to DynamoDB
        self.log(f"Storing session {session_id} to table {self.table_name}")
        try:
            table.put_item(Item=session_data)
            self.log(f"Session {session_id} stored successfully")
        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            error_msg = e.response["Error"]["Message"]
            msg = f"DynamoDB error ({error_code}): {error_msg}"
            raise ValueError(msg) from e

        self.status = f"Session saved for {contact.get('name', 'Unknown')}"

        # 10. Return confirmation
        return Data(data={
            "success": True,
            "session_id": session_id,
            "contact": contact,
            "message": f"Session saved for {contact.get('name', 'Unknown')} ({contact.get('email', 'no email')})",
            "answers_count": len(answers),
            "transcript_count": len(conversation_transcript),
        })

    def build_tool(self) -> Tool:
        """
        Build a LangChain tool for parsing contacts and saving sessions.

        Returns:
            StructuredTool: A tool that can be used by an Agent.
        """
        class ContactParserInput(BaseModel):
            contact_input: str = Field(
                description="The user's free-form contact information (name, email, company)"
            )
            blueprint_text: str = Field(
                default="",
                description="The generated blueprint/proposal content (if Option D was selected)"
            )
            answers_json: str = Field(
                default="",
                description="JSON string of Q1-Q8 answers, e.g., '{\"q1\": \"answer\", \"q2\": \"answer\"}'"
            )

        def _parse_and_save_contact(
            contact_input: str,
            blueprint_text: str = "",
            answers_json: str = ""
        ) -> str:
            """Tool function that parses contact and saves session."""
            import asyncio

            # Debug log
            with open("/tmp/contact_parser_tool_called.txt", "a") as f:
                f.write(f"TOOL CALLED: contact={contact_input[:50]}, blueprint={len(blueprint_text)} chars\n")

            # Set the input values
            self.contact_input = contact_input
            self.blueprint_text = blueprint_text
            self.answers_json = answers_json

            # Run async method
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    # If we're already in an async context, create a new task
                    import concurrent.futures
                    with concurrent.futures.ThreadPoolExecutor() as executor:
                        future = executor.submit(asyncio.run, self.run_model())
                        result = future.result()
                else:
                    result = asyncio.run(self.run_model())

                with open("/tmp/contact_parser_tool_called.txt", "a") as f:
                    f.write(f"SUCCESS: {result}\n")

                if hasattr(result, 'data'):
                    return json.dumps(result.data)
                return str(result)
            except Exception as e:
                with open("/tmp/contact_parser_tool_called.txt", "a") as f:
                    f.write(f"ERROR: {type(e).__name__}: {e}\n")
                raise

        tool = StructuredTool.from_function(
            name="parse_contact_and_save_session",
            description=(
                "Parse contact info from free-form text and save the complete session to DynamoDB. "
                "Call this after collecting contact information (name, email, company). "
                "Pass the contact_input with the user's contact details, optionally include "
                "blueprint_text if a proposal was generated, and answers_json with conversation answers."
            ),
            args_schema=ContactParserInput,
            func=_parse_and_save_contact,
            return_direct=False,
        )

        self.status = "Contact Parser Agent Tool created"
        return tool
