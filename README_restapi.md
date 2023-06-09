# REST API

Experimental!!!

## Step 1: Run a Caikit grpcServer

So far I'd assume you are running caikit-huggingface-demo (don't need the frontend the backend works).  If you have some other grpcServer running it should recognize some tasks, but won't understand the ins/outs so that doesn't work yet.

## Step 2: venv and requirements

Do this once and then only for new requirements.

### TODO: Get a better handle on requirements here

```shell
cd caikit_huggingface_demo
python3 -m venv venv_rest
pip install -r requirements_rest.txt
```

## Step 3: Fire it up

```shell
cd caikit_huggingface_demo
source venv_rest/bin/activate
./restapi.py
```

## Browse

Swagger: http://127.0.0.1:5000/docs
ReDoc: http://127.0.0.1:5000/redoc

> Watch to for Todo and future because a lot of this is "needs impl"

Try:

* Object detection (w/ a URL to an image that isn't too big)
* Image classification (w/ a URL to an image that isn't too big)
* more coming soon
