# Running E-Commerce Dashboard✨
SC data: https: [Dataset](//www.kaggle.com/datasets/olistbr/brazilian-ecommerce).
## Settup virtual environment dengan Miniconda/Anaconda
```
conda create --name main-ds python=3.12
conda activate main-ds
pip install -r requirements.txt
```
## Settup enviroment shell/terminal (mengarahkan ke folder directory yang dibuat)
```
mkdir proyek_analisis_data
cd proyek_analisis_data
pipenv install
pipenv shell
pip install -r requirements.txt
```
## Running dashboard di local
```
streamlit run dashboard/dashboard.py
```
https://keysyaaz.streamlit.app/
