import asyncio
import typing as t

import redis.asyncio as redis
from fastapi import APIRouter
from vecsim_app import config
from vecsim_app.categories import CATEGORIES
from vecsim_app.embeddings import Embeddings
from vecsim_app.models import Paper
from vecsim_app.multilabel_classifier.inference import load_models, predict_categories
from vecsim_app.schema import (
    CategoriesPredictionRequest,
    SimilarityRequest,
    UserTextSimilarityRequest,
)
from vecsim_app.search_index import SearchIndex

paper_router = r = APIRouter()
redis_client = redis.from_url(config.REDIS_URL)
embeddings = Embeddings()
search_index = SearchIndex()
STATE = {}

mlc_path = f"{config.DATA_LOCATION}/multilabel_classifier/checkpoint"
# TODO: load once the model is trained!
# mlc_model, mlc_tokenizer, mlc_b = load_models(mlc_path, f"{mlc_path}/mlb.pkl")


def _cut_off_category_description(c: str):
    # 'q-fin.TR (Trading and Market Microstructure)' -> 'q-fin.TR`
    return c.split()[0]


async def process_paper(p, i: int) -> t.Dict[str, t.Any]:
    paper = await Paper.get(p.paper_pk)
    paper = paper.dict()
    score = 1 - float(p.vector_score)
    paper["similarity_score"] = score
    return paper


async def papers_from_results(total, results_list) -> t.Dict[str, t.Any]:
    # extract papers from VSS results
    results = [
        await process_paper(p, i)
        for res in results_list
        for i, p in enumerate(res.docs)
    ]
    print('\n'.join([f"{r['similarity_score']:.3f} {r['title']}" for r in results]))
    # dedup
    results = list({d["paper_id"]: d for d in results}.values())
    # sort by similarity score
    results = sorted(results, key=lambda x: -x['similarity_score'])
    return {
        "total": total,
        "papers": results,
    }


@r.get("/", response_model=t.Dict)
async def get_papers(
    limit: int = 20, skip: int = 0, years: str = "", categories: str = ""
):
    papers = []
    expressions = []
    years = [y for y in years.split(",") if y]
    categories = [_cut_off_category_description(c) for c in categories.split(",") if c]
    if years and categories:
        expressions.append((Paper.year << years) & (Paper.categories << categories))
    elif years and not categories:
        expressions.append(Paper.year << years)
    elif categories and not years:
        expressions.append(Paper.categories << categories)
    # Run query

    papers = (
        await Paper.find(*expressions)
        .copy(offset=skip, limit=limit)
        .execute(exhaust_results=False)
    )

    # Get total count
    total = (
        await redis_client.ft(config.INDEX_NAME).search(
            search_index.count_query(years=years, categories=categories)
        )
    ).total
    return {"total": total, "papers": papers}


@r.post("/predict-categories", response_model=t.Dict)
async def find_papers_by_text(categories_request: CategoriesPredictionRequest):
    # TODO: once the model is ready, uncomment
    categories = "cs.IT,cs.AI,math.IT,q-bio.PE".split(",")
    # categories = predict_categories(
    #     categories_request.articles,
    #     mlc_model,
    #     mlc_tokenizer,
    #     mlc_b,
    #     proba_threshold=categories_request.proba_threshold,
    # )
    return {
        "categories": categories,
        "categories_names": [CATEGORIES.get(c) for c in categories],
    }

    # Get Paper records of those results
    return await papers_from_results(total.total, [results])


@r.post("/vectorsearch/text", response_model=t.Dict)
async def find_papers_by_text(similarity_request: SimilarityRequest):
    # Create query
    categories = [
        _cut_off_category_description(c) for c in similarity_request.categories
    ]
    query = search_index.vector_query(
        categories,
        similarity_request.years,
        similarity_request.search_type,
        similarity_request.number_of_results,
    )
    count_query = search_index.count_query(
        years=similarity_request.years, categories=similarity_request.categories
    )

    # find the vector of the Paper listed in the request
    paper_vector_key = "paper_vector:" + str(similarity_request.paper_id)
    vector = await redis_client.hget(paper_vector_key, "vector")

    # obtain results of the queries
    total, results = await asyncio.gather(
        redis_client.ft(config.INDEX_NAME).search(count_query),
        redis_client.ft(config.INDEX_NAME).search(
            query, query_params={"vec_param": vector}
        ),
    )

    # Get Paper records of those results
    return await papers_from_results(total.total, [results])


@r.post("/vectorsearch/text/user", response_model=t.Dict)
async def find_papers_by_user_text(similarity_request: UserTextSimilarityRequest):
    # Create query
    categories = [
        _cut_off_category_description(c) for c in similarity_request.categories
    ]

    query = search_index.vector_query(
        categories,
        similarity_request.years,
        similarity_request.search_type,
        similarity_request.number_of_results,
    )
    count_query = search_index.count_query(
        years=similarity_request.years, categories=similarity_request.categories
    )

    query_coroutines = [redis_client.ft(config.INDEX_NAME).search(count_query)]
    for article in similarity_request.articles:
        if not article["text"].strip():
            continue
        query_coroutines.append(
            redis_client.ft(config.INDEX_NAME).search(
                query,
                query_params={"vec_param": embeddings.make(article["text"]).tobytes()},
            )
        )

    # obtain results of the queries
    total, *results_list = await asyncio.gather(*query_coroutines)

    # results = [r for results in results_list for r in results]
    # print(results)

    # Get Paper records of those results
    return await papers_from_results(total.total, results_list)
