FROM python:2.7

WORKDIR /usr/src/app
COPY code .

RUN apt-get update
RUN apt-get -y install npm
RUN npm install -g bower
RUN ln -s /usr/bin/nodejs /usr/bin/node
RUN bower install --allow-root
RUN pip install -r requirements.txt


# fix pbr-based packages versioning
#RUN echo "__version__ = '0.0.1'" | tee toscaparser/__init__.py | tee translator/__init__.py
# delete the copy of the database inside the container (if exists)
RUN rm -f db.sqlite3

RUN python manage.py makemigrations sf_user projecthandler instancehandler vimhandler
RUN python manage.py migrate

RUN python manage.py shell -c "from projecthandler.osm_model import OsmProject; from sf_user.models import CustomUser; CustomUser.objects.create_superuser('admin', 'admin'); admin = CustomUser.objects.get(username='admin'); OsmProject.create_project('admin',admin,True, 'project admin','')"


EXPOSE 80
CMD ["python", "manage.py", "runserver", "0.0.0.0:80"]
