FROM rocker/tidyverse:latest
LABEL MAINTAINER KBase Developer

RUN apt-get update -y && apt-get upgrade -y && \
    apt-get -y install --no-install-recommends --no-install-suggests \
    ca-certificates software-properties-common \
    libssl-dev libcurl4-openssl-dev gnupg2 gnupg1 libbz2-dev \
    python3 python3-pip python3-dev uwsgi

# install R dependencies, checking that each is installed correctly
RUN R -e "\
    packages <- c('openssl', 'httr', 'remotes', 'broom', 'crayon', 'glue', 'gt', 'patchwork', 'scales', 'dplyr', 'ggrepel', 'ggridges', 'purrr', 'S7', 'stringr', 'tidyr'); \
    repos <- 'http://cran.rstudio.com/'; \
    install.packages(packages, dependencies=TRUE, repos=repos); \
    missing_packages <- packages[!packages %in% rownames(installed.packages())]; \
    if(length(missing_packages) > 0) { \
    cat('Failed to install: ', paste(missing_packages, collapse=', '), '\\n'); \
    quit(status = 1); \
    }"

# install python requirements
WORKDIR /tmp
COPY ./requirements.txt /tmp/requirements.txt
COPY ./requirements-test.txt /tmp/requirements-test.txt
RUN ln -s /usr/bin/python3 /usr/bin/python && \
    pip install --upgrade pip && \
    cat /tmp/requirements.txt | sed -e '/^\s*#.*$/d' -e '/^\s*$/d' | xargs -n 1 pip install && \
    cat /tmp/requirements-test.txt | sed -e '/^\s*#.*$/d' -e '/^\s*$/d' | xargs -n 1 pip install

# moving qSIP2 package to the bottom
RUN R -e "remotes::install_github('jeffkimbrel/qSIP2@0bf23f7'); \
    if (!('qSIP2' %in% rownames(installed.packages()))) { quit(status = 1); }; \
    .libPaths();"

# copy in the kb_qsip repo
COPY ./ /kb/module
WORKDIR /kb/module

# ensure all scripts are executable
RUN chmod +x ./scripts/*.sh && chmod +x ./test/run_tests.sh && chmod +x ./bin/*.sh && \
    mkdir -p /kb/module/work && \
    chmod -R a+rw /kb/module

# Entrypoint
ENTRYPOINT [ "./scripts/entrypoint.sh" ]
CMD [ ]
