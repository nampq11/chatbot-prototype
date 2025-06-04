import os
import argparse
from huggingface_hub import login, snapshot_download
from typing import Literal
from sentence_transformers import SentenceTransformer
from pydantic import BaseModel

DATA_PATH = "/home/nampq/projects/chatbot-prototype/api/models"
# HUGGINGFACE_ACCESS_TOKEN = os.getenv('HUGGINGFACE_ACCESS_TOKEN')

# login(token=HUGGINGFACE_ACCESS_TOKEN)

class ModelConfig(BaseModel):
    model_id : str
    mode: Literal['snapshot', 'model'] = 'model'

    class Config:
        protected_namespaces = ()

def download(config: ModelConfig):
    try:

        if config.mode == 'snapshot':
            snapshot_download(
                config.model_id,
                revision='main',
                ignore_patterns=['*.git*', '*README.md'],
                local_dir=os.path.join(DATA_PATH, config.model_id)
            )
        else:
            model = SentenceTransformer(
                config.model_id,
                trust_remote_code=True,
            )
            model.save(os.path.join(DATA_PATH, config.model_id))
    except Exception as e:
        raise e
    
def run():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-i', '--input',
        help='model id to download',
        required=True,
    )
    parser.add_argument(
        '-m', '--mode',
        help='mode to download',
        default='model',
    )

    args = parser.parse_args()
    config = ModelConfig(
        model_id=args.input,
        mode=args.mode
    )


    download(config)

if __name__ == '__main__':
    run()