# REST API

Experimental!!!

## Step 1: Run a Caikit grpcServer

So far I'd assume you are running caikit-huggingface-demo (don't need the frontend the backend works).  If you have some other grpcServer running it should recognize some tasks, but won't understand the ins/outs so that doesn't work yet.

## Step 2: venv and requirements

Use the same venv as you would for the server (fastapi and uvicorn were added).

* Update your venv if needed

```shell
python3 -m venv venv
source venv_rest/bin/activate
pip install -r requirements.txt
```

## Step 3: Fire it up

```shell
source venv_rest/bin/activate
cd caikit_huggingface_demo
./restapi.py
```

## Browse

* Swagger: http://127.0.0.1:5000/docs
* ReDoc: http://127.0.0.1:5000/redoc

> Watch to for Todo and future because a lot of this is "needs impl"

Try:

* Object detection (w/ a URL to an image that isn't too big)
* Image classification (w/ a URL to an image that isn't too big)
* more coming soon
* Parameterized endpoints make sense but for now I'm showing the models that I expect to work. Model+Task need to work together.
