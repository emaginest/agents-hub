from typing import List, Dict
from openai import AsyncOpenAI
from app.config import Settings

settings = Settings()
client = AsyncOpenAI(api_key=settings.openai_api_key)


async def generate_response(query: str, context: List[Dict[str, any]]) -> str:
    """Generate a response using the retrieved context."""
    try:
        # Format context for the prompt
        formatted_context = "\n\n".join(
            [
                f"Document (relevance: {1 - doc['distance']:.2f}):\n{doc['text']}"
                for doc in context
            ]
        )

        # Create the prompt
        prompt = f"""Based on the following context, please answer the question.
        
Context:
{formatted_context}

Question: {query}

Answer:"""

        # Generate response
        response = await client.chat.completions.create(
            model=settings.openai_model,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a helpful assistant. Answer the user's question based on "
                        "the provided context. If the context doesn't contain relevant "
                        "information, say so. Always be clear about what information "
                        "comes from the context."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.7,
            max_tokens=settings.max_tokens,
        )

        return response.choices[0].message.content
    except Exception as e:
        raise Exception(f"Error generating response: {str(e)}")
