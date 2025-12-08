"""
DynamoDB Session Store Component for LangBuilder

Stores conversation session data to AWS DynamoDB for persistence,
analytics, and session resumption capabilities.

Adapted for LangBuilder 1.65 (CloudGeometry fork)
"""

import time
import uuid
from datetime import datetime, timedelta

from langbuilder.custom.custom_component.component import Component
from langbuilder.io import BoolInput, DataInput, DropdownInput, IntInput, MessageTextInput, Output, SecretStrInput, StrInput
from langbuilder.schema.data import Data

# AWS region options for dropdown
AWS_REGIONS = [
    "us-east-1", "us-east-2", "us-west-1", "us-west-2",
    "ca-central-1", "eu-west-1", "eu-west-2", "eu-west-3",
    "eu-central-1", "eu-north-1", "ap-south-1", "ap-northeast-1",
    "ap-northeast-2", "ap-northeast-3", "ap-southeast-1",
    "ap-southeast-2", "sa-east-1"
]


class DynamoDBSessionStoreComponent(Component):
    """
    Store session data to AWS DynamoDB table.

    This component saves conversation session data to DynamoDB with automatic
    TTL for cleanup. It accepts Data input from Structured Output component,
    making it easy to store structured conversation metadata.
    """

    display_name = "DynamoDB Store"
    description = (
        "Store session data to Amazon DynamoDB with automatic TTL. "
        "Accepts Data from Structured Output for easy integration."
    )
    icon = "Amazon"
    name = "DynamoDBSessionStore"

    inputs = [
        # Data input from Structured Output
        DataInput(
            name="structured_data",
            display_name="Structured Data",
            info="Data from Structured Output component containing conversation metadata",
            required=True,
        ),

        # User message input
        MessageTextInput(
            name="user_message",
            display_name="User Message",
            info="The user's message (from Chat Input)",
            required=True,
        ),

        # Session identification
        MessageTextInput(
            name="session_id",
            display_name="Session ID",
            info="UUID or unique identifier for this session. Auto-generates if empty.",
            required=False,
        ),

        # DynamoDB configuration
        StrInput(
            name="table_name",
            display_name="Table Name",
            info="DynamoDB table name",
            value="langbuilder_sessions",
            required=True,
        ),

        # AWS credentials (secured inputs)
        SecretStrInput(
            name="aws_access_key_id",
            display_name="AWS Access Key ID",
            info="AWS Access Key ID (leave empty to use IAM role or environment credentials)",
            value="AWS_ACCESS_KEY_ID",
            required=False,
        ),

        SecretStrInput(
            name="aws_secret_access_key",
            display_name="AWS Secret Access Key",
            info="AWS Secret Access Key (leave empty to use IAM role or environment credentials)",
            value="AWS_SECRET_ACCESS_KEY",
            required=False,
        ),

        DropdownInput(
            name="region_name",
            display_name="AWS Region",
            info="AWS region where DynamoDB table is located",
            options=AWS_REGIONS,
            value="us-west-2",
            required=True,
        ),

        # TTL configuration
        IntInput(
            name="ttl_days",
            display_name="TTL (Days)",
            info="Time To Live in days - sessions auto-delete after this period (default: 30)",
            value=30,
            required=False,
            advanced=True,
        ),

        # Auto-create table option
        BoolInput(
            name="auto_create_table",
            display_name="Auto Create Table",
            info="Automatically create the DynamoDB table if it doesn't exist",
            value=True,
            advanced=True,
        ),
    ]

    outputs = [
        Output(
            name="stored_session",
            display_name="Stored Session",
            method="store_session",
        ),
    ]

    def _ensure_table_exists(self, dynamodb, table):
        """
        Check if DynamoDB table exists, create it if not.

        Args:
            dynamodb: boto3 DynamoDB resource
            table: DynamoDB Table object

        Returns:
            DynamoDB Table object (existing or newly created)
        """
        from botocore.exceptions import ClientError

        try:
            # Try to get table status - this will fail if table doesn't exist
            table.load()
            self.log(f"Table {self.table_name} exists (status: {table.table_status})")
            return table

        except ClientError as e:
            error_code = e.response.get("Error", {}).get("Code", "")

            if error_code == "ResourceNotFoundException":
                self.log(f"Table {self.table_name} not found, creating...")

                # Create the table
                try:
                    new_table = dynamodb.create_table(
                        TableName=self.table_name,
                        KeySchema=[
                            {"AttributeName": "session_id", "KeyType": "HASH"}
                        ],
                        AttributeDefinitions=[
                            {"AttributeName": "session_id", "AttributeType": "S"}
                        ],
                        BillingMode="PAY_PER_REQUEST"
                    )

                    # Wait for table to be created
                    self.log(f"Waiting for table {self.table_name} to be created...")
                    new_table.wait_until_exists()
                    self.log(f"Table {self.table_name} created successfully")

                    # Enable TTL on the table
                    try:
                        client = dynamodb.meta.client
                        client.update_time_to_live(
                            TableName=self.table_name,
                            TimeToLiveSpecification={
                                "Enabled": True,
                                "AttributeName": "ttl"
                            }
                        )
                        self.log(f"TTL enabled on table {self.table_name}")
                    except Exception as ttl_error:
                        self.log(f"Warning: Could not enable TTL: {ttl_error}")

                    return new_table

                except Exception as create_error:
                    msg = f"Failed to create table {self.table_name}: {create_error}"
                    self.log(f"Error: {msg}")
                    raise ValueError(msg) from create_error
            else:
                # Re-raise other errors
                raise

    def store_session(self) -> Data:
        """
        Store session data to DynamoDB.

        Returns:
            Data object with confirmation and stored data
        """
        # Import boto3 (raises ImportError if not installed)
        try:
            import boto3
            from botocore.exceptions import ClientError
        except ImportError as e:
            msg = (
                "boto3 is not installed. Please install it using: "
                "uv pip install boto3"
            )
            raise ImportError(msg) from e

        # Extract data from structured_data input
        data = self.structured_data
        if isinstance(data, list):
            data = data[0] if data else {}

        # Get the data dict from Data object
        if hasattr(data, "data"):
            output_data = data.data
        elif isinstance(data, dict):
            output_data = data
        else:
            output_data = {}

        # Initialize DynamoDB client
        try:
            # Use credentials if provided, otherwise use IAM role or environment
            if self.aws_access_key_id and self.aws_secret_access_key:
                dynamodb = boto3.resource(
                    "dynamodb",
                    region_name=self.region_name,
                    aws_access_key_id=self.aws_access_key_id,
                    aws_secret_access_key=self.aws_secret_access_key,
                )
                self.log("Using provided AWS credentials")
            else:
                dynamodb = boto3.resource("dynamodb", region_name=self.region_name)
                self.log("Using IAM role or environment credentials")

            # Check if table exists, create if needed
            table = dynamodb.Table(self.table_name)

            if self.auto_create_table:
                table = self._ensure_table_exists(dynamodb, table)

        except Exception as e:
            msg = f"Failed to initialize DynamoDB client: {e}"
            raise ValueError(msg) from e

        # Calculate TTL timestamp
        now = datetime.utcnow()
        ttl_timestamp = int((now + timedelta(days=self.ttl_days)).timestamp())

        # Get session_id - priority order:
        # 1. From session_id input (if it's a string)
        # 2. From Message object's session_id (if Message passed to session_id input)
        # 3. From graph's session_id (flow-level session from API call)
        # 4. Auto-generate UUID as last resort
        raw_session_id = self.session_id
        session_id = ""

        # Check if session_id input is a plain string
        if isinstance(raw_session_id, str) and raw_session_id.strip():
            session_id = raw_session_id.strip()
        # Check if it's a Message object - extract its session_id
        elif hasattr(raw_session_id, 'session_id') and hasattr(raw_session_id, 'text'):
            msg_session_id = getattr(raw_session_id, 'session_id', None)
            if msg_session_id:
                session_id = str(msg_session_id).strip()

        # If still empty, try to get from graph's session_id (API-level session)
        if not session_id and hasattr(self, 'graph') and hasattr(self.graph, 'session_id') and self.graph.session_id:
            session_id = str(self.graph.session_id).strip()

        # Last resort: auto-generate (but this breaks conversation continuity!)
        if not session_id:
            session_id = str(uuid.uuid4())
            self.log("WARNING: Auto-generated session_id - conversation continuity will be lost!")

        # Prepare item to save - extract fields from structured output
        item = {
            "session_id": session_id,  # Primary key
            "timestamp": now.isoformat(),
            "ttl": ttl_timestamp,  # DynamoDB TTL attribute
            "user_message": str(self.user_message),
            "ai_response": output_data.get("response", ""),
            "phase": output_data.get("phase", ""),
            "current_question": output_data.get("current_question", ""),
            "questions_answered": output_data.get("questions_answered", []),
            "answers": output_data.get("answers", {}),
            "persona_hint": output_data.get("persona_hint", ""),
            "email": output_data.get("email", ""),
        }

        # Log operation
        self.log(f"Storing session {session_id} to table {self.table_name}")
        self.log(f"Phase: {item['phase']}, Question: {item['current_question']}")
        self.log(f"TTL: {ttl_timestamp} ({self.ttl_days} days from now)")

        # Put item to DynamoDB
        try:
            table.put_item(Item=item)
            self.log(f"Session {session_id} stored successfully")

        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            error_msg = e.response["Error"]["Message"]
            msg = f"DynamoDB error ({error_code}): {error_msg}"
            self.log(f"Error: {msg}")
            raise ValueError(msg) from e

        except Exception as e:
            msg = f"Unexpected error storing session: {e}"
            self.log(f"Error: {msg}")
            raise ValueError(msg) from e

        # Update status (visible in component UI)
        self.status = f"Stored session {session_id}"

        # Return Data object with stored information
        return Data(data=item)
