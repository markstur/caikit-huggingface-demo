#!/usr/bin/env python
# Copyright The Caikit Authors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Standard
from google.protobuf.message_factory import MessageFactory
import module_ids

import os

# Third Party
import uvicorn
from fastapi import FastAPI, APIRouter

# Local
from caikit.config import configure

from grpc_task_wrappers import Grpcer, get_module_models, get_grpc_things

# runtime library config
CONFIG_PATH = os.path.realpath(
    os.path.join(os.path.dirname(__file__), "runtime", "config", "config.yml")
)
configure(CONFIG_PATH)

# __main__ runs uvicorn, then uvicorn runs this file __restapi__ to get app
if __name__ != "__main__":
    app = FastAPI()
    router = APIRouter()

    service_prefix, methods, desc_pool, client_stub = get_grpc_things()  # TODO: Refactor all grpc coupling out of this file
    print("METHODS: ", methods)

    # Our equivalent to:
    # https://api-inference.huggingface.co/models/bert-base-uncased or
    # https://api-inference.huggingface.co/models/facebook/bart-large-cnn
    # can be:
    # https://{host}/models/caikit/{mm-model-id}

    # TBD: ^^^ with caikit like a namespace(?) -- or drop that?

    # For models that support multiple tasks there is an undocumented(?) pipeline/task
    # Caikit might prefer this, but we'll have to map models to tasks somehow anyway.
    # https://api-inference.huggingface.co/pipeline/{task}/model/{model}
    # https://{host}/pipeline/{task}/model/caikit/{mm-model-id}


    #
    # Here we are discovering and adding to swagger for all tasks/models.
    # This is nice to see the models available, but TBD.  That could just be a path param.
    #
    for method_name, method_descriptor in methods.items():

        # print(method_descriptor.output_type.full_name)

        task, _, _ = method_name.rpartition("TaskPredict")
        if hasattr(client_stub, method_name):
            method = getattr(client_stub, method_name)
        else:
            print(f"Failed to find expected method: {method_name}")
            continue

        request_name = f"{service_prefix}.{task}TaskRequest"
        try:
            request_desc = desc_pool.FindMessageTypeByName(request_name)
        except KeyError as e:
            print(f"Find request error: {e}")
            continue

        request = MessageFactory(desc_pool).GetPrototype(request_desc)
        module_models = get_module_models(None)
        models = module_models.get(module_ids.MODULE_IDS[task], [])

        print("MODELS", models)

        for model in models:
            grpcer = Grpcer(request=request, predict=method, model=model)
            # endpoint = lambda task, model, name: f"Hey there {name} {model} {task}"
            # endpoint.__name__ = task
            if hasattr(grpcer, task):
                endpoint = getattr(grpcer, task)
            else:
                endpoint = grpcer.ToDo

            route_path = f"/pipeline/{task}/model/caikit/{model}"
            router.add_api_route(path=route_path, endpoint=endpoint)
            route_path = f"/models/caikit/{model}"
            router.add_api_route(path=route_path, endpoint=endpoint)

    route_path = "/pipeline/{task:str}/model/{model:str}"
    lam = lambda task, model, name: f"Hey there {name} {model} {task}"  # Echo for testing
    lam.__name__ = "TODO: Route for future generic any task handler"
    router.add_api_route(path=route_path, methods=["POST", "GET"], endpoint=lam)
    route_path = "/models/{model}"
    endpoint = lambda model, name: {"result": f"Hey there {name} {model}"}  # Echo for testing
    endpoint.__name__ = "TODO: route for any model"
    router.add_api_route(path=route_path, methods=["POST", "GET"], endpoint=endpoint, response_description="your results may vary")

    app.include_router(router)


if __name__ == "__main__":
    uvicorn.run("restapi:app", port=5000)
