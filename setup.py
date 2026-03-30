from setuptools import find_packages, setup

setup(
    name="docquest",
    version="2.0.0",
    author="vishal m",
    author_email="vishalmuthukumar3@gmail.com",
    packages=find_packages(),
    install_requires=[
        "fastapi",
        "uvicorn",
        "python-multipart",
        "pydantic",
        "pydantic-settings",
        "python-dotenv",
        "sqlalchemy",
        "psycopg2-binary",
        "llama-index",
        "llama-index-llms-gemini",
        "llama-index-embeddings-gemini",
        "google-generativeai",
        "PyMuPDF",
        "python-docx",
    ],

)