export EB_MAX_RETRIES=100
export EB_BASE_URL=http://10.154.81.14:8868/ernie-foundry/v1

export EB_API_TYPE="aistudio"
export EB_ACCESS_TOKEN="1dc43e5843cfb51b7b41ba766aff2372cf2f3ccb"

export AISTUDIO_HUB_BASE_URL=http://sandbox-aistudio-hub.baidu.com

# python -m pytest -s -v tests/integration_tests/apihub/test_doc_rm_bnd.py
python -m pytest -s -v /Users/tanzhehao/Documents/ERINE/ERNIE-Bot-SDK/erniebot-agent/tests/integration_tests/apihub/test_pp_models.py::TestPPRemoteTool::test_pp_matting