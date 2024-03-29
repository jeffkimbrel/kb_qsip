FROM kbase/sdkpython:3.8.0
LABEL MAINTAINER KBase Developer

RUN apt-get update -y && apt-get upgrade -y
# System dependencies
RUN apt-get update -qq && apt-get -y install --no-install-recommends --no-install-suggests \
    ca-certificates software-properties-common gnupg2 gnupg1 \
    && apt-key adv --keyserver keyserver.ubuntu.com --recv-keys E298A3A825C0D65DFD57CBB651716619E084DAB9 \
    && add-apt-repository 'deb https://cloud.r-project.org/bin/linux/ubuntu focal-cran40/' \
    && apt-get update -qq && apt-get -y install r-base r-base-dev

RUN apt-get install libssl-dev libcurl4-openssl-dev -y
RUN R -e "install.packages('openssl', repos='http://cran.rstudio.com/'); if (!('openssl' %in% installed.packages())) { quit(status = 1) }"
RUN R -e "install.packages('httr', repos='http://cran.rstudio.com/'); if (!('httr' %in% installed.packages())) { quit(status = 1) }"
RUN R -e "install.packages('remotes', repos='http://cran.rstudio.com/'); if (!('remotes' %in% installed.packages())) { quit(status = 1) }"



# Python packages
RUN pip install --upgrade pip && pip install pandas rpy2

# APP specific R stuff

## install qSIP2 dependencies from CRAN (this won't catch failures though)
RUN R -e "install.packages(c('broom', 'crayon', 'glue', 'gt', 'patchwork', 'scales'),dependencies=TRUE, repos='http://cran.rstudio.com/')"
RUN R -e "install.packages(c('dplyr', 'ggrepel', 'ggridges', 'purrr', 'S7', 'stringr', 'tidyr'),dependencies=TRUE, repos='http://cran.rstudio.com/')"

RUN R -e "remotes::install_github('jeffkimbrel/qSIP2@6edfa61'); if (!('qSIP2' %in% installed.packages())) { quit(status = 1) }"
RUN R -e ".libPaths()"


COPY ./ /kb/module
RUN pip install --upgrade pip && \
    # install the required packages
    cat requirements.txt | sed -e '/^\s*#.*$/d' -e '/^\s*$/d' | xargs -n 1 pip install && \
    # install packages for running tests
    cat requirements-test.txt | sed -e '/^\s*#.*$/d' -e '/^\s*$/d' | xargs -n 1 pip install && \
    mkdir -p /kb/module/work && \
    chmod -R a+rw /kb/module && \
    # copy the compile report to the appropriate location
    cp compile_report.json work/ && \
    chmod a+rx ./scripts/*.sh

WORKDIR /kb/module
RUN make all


# Entrypoint
ENTRYPOINT [ "./scripts/entrypoint.sh" ]
CMD [ ]
