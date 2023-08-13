# Python base image
FROM python:3.8-slim

# Set the current working directory to /noccodeproject.
WORKDIR /noccodeproject

# Copy the requirements to the WORKDIR 
COPY ./requirements.txt ./

# Upgrade pip and install dependencies
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Copy project contents to the WORKDIR
COPY . .

# To copy specific directory
# COPY ./data ./data

# Remove '#' to run the specific python script
CMD [ "python", "./src/preprocess.py" ]
# CMD [ "python", "./src/NOC_Code_Auto.py" ]
# CMD [ "python", "./src/result_analysis.py" ]
