# CS 3364 Project 1: find the most reliable ranking source.
#
# This image holds everything the program needs: a Python interpreter, the
# program, the sorting algorithms, the five source files and the tests.
# The program uses only the Python standard library, so there are no packages
# to install.
#
# Build the image (run this from the project folder):
#     docker build -t search-engine-sorting .
#
# Run the program:
#     docker run --rm search-engine-sorting
#
# Run the tests:
#     docker run --rm search-engine-sorting python -m unittest
#
# Run the program on the source files of a folder on your computer instead of
# the ones stored in the image (Linux or macOS shell; the files must be named
# source*.txt and hold one rank per line):
#     docker run --rm -v "$(pwd)/sources:/app/sources:ro" search-engine-sorting

# Official Python image, "slim" variant: Python on a minimal Debian system.
# The Python version is pinned so that every build uses the same interpreter.
# The program needs Python 3.9 or newer.
FROM python:3.14-slim

# PYTHONDONTWRITEBYTECODE=1  do not write __pycache__ folders in the container
# PYTHONUNBUFFERED=1         show the program's output immediately
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Create an ordinary user to run the program, instead of root. The program
# only reads files and prints text, so it needs no special permissions.
RUN useradd --system --no-create-home appuser

# Folder inside the image that holds the program.
WORKDIR /app

# Copy only the files the program needs. The patterns leave out everything
# else in the project folder (.git, __pycache__, the project statement, ...).
# --chown hands the copies to the user created above, so the program can read
# them whatever permissions the files have on the computer that builds the
# image. The source files come first because they change least often, which
# lets Docker reuse that step when only the code changes.
COPY --chown=appuser:appuser sources/*.txt ./sources/
COPY --chown=appuser:appuser algorithms/*.py ./algorithms/
COPY --chown=appuser:appuser tests/*.py ./tests/
COPY --chown=appuser:appuser main.py ./

# Everything from here on, and the container itself, runs as that user.
USER appuser

# Default command: run the program. A command typed after the image name in
# "docker run" replaces it (see "Run the tests" above).
CMD ["python", "main.py"]
