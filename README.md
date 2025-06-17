## Setup project root directory to your Python path

```
export PYTHONPATH=/path/to/projectRecon
```

- Example:

```
export PYTHONPATH=$PYTHONPATH:/root/pr/projectRecon
```

## Help:

### Python version 3.8+ required
- Install python 3.8 in amazon linux:

```
sudo amazon-linux-extras enable python3.8
sudo yum install python3.8
python3.8 --version

sudo alternatives --install /usr/bin/python3 python3 /usr/bin/python3.8 1
sudo alternatives --config python3  # Select the new version if prompted
python3 --version
```

- Install psycopg2-binary

```
sudo yum install gcc python3-devel postgresql-devel
pip3 install psycopg2-binary
```

- Run

```
uvicorn main:app --host 0.0.0.0 --port 54755
vite --host --port 54754
```

- Remove __pychache__ dir recursively from each sub dir

```
find . -type d -name '__pycache__' -exec rm -r {} +
```