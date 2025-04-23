from langchain_huggingface import HuggingFaceEmbeddings

EmbeddingsModel = HuggingFaceEmbeddings

def get_embedding_model(
    model_id: str,
    device: str = "cpu",
) -> EmbeddingsModel:
    
    return get_huggingface_embedding_model(
        model_id=model_id,
        device=device
    )

def get_huggingface_embedding_model(
    model_id: str,
    device: str
) -> HuggingFaceEmbeddings:
    """
    Load a SentenceTransformer model.

    Args:
        model_id (str): The ID of the model to load.
        device (str): The device to use for loading the model ('cpu' or 'cuda').

    Returns:
        SentenceTransformer: The loaded SentenceTransformer model.
    """
    return HuggingFaceEmbeddings(
        model_name=model_id,
        model_kwargs={
            "device": device,
            "trust_remote_code": True,
        }
    )