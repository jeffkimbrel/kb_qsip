FROM rocker/tidyverse:latest
LABEL MAINTAINER KBase Developer

RUN apt-get update -y && apt-get upgrade -y && \
    apt-get -y install --no-install-recommends --no-install-suggests \
    ca-certificates software-properties-common gnupg2 gnupg1 python3 python3-pip uwsgi \
    libssl-dev libcurl4-openssl-dev python3-dev libbz2-dev
# && apt-key adv --keyserver keyserver.ubuntu.com --recv-keys E298A3A825C0D65DFD57CBB651716619E084DAB9 \
# && add-apt-repository 'deb https://cloud.r-project.org/bin/linux/ubuntu focal-cran40/'
# && apt-get update -qq && apt-get -y install r-base r-base-dev

RUN R -e "install.packages('openssl', repos='http://cran.rstudio.com/'); if (!('openssl' %in% installed.packages())) { quit(status = 1) }"
RUN R -e "install.packages('httr', repos='http://cran.rstudio.com/'); if (!('httr' %in% installed.packages())) { quit(status = 1) }"
RUN R -e "install.packages('remotes', repos='http://cran.rstudio.com/'); if (!('remotes' %in% installed.packages())) { quit(status = 1) }"

## install qSIP2 dependencies from CRAN (this won't catch failures though)
RUN R -e "install.packages(c('broom', 'crayon', 'glue', 'gt', 'patchwork', 'scales'),dependencies=TRUE, repos='http://cran.rstudio.com/')"
RUN R -e "install.packages(c('dplyr', 'ggrepel', 'ggridges', 'purrr', 'S7', 'stringr', 'tidyr'),dependencies=TRUE, repos='http://cran.rstudio.com/')"

RUN R -e "remotes::install_github('jeffkimbrel/qSIP2@6edfa61'); if (!('qSIP2' %in% installed.packages())) { quit(status = 1) }"
RUN R -e ".libPaths()"

# install python requirements
COPY ./requirements.txt /kb/module/requirements.txt
COPY ./requirements-test.txt /kb/module/requirements-test.txt
WORKDIR /kb/module
RUN ln -s /usr/bin/python3 /usr/bin/python && \
    pip install --upgrade pip && \
    cat requirements.txt | sed -e '/^\s*#.*$/d' -e '/^\s*$/d' | xargs -n 1 pip install && \
    cat requirements-test.txt | sed -e '/^\s*#.*$/d' -e '/^\s*$/d' | xargs -n 1 pip install && \
    mkdir -p /kb/module/work && \
    chmod -R a+rw /kb/module

COPY ./ /kb/module
WORKDIR /kb/module
# ensure all scripts are executable
RUN chmod +x ./scripts/*.sh && chmod +x ./test/run_tests.sh && chmod +x ./bin/*.sh

# Entrypoint
ENTRYPOINT [ "./scripts/entrypoint.sh" ]
CMD [ ]
