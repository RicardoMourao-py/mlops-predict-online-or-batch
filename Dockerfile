FROM public.ecr.aws/lambda/python:3.10

# Copy function code
COPY . ${LAMBDA_TASK_ROOT}

# Install the function's dependencies using file requirements.txt
# from your project folder.
COPY requirements.txt .

RUN yum install -y libstdc++ cmake gcc-c++ && \
    yum clean all && \
    rm -rf /var/cache/yum

RUN pip install -r requirements.txt --target "${LAMBDA_TASK_ROOT}" --upgrade --no-cache-dir

# Set the CMD to your handler (could also be done as a parameter override outside of the Dockerfile)
CMD [ "main.handler" ]