from pydantic import BaseModel


class SimilarityRequest(BaseModel):
    paper_id: str
    categories: list
    years: list
    number_of_results: int = 10
    search_type: str = "KNN"


class UserTextSimilarityRequest(BaseModel):
    articles: list
    categories: list
    years: list
    number_of_results: int = 10
    search_type: str = "KNN"
