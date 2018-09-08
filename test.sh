#!/usr/bin/env bash

#!/usr/bin/env bash

python -m pytest

find batch_crop -name *.py | xargs pylint
find tests/src -name *.py | xargs pylint

python -m mypy batch_crop --ignore-missing-imports
