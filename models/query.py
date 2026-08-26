from pydantic import BaseModel, Field
from typing import List, Literal, Optional, Union

from models.document import BaseDocumentChunk
from models.ingest import EncoderConfig
from models.vector_database import VectorDatabase
from qdrant_client.http.models import Filter as QdrantFilter


Filter = Union[QdrantFilter, dict]


class QueryTransformationConfig(BaseModel):
    fusion: bool = Field(
        default=False, description="Enable query fusion to split queries into multiple searches"
    )
    step_back: bool = Field(
        default=False, description="Enable step-back prompting for broader context retrieval"
    )
    rewrite: bool = Field(
        default=False, description="Enable query rewriting to improve search relevance"
    )


class RequestPayload(BaseModel):
    input: str
    vector_database: VectorDatabase
    index_name: str
    encoder: EncoderConfig = EncoderConfig()
    session_id: Optional[str] = None
    interpreter_mode: Optional[bool] = False
    exclude_fields: List[str] = None
    filter: Optional[Filter] = None
    top_k: int = Field(
        default=5, description="Number of top results to retrieve from vector database"
    )
    top_n: Optional[int] = Field(
        default=None, description="Optional: limit final results to top_n (must be <= top_k)"
    )
    relevancy_score_threshold: Optional[float] = Field(
        default=None, description="Optional: minimum relevancy score threshold (0.0 to 1.0)"
    )
    query_transformation: QueryTransformationConfig = Field(
        default_factory=QueryTransformationConfig, description="Query transformation options"
    )


class ResponseData(BaseModel):
    content: str
    doc_url: str
    page_number: Optional[int]
    metadata: Optional[dict] = None


class ResponsePayload(BaseModel):
    success: bool
    data: List[BaseDocumentChunk]

    def model_dump(self, exclude: set = None):
        return {
            "success": self.success,
            "data": [chunk.dict(exclude=exclude) for chunk in self.data],
        }
