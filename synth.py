# Copyright 2018 Google LLC
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

"""This script is used to synthesize generated parts of this library."""

import synthtool as s
import synthtool.gcp as gcp
from synthtool.languages import python
import logging

AUTOSYNTH_MULTIPLE_COMMITS = True

logging.basicConfig(level=logging.DEBUG)

gapic = gcp.GAPICBazel()
common = gcp.CommonTemplates()

# ----------------------------------------------------------------------------
# Generate monitoring GAPIC layer
# ----------------------------------------------------------------------------
v3_library = gapic.py_library(
    service="monitoring",
    version="v3",
    bazel_target="//google/monitoring/v3:monitoring-v3-py",
    include_protos=True,
    proto_output_path="google/cloud/monitoring_v3/proto"
)

# don't copy nox.py, setup.py, README.rst, docs/index.rst
excludes = ["nox.py", "setup.py", "README.rst", "docs/index.rst"]
s.move(v3_library, excludes=excludes)

# Synth hack due to googleapis and python-api-common-protos out of sync.
for pattern in [
    "monitored_resource_types=\['monitored_resource_types_value'\],",
    "assert response.monitored_resource_types == \['monitored_resource_types_value'\]",
    "launch_stage=launch_stage.LaunchStage.UNIMPLEMENTED,",
    "assert response.launch_stage == launch_stage.LaunchStage.UNIMPLEMENTED",
]:
    s.replace(
        "tests/unit/gapic/monitoring_v3/test_*.py",
        pattern,
        ""
    )

s.replace(
    "google/cloud/**/*.py",
    "google.monitoring",
    "google.cloud.monitoring"
)

# Synth hack due to microgenerator uses "type_" while api-common-protos uses "type".
for file in ["test_uptime_check_service.py", "test_metric_service.py"]:
    s.replace(
        f"tests/unit/gapic/monitoring_v3/{file}",
        "type_",
        "type"
    )

# ----------------------------------------------------------------------------
# Add templated files
# ----------------------------------------------------------------------------
# ----------------------------------------------------------------------------
# Add templated files
# ----------------------------------------------------------------------------
templated_files = common.py_library(
    samples=True,  # set to True only if there are samples
    microgenerator=True,
)
s.move(templated_files, excludes=[".coveragerc"])  # microgenerator has a good .coveragerc file

# ----------------------------------------------------------------------------
# Samples templates
# ----------------------------------------------------------------------------
python.py_samples(skip_readmes=True)


# TODO(busunkim): Use latest sphinx after microgenerator transition
s.replace("noxfile.py", """['"]sphinx['"]""", '"sphinx<3.0.0"')


s.shell.run(["nox", "-s", "blacken"], hide_output=False)
