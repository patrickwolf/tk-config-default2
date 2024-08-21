# Setup Dev-Env

## 1. Setup virtualenv
After zip-file extraction create a virtualenv with the shotgun python.
```
c:\Program Files\Shotgun\Python3\python.exe -m venv .venv
```
Alternatively let VSCode create the .venv by directing it to the shotgun python executable.

## 2. Install additional python libs

```
.venv/Scripts/pip.exe install -r config/dev/requirements.txt
```

## 3. Download Apps and Cache

```
tank.bat cache_apps
```

## 4. Ready to start

Now it should be possible to run the publish app from within the "Desktop Tool" and through the `config/dev/start_engine.py` script. The latter should help for easy debugging and scripting.

You can specify the project id through `config/dev/start_engine.py <id>`. If not specified a hardcoded ID is used. 