#Docker configuration for containerizing the app
#this is a Dockerfile (recipe) for containerizing the app
    #if there were more build dependecies, a multistage build to make the final image smaller

#use a lightweight Python image
FROM python:3.12-slim
    #regularly update base image to ensure latest security patches
    #note python:3.9-slim has a Critical CVE with an EPSS score .1 that was fixed in later versions

#set working directory inside the container
WORKDIR /app

#copy dependencies and install them
COPY requirements.txt requirements.txt
#requirements.txt is written twice to indicate to and from
RUN pip install --no-cache-dir -r requirements.txt

#copy the app code into the container
COPY . . 

#set the enivironment variable to allow Flask to run in a container
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0

#expose the port the Flask app will run on
EXPOSE 5000

#command to run the Flask app
CMD ["python", "app.py"]
