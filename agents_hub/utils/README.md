# Utils Module for Agents Hub

This module provides utility functions and classes that support various components of the Agents Hub framework.

## Components

### Approval Interface

The ApprovalInterface class provides mechanisms for requesting human approval for critical operations:
- **Request Approval**: Ask for human confirmation before proceeding
- **Notify**: Send notifications to users
- **Track Decisions**: Record approval decisions for auditing

### Document Processing

The document module provides utilities for processing various document formats:
- **PDF Processing**: Extract text and metadata from PDF files
- **DOCX Processing**: Extract text and metadata from Word documents
- **Text Chunking**: Split text into manageable chunks for processing
- **Markdown Processing**: Parse and generate Markdown content

### Model Context Protocol (MCP)

The MCP module provides utilities for working with the Model Context Protocol:
- **MCP Client**: Connect to MCP servers
- **MCP Transport**: Handle communication with MCP servers
- **MCP Utilities**: Helper functions for MCP operations

### Multimodal Utilities

The multimodal module provides utilities for working with multimodal content:
- **Image Processing**: Process and analyze images
- **Audio Processing**: Process and analyze audio
- **Video Processing**: Process and analyze video
- **Multimodal Formatting**: Format multimodal content for LLMs

## Usage

### Human Approval Interface

```python
from agents_hub.utils.approval import ApprovalInterface

# Create approval interface
approval_interface = ApprovalInterface()

# Request human approval
approved = await approval_interface.request_approval(
    operation_id="deploy_production",
    details={
        "Environment": "Production",
        "Service": "API Gateway",
        "Changes": "Updated rate limiting",
    },
    message="Approve deployment to production?"
)

if approved:
    # Proceed with the operation
    print("Deployment approved, proceeding...")
else:
    # Cancel the operation
    print("Deployment cancelled by user")

# Send a notification
await approval_interface.notify(
    message="Deployment completed successfully",
    details={
        "Environment": "Production",
        "Service": "API Gateway",
        "Status": "Success",
        "Timestamp": "2023-06-15T14:30:00Z",
    }
)
```

### Document Processing

```python
from agents_hub.utils.document import extract_text_from_pdf, extract_text_from_docx, chunk_text

# Extract text from PDF
pdf_result = extract_text_from_pdf("document.pdf")
print(pdf_result["text"])
print(pdf_result["metadata"])

# Extract text from DOCX
docx_result = extract_text_from_docx("document.docx")
print(docx_result["text"])
print(docx_result["metadata"])

# Chunk text for processing
chunks = chunk_text(
    text=pdf_result["text"],
    chunk_size=1000,
    chunk_overlap=200,
    chunk_method="sentence"  # Options: token, character, sentence
)

for i, chunk in enumerate(chunks):
    print(f"Chunk {i+1}: {chunk[:100]}...")
```

### Model Context Protocol (MCP)

```python
from agents_hub.utils.mcp import MCPClient

# Create MCP client for filesystem access
filesystem_client = MCPClient(
    server_name="filesystem",
    server_command="npx",
    server_args=["-y", "@modelcontextprotocol/server-filesystem", "./"],
    transport="stdio",
)

# Start the MCP server
await filesystem_client.start()

# List files in a directory
files = await filesystem_client.execute({
    "command": "listFiles",
    "args": {
        "path": "."
    }
})

print("Files in current directory:")
for file in files:
    print(f"- {file['name']} ({file['type']})")

# Read a file
file_content = await filesystem_client.execute({
    "command": "readFile",
    "args": {
        "path": "README.md"
    }
})

print(f"README.md content: {file_content[:100]}...")

# Stop the MCP server
await filesystem_client.stop()
```

### Multimodal Utilities

```python
from agents_hub.utils.multimodal import process_image, format_multimodal_message

# Process an image
image_result = process_image("image.jpg")
print(f"Image dimensions: {image_result['width']}x{image_result['height']}")
print(f"Image format: {image_result['format']}")
print(f"Image size: {image_result['size']} bytes")

# Format a multimodal message for LLM
multimodal_message = format_multimodal_message(
    text="What can you tell me about this image?",
    images=["image.jpg"],
    image_format="base64"  # Options: base64, url
)

# Use the formatted message with an LLM
from agents_hub.llm.providers import OpenAIProvider

llm = OpenAIProvider(api_key="your-openai-api-key", model="gpt-4o")
response = await llm.chat(messages=[multimodal_message])
print(response.message.content)
```

## Advanced Features

### Custom Approval Handlers

```python
from agents_hub.utils.approval import ApprovalInterface, ApprovalHandler

# Create a custom approval handler
class SlackApprovalHandler(ApprovalHandler):
    def __init__(self, webhook_url: str, channel: str):
        self.webhook_url = webhook_url
        self.channel = channel
    
    async def request_approval(self, operation_id: str, details: dict, message: str) -> bool:
        # Implement Slack-based approval request
        # This would typically send a message to Slack and wait for a response
        return await self._send_slack_approval_request(message, details)
    
    async def notify(self, message: str, details: dict) -> None:
        # Implement Slack notification
        await self._send_slack_notification(message, details)
    
    async def _send_slack_approval_request(self, message: str, details: dict) -> bool:
        # Implementation details
        pass
    
    async def _send_slack_notification(self, message: str, details: dict) -> None:
        # Implementation details
        pass

# Use the custom approval handler
slack_approval = SlackApprovalHandler(
    webhook_url="https://hooks.slack.com/services/...",
    channel="#approvals"
)

approval_interface = ApprovalInterface(handlers=[slack_approval])
```

### Advanced Document Processing

```python
from agents_hub.utils.document import process_document_batch, extract_tables_from_pdf

# Process a batch of documents
documents = ["doc1.pdf", "doc2.docx", "doc3.pdf"]
results = await process_document_batch(
    documents=documents,
    chunk_size=1000,
    chunk_overlap=200
)

for doc, result in results.items():
    print(f"Document: {doc}")
    print(f"Chunks: {len(result['chunks'])}")
    print(f"Metadata: {result['metadata']}")

# Extract tables from PDF
tables = extract_tables_from_pdf("report.pdf")
for i, table in enumerate(tables):
    print(f"Table {i+1}:")
    print(table)
```

## Integration with Other Modules

The utils module integrates with:
- **Tools Module**: Providing utility functions for tools
- **RAG Module**: Supporting document processing for knowledge bases
- **Monitoring Module**: Tracking approval decisions and operations
- **LLM Module**: Formatting content for LLM interactions
