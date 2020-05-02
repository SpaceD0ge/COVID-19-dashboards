# Tools for the COVID-19 information processing.
Simple up to date data retrieval tools.

## Requirements

python 3.5+

internet access

## Getting started

```python
predictions = [
    pd.read_csv('.submissions/seir3.csv'),
    pd.read_csv('.submissions/seir2.csv')    
]
team_names = [
    'Gork',
    'Mork'
]
start_date = "2020-04-27"
end_date = "2020-05-01"
```
Change this code in the app.py file to process your own predictions.

## Serving

[Follow this tutorial](https://www.digitalocean.com/community/tutorials/how-to-serve-flask-applications-with-gunicorn-and-nginx-on-ubuntu-18-04)

[Or this one](https://markobigdata.com/2019/12/05/nginx-gunicorn-and-dash-on-centos/)