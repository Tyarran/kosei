FROM rcommande/alpine-pyenv

# Pyenv
RUN pyenv install 3.6.10
RUN pyenv install 3.7.6
RUN pyenv install 3.8.1
RUN pyenv local 3.6.10 3.7.6 3.8.1

RUN mkdir /code
WORKDIR /code

# Pipx
RUN sh /entrypoint.sh pip3.8 install pipx
ENV PATH "$PATH:/root/.pyenv/versions/3.8.1/bin/:/root/.local/bin"
RUN pipx ensurepath

# Python tools
RUN pipx install poetry 
RUN pipx install black 
RUN pipx install tox 
RUN pipx install isort
RUN pipx install flake8
RUN pipx runpip flake8 install flake8-black

ENV PYTHONDONTWRITEBYTECODE 1
