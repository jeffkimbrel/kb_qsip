FROM rocker/tidyverse:latest
MAINTAINER KBase Developer
# -----------------------------------------
# In this section, you can install any system dependencies required
# to run your App.  For instance, you could place an apt-get update or
# install line here, a git checkout to download code, or run any other
# installation scripts.

# RUN R -e "install.packages('openssl')"
# RUN R -e "install.packages('httr')"
RUN R -e "install.packages('remotes')"
RUN R -e "remotes::install_github('jeffkimbrel/qSIP2')"

# install python and packages
RUN apt-get update
RUN /rocker_scripts/install_python.sh

# Setup virtualenv in this path
ENV VIRTUAL_ENV=/opt/venv
ENV PATH=${VIRTUAL_ENV}/bin:${PATH}
RUN python3 -m venv ${VIRTUAL_ENV}

RUN python -V

RUN pip install pandas
RUN pip install rpy2==3.5.12

# -----------------------------------------

COPY ./ /kb/module
RUN mkdir -p /kb/module/work
RUN chmod -R a+rw /kb/module

WORKDIR /kb/module

RUN make all

ENTRYPOINT [ "./scripts/entrypoint.sh" ]

CMD [ ]
