import numpy as np
import openai
from rest_framework import status
from rest_framework.views import APIView

from services import CustomResponseMixin

from .models import PropertyChatHistory, PropertyEmbedding
from .serializers import PropertyChatSerializer

import logging

logger = logging.getLogger(__name__)
class PropertyChatAPIView(APIView, CustomResponseMixin):
    def post(self, request, property_id):
        serializer = PropertyChatSerializer(data=request.data)
        if serializer.is_valid():
            question = serializer.validated_data["question"]
            # This Fetch embeddings for this property
            embeddings_qs = PropertyEmbedding.objects.filter(property_id=property_id)
            if not embeddings_qs.exists():
                return self.custom_response(
                    message="No data available for this property.",
                    status=status.HTTP_404_NOT_FOUND,
                )

            question_embedding = self.generate_embedding(question)
            if not question_embedding:
                return self.custom_response(
                    message="Failed to generate question embedding.",
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )
            # Calculate similarity with each chunk
            chunks_with_scores = []
            for emb in embeddings_qs:
                score = self.cosine_similarity(question_embedding, emb.embedding)
                chunks_with_scores.append((score, emb.chunk))
            # Sort and select top 3 relevant chunks
            top_chunks = sorted(chunks_with_scores, key=lambda x: x[0], reverse=True)[
                :3
            ]
            context = "\n".join([chunk for _, chunk in top_chunks])

            # Fetch recent chat history for this property (limit last 5)
            chat_history_qs = PropertyChatHistory.objects.filter(
                property_id=property_id
            ).order_by("-created_at")[:5]
            # Build chat history context
            chat_context = ""
            for chat in reversed(chat_history_qs):  # Oldest to newest
                chat_context += f"User: {chat.question}\nAI: {chat.answer}\n"

            final_context = f"Property Information:\n{context}\n\nRecent Conversation:\n{chat_context}"
            #  Build prompt
            prompt = f"Context:\n{final_context}\n\nQuestion:\n{question}\n\nAnswer:"
            # Call OpenAI Chat API
            answer = self.call_openai_chat(prompt)
            # Save this chat to ChatHistory for future context
            PropertyChatHistory.objects.create(
                property_id=property_id,
                user=(
                    request.user if request.user.is_authenticated else None
                ),  # Optional: store user
                question=question,
                answer=answer,
            )
            return self.custom_response(message=answer, status=status.HTTP_200_OK)
        else:
            return self.custom_response(
                data=serializer.errors, status=status.HTTP_400_BAD_REQUEST
            )

    def generate_embedding(self, text, model="text-embedding-ada-002"):
        try:
            response = openai.embeddings.create()(input=text, model=model)
            return response["data"][0]["embedding"]
        except Exception as e:
            logger.error(f"Embedding error: {e}")
            return None

    def cosine_similarity(self, vec1, vec2):
        # Simple cosine similarity between two lists
        vec1 = np.array(vec1)
        vec2 = np.array(vec2)
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        return dot_product / (norm1 * norm2)

    def call_openai_chat(self, prompt, model="gpt-3.5-turbo", temperature=0.2):
        try:
            response = openai.ChatCompletion.create(
                model=model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful real estate assistant.",
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=temperature,
            )
            return response["choices"][0]["message"]["content"].strip()
        except Exception as e:
            print(f"ChatCompletion error: {e}")
            return "Sorry, I couldn't process your question at the moment."
