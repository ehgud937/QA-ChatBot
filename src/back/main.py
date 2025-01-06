from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import openai
import json
import os
from typing import List, Dict
from dotenv import load_dotenv
from pydantic import BaseModel
from sentence_transformers import CrossEncoder

import numpy as np

# 환경변수 로드
load_dotenv()

# FastAPI 앱 및 OpenAI 클라이언트 초기화
app = FastAPI()

openai.api_key = os.getenv("OPENAI_API_KEY")
client = openai

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://ssafychat.kro.kr:5173", "https://ssafychat.kro.kr", "https://ssafychat.kro.kr:8000", "https://ssafychat.kro.kr:5174"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 대화 기록 저장소
conversation_history = {}

class SearchQuery(BaseModel):
    query: str
    
class Message(BaseModel):
    text: str
    chat_id: str = 'default'

class RAGSystem:
    def __init__(self, client):
        self.client = client
        self.regulation_chunks = self._prepare_regulation_chunks()
        self.qa_chunks = self._prepare_qa_chunks()
        self.chunks = self.regulation_chunks + self.qa_chunks
        self.embeddings_cache = {}
        # Cross-encoder 모델 초기화
        self.reranker = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')
        self.max_cache_size = 10000
    
    def _prepare_regulation_chunks(self) -> List[Dict]:
        """규정 JSON을 청크로 분할"""
        file_path = os.path.join(os.path.dirname(__file__), "rule.json")
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            chunks = self._create_chunks(data)
            return [{"id": chunk["id"], 
                    "content": chunk["content"],
                    "section": chunk["section"],
                    "type": "regulation"} for chunk in chunks]

    def _prepare_qa_chunks(self) -> List[Dict]:
        """QA 데이터셋을 청크로 분할"""
        file_path = os.path.join(os.path.dirname(__file__), "qa_dataset.json")
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                chunks = []
                
                for category in data['qa_dataset']:
                    for qa_pair in category['qa_pairs']:
                        chunk_content = {
                            "question": qa_pair['question'],
                            "answer": qa_pair['answer'],
                            "category": category['category']
                        }
                        chunks.append({
                            "id": f"qa_{category['category']}_{len(chunks)}",
                            "content": json.dumps(chunk_content, ensure_ascii=False, indent=2),
                            "section": category['category'],
                            "type": "qa"
                        })
                
                return chunks
        except FileNotFoundError:
            print("QA dataset file not found. Continuing with regulations only.")
            return []
    
    def _create_chunks(self, data, path="") -> List[Dict]:
        """재귀적으로 JSON을 청크로 분할"""
        chunks = []
        
        for key, value in data.items():
            current_path = f"{path}/{key}" if path else key
            
            if isinstance(value, dict):
                chunks.append({
                    "id": current_path,
                    "content": json.dumps({key: value}, ensure_ascii=False, indent=2),
                    "section": key
                })
                chunks.extend(self._create_chunks(value, current_path))
            
            elif isinstance(value, list):
                chunks.append({
                    "id": current_path,
                    "content": json.dumps({key: value}, ensure_ascii=False, indent=2),
                    "section": key
                })
        
        return chunks

    def _get_embedding(self, text: str) -> List[float]:
        """텍스트의 임베딩 생성 (캐싱 적용)"""
        if text not in self.embeddings_cache:
            # 캐시 크기 제한 관리
            if len(self.embeddings_cache) >= self.max_cache_size:
                # 캐시 클리어
                print(f"Clearing embedding cache (size: {len(self.embeddings_cache)})")
                self.embeddings_cache.clear()
            
            response = self.client.embeddings.create(
                model="text-embedding-ada-002",
                input=text
            )
            self.embeddings_cache[text] = response.data[0].embedding
        return self.embeddings_cache[text]

    def _calculate_similarity(self, query_embedding: List[float], chunk_embedding: List[float]) -> float:
        """코사인 유사도 계산"""
        dot_product = sum(a * b for a, b in zip(query_embedding, chunk_embedding))
        norm1 = sum(a * a for a in query_embedding) ** 0.5
        norm2 = sum(b * b for b in chunk_embedding) ** 0.5
        return dot_product / (norm1 * norm2)

    def retrieve_relevant_chunks(self, query: str, top_k: int = 10) -> List[Dict]:
        """질문과 관련된 청크 초기 검색"""
        query_embedding = self._get_embedding(query)
        chunk_scores = []
        
        for chunk in self.chunks:
            chunk_embedding = self._get_embedding(chunk['content'])
            similarity = self._calculate_similarity(query_embedding, chunk_embedding)
            chunk_scores.append((chunk, similarity))
        
        chunk_scores.sort(key=lambda x: x[1], reverse=True)
        return [chunk for chunk, _ in chunk_scores[:top_k]]

    def retrieve_and_rerank(self, query: str, initial_k: int = 10, final_k: int = 3) -> List[Dict]:
        """2단계 검색: 초기 검색 후 재순위화"""
        # 1단계: 임베딩 기반 초기 검색
        initial_chunks = self.retrieve_relevant_chunks(query, top_k=initial_k)
        
        if not initial_chunks:
            return []

        # 2단계: Cross-encoder를 사용한 재순위화
        # 배치 처리를 위한 설정
        batch_size = 32
        all_scores = []
        all_pairs = [[query, chunk['content']] for chunk in initial_chunks]
        
        # 배치 단위로 처리
        for i in range(0, len(all_pairs), batch_size):
            batch_pairs = all_pairs[i:i + batch_size]
            batch_scores = self.reranker.predict(batch_pairs)
            all_scores.extend(batch_scores.tolist() if isinstance(batch_scores, np.ndarray) else batch_scores)
        
        # 점수와 청크를 결합하고 정렬
        chunk_scores = list(zip(initial_chunks, all_scores))
        chunk_scores.sort(key=lambda x: x[1], reverse=True)
        
        # 최종 상위 k개 반환
        return [chunk for chunk, _ in chunk_scores[:final_k]]

# RAG 시스템 초기화
rag_system = RAGSystem(client)

@app.post("/chat")
async def chat_with_gpt(message: Message):
    # 대화 기록 관리
    if message.chat_id not in conversation_history:
        conversation_history[message.chat_id] = []
    
    try:
        # 관련 청크 검색 (reranker 사용)
        relevant_chunks = rag_system.retrieve_and_rerank(message.text)
        
        # 규정과 QA를 분리하여 컨텍스트 구성
        regulation_chunks = [chunk for chunk in relevant_chunks if chunk['type'] == 'regulation']
        qa_chunks = [chunk for chunk in relevant_chunks if chunk['type'] == 'qa']
        
        context = f"""
관련 규정:
{chr(10).join(chunk['content'] for chunk in regulation_chunks)}

관련 질문/답변 예시:
{chr(10).join(chunk['content'] for chunk in qa_chunks)}
"""
        
        system_prompt = """당신은 SSAFY 교육생들을 위한 학사 규정 안내 도우미입니다.
        주어진 규정 정보와 기존 질문/답변 예시를 참고하여 정확하고 친절하게 답변해주세요.
        답변은 반드시 제공된 규정 내용에 기반해야 하며, 규정에 명시되지 않은 내용은
        '해당 내용은 규정에 명시되어 있지 않습니다.'라고 답변해주세요."""
        
        messages = [
            {"role": "system", "content": system_prompt},
            *conversation_history[message.chat_id],
            {"role": "user", "content": f"""
컨텍스트 정보:
{context}

질문: {message.text}
"""}
        ]
        
        # GPT 응답 생성
        response = client.chat.completions.create(
            model="gpt-4",
            messages=messages,
            temperature=0.7
        )
        
        assistant_response = response.choices[0].message.content
        
        # 대화 기록 저장
        conversation_history[message.chat_id].append({"role": "user", "content": message.text})
        conversation_history[message.chat_id].append({"role": "assistant", "content": assistant_response})
        
        # 대화 기록 관리 (최근 20개 메시지만 유지)
        if len(conversation_history[message.chat_id]) > 20:
            conversation_history[message.chat_id] = conversation_history[message.chat_id][-20:]
        
        return {"response": assistant_response}
    except Exception as e:
        print(f"Error in chat endpoint: {str(e)}")
        return {"error": str(e)}

@app.post("/reset-chat")
async def reset_chat(chat_id: str = 'default'):
    if chat_id in conversation_history:
        conversation_history[chat_id] = []
    return {"message": "Chat history reset successfully"}

@app.get("/test")
async def test():
    return {"message": "Backend Connected!"}