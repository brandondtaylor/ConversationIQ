"""
Setup script for ConversationIQ
"""
from setuptools import setup, find_packages
from pathlib import Path

# Read README for long description
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text(encoding="utf-8") if readme_file.exists() else ""

setup(
    name="conversationiq",
    version="0.1.0",
    description="AI-powered chat response evaluation platform using TinyTroupe virtual agents",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Your Name",
    author_email="your.email@example.com",
    url="https://github.com/yourusername/conversationiq",
    packages=find_packages(),
    python_requires=">=3.10",
    install_requires=[
        "python-dotenv>=1.0.0",
        "pydantic>=2.0.0",
        "pydantic-settings>=2.0.0",
        "tinytroupe>=0.1.0",
        "httpx>=0.25.0",
        "requests>=2.31.0",
        "typer>=0.9.0",
        "rich>=13.0.0",
        "click>=8.1.0",
        "pandas>=2.0.0",
        "openpyxl>=3.1.0",
        "sqlalchemy>=2.0.0",
        "alembic>=1.12.0",
        "python-dateutil>=2.8.0",
        "pyyaml>=6.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-asyncio>=0.21.0",
            "pytest-cov>=4.1.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.5.0",
        ]
    },
    entry_points={
        "console_scripts": [
            "conversationiq=src.ui.cli:main",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    keywords="ai chat evaluation testing tinytroupe agents personas",
    project_urls={
        "Bug Reports": "https://github.com/yourusername/conversationiq/issues",
        "Source": "https://github.com/yourusername/conversationiq",
    },
)
