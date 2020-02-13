import pytest

import warnings

warnings.filterwarnings("ignore", category=DeprecationWarning)

pytest.main()

# To run without warnings, execute this is command line in crowd_sorting dir:
# python -m pytest -W ignore::DeprecationWarnings