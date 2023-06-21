import pandas as pd
import numpy as np
import openai

openai.api_key = "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"

datafile_path = "comidas_embeddings.csv"

df = pd.read_csv(datafile_path)
df["embedding"] = df.embedding.apply(eval).apply(np.array)

from openai.embeddings_utils import get_embedding, cosine_similarity

# search through the reviews for a specific product
def search_reviews(df, product_description, n=3, pprint=True):
    product_embedding = get_embedding(
        product_description,
        engine="text-embedding-ada-002"
    )
    df["similarity"] = df.embedding.apply(lambda x: cosine_similarity(x, product_embedding))

    results = (
        df.sort_values("similarity", ascending=False)
        .head(n)
        .combined.str.replace("Platos: ", "")
        .str.replace("; Calorias:", ": ")
    )

    pruebas = (
        df.sort_values("similarity", ascending=False)
        .head(n).Calorias
    )

    if pprint:
        for r in results:
            print(r[:200])
            print()


    return pruebas.iloc[0]

print(search_reviews(df,"ceviche",n=3))