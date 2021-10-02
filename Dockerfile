FROM signate/sim_env:latest

# install zip
RUN apt-get update && apt-get install -y zip

# install additional libraries
RUN mkdir /temp
WORKDIR /temp
ADD requirements.txt /temp/
RUN source /root/.zshrc && \
    pip install -r requirements.txt

# set tdn conf
WORKDIR /code
ADD tdn_lisb.conf /code/
RUN cp tdn_lisb.conf /etc/ld.so.conf.d/
