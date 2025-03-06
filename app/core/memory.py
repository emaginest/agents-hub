import boto3
from typing import List, Dict, Optional
import json
import time
from datetime import datetime, timedelta
from app.core.constants import SYSTEM_PROMPT


class DynamoDBMemory:
    """Memory store using DynamoDB for the ARIA agent."""

    def __init__(self):
        """Initialize DynamoDB memory store."""
        from app.config import Settings

        settings = Settings()

        self.dynamodb = boto3.resource("dynamodb")
        self.table_name = f"{settings.environment.value}-jr-agent-langchain"
        self._ensure_table_exists()
        self.table = self.dynamodb.Table(self.table_name)

    def _ensure_table_exists(self):
        """Ensure the DynamoDB table exists, create it if it doesn't."""
        try:
            # Check if table exists
            client = boto3.client("dynamodb")
            client.describe_table(TableName=self.table_name)
        except client.exceptions.ResourceNotFoundException:
            try:
                # Create table if it doesn't exist
                print(f"Creating DynamoDB table {self.table_name}...")
                client.create_table(
                    TableName=self.table_name,
                    KeySchema=[
                        {
                            "AttributeName": "patientId",
                            "KeyType": "HASH",
                        },  # Partition key
                        {"AttributeName": "date", "KeyType": "RANGE"},  # Sort key
                    ],
                    AttributeDefinitions=[
                        {"AttributeName": "patientId", "AttributeType": "S"},
                        {"AttributeName": "date", "AttributeType": "S"},
                    ],
                    BillingMode="PAY_PER_REQUEST",  # On-demand capacity
                )
                # Wait for table to be created
                print("Waiting for table to be created...")
                waiter = client.get_waiter("table_exists")
                waiter.wait(
                    TableName=self.table_name,
                    WaiterConfig={"Delay": 5, "MaxAttempts": 20},
                )
                print("Table created successfully")
            except Exception as e:
                raise Exception(f"Error creating DynamoDB table: {str(e)}")

    async def save_interaction(
        self,
        patient_id: str,
        ask: str,
        answer: str,
        prompt: Optional[str] = None,
    ) -> None:
        """
        Save an interaction to DynamoDB.

        Args:
            patient_id: Unique identifier for the patient
            ask: Patient's question/message
            answer: ARIA's response
            prompt: Optional system prompt used
        """
        date = datetime.now().isoformat()

        item = {
            "patientId": patient_id,
            "date": date,
            "ask": ask,
            "answer": answer,
            "prompt": prompt if prompt else SYSTEM_PROMPT,
        }

        self.table.put_item(Item=item)

    async def get_recent_interactions(
        self, patient_id: str, limit: int = 5
    ) -> List[Dict]:
        """
        Retrieve recent interactions for a patient.

        Args:
            patient_id: Unique identifier for the patient
            limit: Maximum number of interactions to retrieve

        Returns:
            List of recent interactions
        """
        response = self.table.query(
            KeyConditionExpression="patientId = :pid",
            ExpressionAttributeValues={":pid": patient_id},
            ScanIndexForward=False,  # Sort in descending order (most recent first)
            Limit=limit,
        )

        interactions = []
        for item in response.get("Items", []):
            interaction = {
                "message": item["ask"],
                "response": item["answer"],
                "date": item["date"],
            }
            interactions.append(interaction)

        return interactions

    async def clear_patient_history(self, patient_id: str) -> None:
        """
        Clear all interaction history for a patient.

        Args:
            patient_id: Unique identifier for the patient
        """
        # Query all items for the patient
        response = self.table.query(
            KeyConditionExpression="patientId = :pid",
            ExpressionAttributeValues={":pid": patient_id},
        )

        # Delete each item
        with self.table.batch_writer() as batch:
            for item in response.get("Items", []):
                batch.delete_item(
                    Key={"patientId": item["patientId"], "date": item["date"]}
                )


# Create a global instance
memory = DynamoDBMemory()
