from setuptools import setup, find_packages

setup(
    name="escargot",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "openai",
        "backoff",
        "flask",
        "chromadb",
        "weaviate-client",
        "gqlalchemy"
    ],
    python_requires=">=3.8",
) 