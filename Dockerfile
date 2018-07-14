FROM coinstac/coinstac-base-python-stream

# Set the working directory
WORKDIR /computation

# Copy the current directory contents into the container
# COPY requirements.txt /computation

#RUN apt-get update && apt-get install -y r-base

# Install any needed packages specified in requirements.txt
# RUN pip install -r requirements.txt

# https://github.com/rocker-org/rocker/blob/b9f9289ef27f07dc2f2b64d56d12646770b9b233/r-base/Dockerfile
RUN apt-get update \ 
	&& apt-get install -y --no-install-recommends \
	#	ed \
	#	less \
	#	locales \
	#	vim-tiny \
		wget \
		ca-certificates \
	#	fonts-texgyre \
	&& rm -rf /var/lib/apt/lists/*

## Use Debian unstable via pinning -- new style via APT::Default-Release
RUN echo "deb http://http.debian.net/debian sid main" > /etc/apt/sources.list.d/debian-unstable.list \
        && echo 'APT::Default-Release "testing";' > /etc/apt/apt.conf.d/default 

ENV R_BASE_VERSION 3.5.1

RUN apt-get update \
	&& apt-get install -t unstable -y --no-install-recommends \
		r-base=${R_BASE_VERSION}-* \
		r-base-dev=${R_BASE_VERSION}-* \
        && echo 'options(repos = c(CRAN = "https://cloud.r-project.org/"))' >> /etc/R/Rprofile.site \
    	&& rm -rf /tmp/downloaded_packages/ /tmp/*.rds \
    	&& rm -rf /var/lib/apt/lists/*

RUN Rscript -e "install.packages(c('ppcor', 'moments', 'matrixStats'))"

# Copy the current directory contents into the container
COPY . /computation