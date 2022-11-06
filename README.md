# Untitled1: Redis Vector Search hackathon
[Oct 24 - Nov 4, 2022 hackathon](https://hackathon.redisventures.com/) by Redis, Saturn Cloud, MLOps Community and NVIDIA Inception centered on **Vector Search** using the [arXiv scholarly papers](https://arxiv.org/) dataset.

*Demo app hosted at: **TBD***  <!-- TODO -->

## Changes to original repo
Original repo: https://github.com/RedisVentures/redis-arXiv-search

1. **Improved paper embeddings**: changed model to [sentence-transformers/all-distilroberta-v1](https://www.sbert.net/docs/pretrained_models.html) included authors to the embedding vector:
```python
df['authors_clean'] = df['authors'].apply(lambda a: ' '.join(re.findall(r'\w\w+', a)).strip())
df['text'] = df.apply(lambda r: Embeddings.clean_description(r['authors_clean'] + ' ' + r['title'] + ' ' + r['abstract']), axis=1)
```

2. **Enabled Redis search query to join categories with "AND" in addition to "OR" operator**. Thus, one can now define only the paper categories they're interested in and search for the papers that include all these categories, not just one. See [git blame](https://github.com/liram11/untitled1-vector-search/blame/2f26a01bb41cc86d95ef424f07cea39c8b97b27f/backend/vecsim_app/search_index.py#L130-L132).


3. **Enabled multi-input vector search**. We decided that some it might be useful for a scientist to know what are the papers "in between" the papers *A*, *B* and *C*. For that, we extended our Web UI to accept multiple article abstracts as input (along with a single set of "years" and "categories" configuration), we encode each abstract as a vector and then find the *mean* vector of these vectors. In case of two input papers, this is the middle of the line segment between two coordinates. In case of three papers, this is a centroid of a triangle of three coordinates. Thus, searching similar articles within the sphere around these points of interests can bring some interesting results (for example, it can help find multi-disciplinary papers related to the given papers).

4. **Implemented auto-detection of the cateogires**. We thought that it's a difficult work to assign the one of >150 categories manually and we trained and deployed a multi-label classification model that predicts categories for given text inputs. Our model performs relatively well showing ~0.74 evaluation result on multi-label text classfication (note that for demo purposes and for sake of saving computing resources it was trained only on 50% of the dataset). This model is deployed on the backend route `POST /predict-categories` and is called by the frontend in order to auto-select the dropdown checkbox of the category selection for all user input texts.

5. TBD (guys)


## How we used Redis
TBD (artem)

## How we used Saturn Cloud
TBD (artem)

---


Through the RediSearch module, vector data types and search indexes can be added to Redis. This turns Redis into
a highly performant, in-memory, vector database, which can be used for many types of applications.
Here we showcase Redis vector similarity search (VSS) applied to a document search/retrieval use case. 


## Getting Started
The steps below outline how to get this app up and running on your machine.

## Docker
Install [Docker Desktop](https://www.docker.com/products/docker-desktop/).

## Download arXiv Dataset

Pull the arXiv dataset from the the following [Kaggle link](https://www.kaggle.com/Cornell-University/arxiv).

Download and extract the zip file and place the resulting json file (`arxiv-metadata-oai-snapshot.json`) in the `data/` directory.

## Embedding Creation

**1. Setup python environment:**
- If you use conda, take advantage of the Makefile included here: `make env`
- Otherwise, setup your virtual env however you wish and install python deps in `requirements.txt`

**2. Use the notebook:**
- Run through the [`arxiv-embeddings.ipynb`](data/arxiv-embeddings.ipynb) notebook to generate some sample embeddings.


## Application

This app was built as a Single Page Application (SPA) with the following components:

- **[Redis Stack](https://redis.io/docs/stack/)**: Vector database + JSON storage
- **[FastAPI](https://fastapi.tiangolo.com/)** (Python 3.8)
- **[Pydantic](https://pydantic-docs.helpmanual.io/)** for schema and validation
- **[React](https://reactjs.org/)** (with Typescript)
- **[Redis OM](https://redis.io/docs/stack/get-started/tutorials/stack-python/)** for ORM
- **[Docker Compose](https://docs.docker.com/compose/)** for development
- **[MaterialUI](https://material-ui.com/)** for some UI elements/components
- **[React-Bootstrap](https://react-bootstrap.github.io/)** for some UI elements
- **[Huggingface Tokenizers + Models](https://huggingface.co/sentence-transformers)** for vector embedding creation

Some inspiration was taken from this [Cookiecutter project](https://github.com/Buuntu/fastapi-react)
and turned into a SPA application instead of a separate front-end server approach.

### Launch

**To launch app, run the following:**
- `docker compose up` from the same directory as `docker-compose.yml`
- Navigate to `http://localhost:8888` in a browser

**Building the containers manually:**

The first time you run `docker compose up` it will automatically build your Docker images based on the `Dockerfile`. However, in future passes when you need to rebuild, simply run: `docker compose up --build` to force a new build.

### Using a React dev env
It's typically easier to manipulate front end code in an interactive environment (**outside of Docker**) where one can test out code changes in real time. In order to use this approach:

1. Follow steps from previous section with Docker Compose to deploy the backend API.
2. `cd gui/` directory and use `yarn` to install packages: `yarn install --no-optional` (you may need to use `npm` to install `yarn`).
3. Use `yarn` to serve the application from your machine: `yarn start`.
4. Navigate to `http://localhost:3000` in a browser.
5. Make front end changes in realtime.

### Troubleshooting

- Issues with Docker? Run `docker system prune`, restart Docker Desktop, and try again.
- Open an issue here on GitHub and we will be as responsive as we can!


### Interested in contributing?
This is a new project. Comment on an open issue or create a new one. We can triage it from there.
