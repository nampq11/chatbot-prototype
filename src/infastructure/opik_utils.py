import os

import opik
from loguru import logger
from opik.configurator.configure import OpikConfigurator

from src.config import Config

config = Config()

def configure() -> None:
    if config.comet.API_KEY and config.comet.PROJECT:
        try:
            client = OpikConfigurator(api_key=config.comet.API_KEY)
            default_workspace = client._get_default_workspace()
        except Exception:
            logger.warning(
                "Default workspace not found. Setting workspace to None and enabling interactive mode."
            )
            default_workspace = None

        os.environ["OPIK_PROJECT_NAME"] = config.comet.PROJECT

        try:
            opik.configure(
                api_key=config.comet.API_KEY,
                workspace=default_workspace,
                use_local=False,
                force=True,
            )
            logger.info(
                f"Opik configured successfully using workspace '{default_workspace}'"
            )
        except Exception:
            logger.warning(
                "COMET_API_KEY and COMET_PROJECT are not set. Set them to enable prompt monitoring with Opik (powered by Comet ML)."
            )
    
    def get_dataset(name: str) -> opik.Dataset | None:
        try:
            dataset = opik.Dataset(name=name)
            return dataset
        except Exception as e:
            logger.warning(f"Error creating dataset: {e}")
            dataset = None
        
        return dataset
    
    def create_dataset(name: str, description: str, items: list[dict]) -> opik.Dataset:
        client = opik.Opik()

        client.delete_dataset(name=name)

        dataset = client.create_dataset(name=name, description=description)
        dataset.insert(items)

        return dataset