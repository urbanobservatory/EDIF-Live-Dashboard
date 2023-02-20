from dotenv import load_dotenv
from pathlib import Path

dotenv_path = Path('/env/.env')
load_dotenv(dotenv_path=dotenv_path)
import os
import json

json.dump(dict(os.environ.items()),open('/code/env.json','w'))

