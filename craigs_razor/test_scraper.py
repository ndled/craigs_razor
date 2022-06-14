from unittest.mock import patch

def test_cl_requester():
    with patch("requests.get") as mock_get:
        mock_get.return_value.text