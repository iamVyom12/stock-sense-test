## Commands

```bash
venv\Scripts\activate
pytest --alluredir=allure-results
allure generate allure-results --clean -o allure-report
allure open allure-report
