from setuptools import setup, find_packages

setup(
    name="dagobah_email",
    version="0.1.0",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    install_requires=[
        # Add your dependencies here, or use requirements.txt
    ],
    python_requires=">=3.8",
) 