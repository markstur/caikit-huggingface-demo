import os

import grpc
from caikit import get_config
from caikit.core import ModuleConfig
from caikit.runtime.service_factory import ServicePackageFactory
from google.protobuf.descriptor_pool import DescriptorPool
from grpc_reflection.v1alpha.proto_reflection_descriptor_database import ProtoReflectionDescriptorDatabase


class Grpcer:
    def __init__(self, request, predict, model) -> None:
        self.request = request
        self.predict = predict
        self.model = model

    def ObjectDetection(self, encoded_bytes_or_url):
        response = self.predict(
            self.request(encoded_bytes_or_url=encoded_bytes_or_url),
            metadata=[("mm-model-id", self.model)],
        )

        results = list(response.objects)
        results.sort(
            key=lambda c: c.score, reverse=True
        )  # Sort so numbering will be in desc score order

        labels = {}
        counter = {}
        for result in results:
            label = result.label
            counter[label] = (
                    counter.get(label, 0) + 1
            )  # Count for repeated objects of same class
            key = (
                label if counter[label] == 1 else f"{label}-{counter[label]}"
            )  # Append counter when repeated
            labels[key] = {"score": result.score,
                           "box": {
                               "xmin": result.box.xmin,
                               "ymin": result.box.ymin,
                               "xmax": result.box.xmax,
                               "ymax": result.box.ymax,
                           }}

        return labels  # , image

    def ImageClassification(self, encoded_bytes):
        response = self.predict(
            self.request(encoded_bytes_or_url=encoded_bytes),
            metadata=[("mm-model-id", self.model)],
        )
        return {x.class_name: x.confidence for x in response.classes}

    def Sentiment(self, text_in: str):
        predict = client_stub.SentimentPredict
        request = inference_service.messages.SentimentRequest
        response = predict(
            request(text_in=text_in), metadata=[("mm-model-id", self.model)]
        )
        return {"classes": [{"class_name": x.class_name, "confidence": x.confidence} for x in response.classes]}

    # def Sample(self, name: str) -> SampleOutputType:
    def Sample(self, name: str):
        # req = self.request(sample_input=SampleInputType(name=name))
        # resp = self.predict(sample_input=req, throw=False, metadata=[("mm-model-id", self.model)])
        # ret = self.SampleOutputType(greeting="foo")
        return f"Sorry {name} but I cannot handle Sample input and output types"

    def ToDo(self, model, text_in, chat):
        if text_in:
            response = self.predict(
                self.request(text_in=text_in), metadata=[("mm-model-id", model)]
            ).text
            chat.append((text_in, response))
        return "", chat  # '' is to clear input


def get_module_models(model_manager=None) -> dict:
    """
    Determine the modules and models that are loaded (so the UI only shows what is available).
    Tries to use model manager to keep backend/frontend in sync, but can run independently by
    using the same configs that the backend would use (library runtime config.yml and model config.yml files.

    Parameters
    ----------
    model_manager - if set this allows us to ask the ModelManager for loaded models (and details) instead of crawling configs and assuming the backend used the same configs.

    Returns
    -------
    dict - mapping loaded module module_ids to loaded model model_ids

    """
    if model_manager:
        model_modules = {
            k: v.module().metadata["module_id"]
            for (k, v) in model_manager.loaded_models.items()
        }
    else:
        model_modules = {}
        # Without loading models build a map from local_models_dir configs
        local_models_path = get_config().runtime.local_models_dir
        if os.path.exists(local_models_path):
            for model_id in os.listdir(local_models_path):
                try:
                    # Use the file name as the model id
                    model_path = os.path.join(local_models_path, model_id)
                    config = ModuleConfig.load(model_path)
                    model_modules[model_id] = config.module_id
                except Exception:  # pylint: disable=broad-exception-caught
                    # Broad exception, but want to ignore any unusable dirs/files
                    pass

    flipped = {}  # map module_id to list of model_ids
    for k, v in model_modules.items():
        flipped[v] = flipped.get(v, []) + [k]
    return flipped


def get_grpc_things():
    global inference_service, client_stub, reflection_db, desc_pool
    inference_service = ServicePackageFactory().get_service_package(
        ServicePackageFactory.ServiceType.INFERENCE,
    )
    channel = grpc.insecure_channel(
        "localhost:8085",  # target TODO: target
        options=[
            ('grpc.max_send_message_length', -1),
            ('grpc.max_receive_message_length', -1),
        ],
    )
    client_stub = inference_service.stub_class(channel)
    reflection_db = ProtoReflectionDescriptorDatabase(channel)
    desc_pool = DescriptorPool(reflection_db)
    services = [
        x for x in reflection_db.get_services() if x.startswith("caikit.runtime.")
    ]
    if len(services) != 1:
        print(f"Error: Expected 1 caikit.runtime service, but found {len(services)}.")
    service_name = services[0]
    service_prefix, _, _ = service_name.rpartition(".")
    service_descriptor = desc_pool.FindServiceByName(service_name)
    methods = service_descriptor.methods_by_name
    return service_prefix, methods, desc_pool, client_stub
