# Setup Dev-Env

## 1. Fix paths
After zip-file extraction the `install/core/Windows.cfg` file needs to be adopted
with the proper user-path according to your local system.

The following steps are assumed to be executed from within the previously extracted directory.

## 2. Setup virtualenv
Then create a virtualenv with the shotgun python.
```
"c:\Program Files\Shotgun\Python3\python.exe" -m venv .venv
```
Alternatively let VSCode create the .venv by directing it to the shotgun python executable.

If you have issues with installing pip you can use this alternate steps
"c:\Program Files\Shotgun\Python3\python.exe" -m venv --without-pip .venv
.venv\Scripts\activate
wget https://bootstrap.pypa.io/get-pip.py
python get-pip.py

## 3. Install additional python libs

```
.venv/Scripts/pip.exe install -r config/dev/requirements.txt
```

## 4. Download Apps and Cache

```
tank.bat cache_apps
```

## 5. Ready to start

Now it should be possible to run the publish app from within the "Desktop Tool" and through the `config/dev/start_engine.py` script. The latter should help for easy debugging and scripting.

You can specify the project id through `config/dev/start_engine.py <id>`. If not specified a hardcoded ID is used. 