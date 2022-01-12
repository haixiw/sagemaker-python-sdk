# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"). You
# may not use this file except in compliance with the License. A copy of
# the License is located at
#
#     http://aws.amazon.com/apache2.0/
#
# or in the "license" file accompanying this file. This file is
# distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF
# ANY KIND, either express or implied. See the License for the specific
# language governing permissions and limitations under the License.
from __future__ import absolute_import


from tests.integ.sagemaker.jumpstart.retrieve_uri.inference import (
    EndpointInvoker,
    InferenceJobLauncher,
)
from sagemaker import image_uris
from sagemaker import script_uris
from sagemaker import model_uris

from tests.integ.sagemaker.jumpstart.retrieve_uri.constants import InferenceTabularDataname

from tests.integ.sagemaker.jumpstart.retrieve_uri.utils import (
    download_inference_assets,
    get_tabular_data,
)


def test_jumpstart_inference_retrieve_functions(setup):

    model_id, model_version = "catboost-classification-model", "1.0.0"
    instance_type = "ml.m5.xlarge"

    print("Starting inference...")

    image_uri = image_uris.retrieve(
        region=None,
        framework=None,
        image_scope="inference",
        model_id=model_id,
        model_version=model_version,
        instance_type=instance_type,
    )

    script_uri = script_uris.retrieve(
        model_id=model_id, model_version=model_version, script_scope="inference"
    )

    model_uri = model_uris.retrieve(
        model_id=model_id, model_version=model_version, model_scope="inference"
    )

    inference_job = InferenceJobLauncher(
        image_uri=image_uri,
        script_uri=script_uri,
        model_uri=model_uri,
        instance_type=instance_type,
        base_name="catboost",
    )

    inference_job.launch_inference_job()
    inference_job.wait_until_endpoint_in_service()

    endpoint_invoker = EndpointInvoker(
        endpoint_name=inference_job.endpoint_name,
    )

    download_inference_assets()
    ground_truth_label, features = get_tabular_data(InferenceTabularDataname.MULTICLASS)

    response = endpoint_invoker.invoke_tabular_endpoint(features)

    assert response is not None
