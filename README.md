<div align="right">
  <a href="https://github.com/RedisVentures/redis-arXiv-search"><img src="https://github.com/liram11/untitled1-vector-search/blob/fin-readme/backend/vecsim_app/data/untitled.png?raw=true" width="40%"><img></a>
</div>

<div align="center">
    <a href="https://github.com/RedisVentures/redis-arXiv-search"><img src="https://github.com/liram11/untitled1-vector-search/blob/fin-readme/backend/vecsim_app/data/redis-logo.png?raw=true" width="20%"><img></a>
    <a href="https://github.com/RedisVentures/redis-arXiv-search"><img src="https://github.com/liram11/untitled1-vector-search/blob/fin-readme/backend/vecsim_app/data/saturn.jpg?raw=true" width="20%"><img></a>
    <br />
    <br />
<div display="inline-block">
    <a href="https://untitled1-vector-search.community.saturnenterprise.io/" style="color:red;"><b>Hosted Demo</b></a>&nbsp;&nbsp;&nbsp;
    <a href="https://github.com/liram11/untitled1-vector-search" style="color:yellow;"><b>Code</b></a>&nbsp;&nbsp;&nbsp;
    <a href="TBD" style="color:yellow;"><b>Blog Post</b></a>&nbsp;&nbsp;&nbsp;
    <a href="https://redis.io/docs/stack/search/reference/vectors/"><b>Redis VSS Documentation</b></a>&nbsp;&nbsp;&nbsp;
  </div>
    <br />
    <br />
</div>

## Changes to the baseline solution
Original repo: https://github.com/RedisVentures/redis-arXiv-search

1. **Improved paper embeddings**: changed model to [sentence-transformers/all-distilroberta-v1](https://www.sbert.net/docs/pretrained_models.html)
We found that this gave more realistic results, at least for our use case.

2. **Enabled Redis search query to join categories with "AND" in addition to "OR" operator**. Thus, one can now define only the paper categories they're interested in and search for the papers that include all these categories, not just one. See [git blame](https://github.com/liram11/untitled1-vector-search/blame/2f26a01bb41cc86d95ef424f07cea39c8b97b27f/backend/vecsim_app/search_index.py#L130-L132).

3. **Enabled multi-input vector search**. We decided that some it might be useful for a scientist to know what are the papers "in between" the papers *A*, *B* and *C*. For that, we extended our Web UI to accept multiple article abstracts as input (along with a single set of "years" and "categories" configuration), we encode each abstract as a vector and then find the *mean* vector of these vectors. In case of two input papers, this is the middle of the line segment between two coordinates. In case of three papers, this is a centroid of a triangle of three coordinates. Thus, searching similar articles within the sphere around these points of interests can bring some interesting results (for example, it can help find multi-disciplinary papers related to the given papers).

4. **Implemented auto-detection of the categories**. We thought that it's a difficult work to assign the one of >150 categories manually and we trained and deployed a multi-label classification model that predicts categories for given text inputs. Our model performs relatively well: 

| *Model*                  | *Accuracy (%)* | *F1 (%)* | *AUC (%)* |
|----------------------------|------------------|------------|-------------|
| *Without pre-processing* |       39.60      |    65.55   |    78.03    |
| *with pre-processing*    |       39.76      |    66.95   |    80.06    |

This model is deployed on the backend route `POST /predict-categories` and is called by the frontend in order to auto-select the dropdown checkbox of the category selection for all user input texts. In the backend route, we can select the threshold for displaying the categories, but we pre-selected a value empirically.

For more details about the model technicalities, please go to [the detailed README](data/README.md).

## How we used Saturn Cloud
TBD (Artem)

## How we used Redis
TBD (artem)

___

Here we showcase Redis vector similarity search (VSS) applied to a document search/retrieval use case.

![Screen Shot 2022-09-20 at 12 20 16 PM](https://user-images.githubusercontent.com/13009163/191346916-4b8f648f-7552-4910-ad4e-9cc117230f00.png)


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
