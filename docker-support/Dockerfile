FROM public.registry.u-hopper.com/python:3.8 as builder

ARG PIP_CONF_DOCKER


RUN mkdir -p /root/.config/pip
RUN echo "${PIP_CONF_DOCKER}" > /root/.config/pip/pip.conf
ENV PIP_CONFIG_FILE /root/.config/pip/pip.conf


RUN pip install --upgrade pip
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt


FROM public.registry.u-hopper.com/python:3.8

RUN mkdir /var/www


COPY --from=builder /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH

RUN pip install coverage pytest-cov anybadge PyYAML

ADD  src/ /scripts/
ADD  documentation/ /documentation/

WORKDIR /scripts

COPY  run.sh .

COPY  run_survey.sh .
COPY  run_worker.sh .

ENV DOCUMENTATION_PATH /documentation

ADD  test/ /scripts/test/
COPY  run_tests.sh .
COPY  test.sh .

COPY  run_test_coverage.sh .
COPY  .coveragerc .

RUN pip install uWSGI==2.0.19.1


# Collect all Django static files
COPY  uwsgi.ini .
RUN python manage.py collectstatic --noinput

ENV PYTHONPATH /scripts

ARG GIT_REF

# Specific runners for each defined service need to be called explicitly
