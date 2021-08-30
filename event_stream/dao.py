from typing import List
from enum import Enum
import datetime
from typing import Optional

from event_stream.models.model import *
from pydantic import BaseModel
import databases
import sqlalchemy
from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy import Table, Column, MetaData, create_engine
from enum import Enum
import os
import urllib
import event_stream.models
from sqlalchemy.orm import sessionmaker


class DB(object):

    def __init__(self):
        host_server = os.environ.get('POSTGRES_HOST', 'localhost')
        db_server_port = urllib.parse.quote_plus(str(os.environ.get('POSTGRES_PORT', '5432')))
        database_name = os.environ.get('POSTGRES_DB', 'fastapi')
        db_username = urllib.parse.quote_plus(str(os.environ.get('POSTGRES_USER', 'postgres')))
        db_password = urllib.parse.quote_plus(str(os.environ.get('POSTGRES_PASSWORD', 'secret')))
        # ssl_mode = urllib.parse.quote_plus(str(os.environ.get('ssl_mode','prefer')))
        DATABASE_URL = 'postgresql://{}:{}@{}:{}/{}'.format(db_username, db_password, host_server,
                                                            db_server_port, database_name)

        engine = create_engine(DATABASE_URL)
        Base.metadata.create_all(engine)
        # database = databases.Database(DATABASE_URL)

        Session = sessionmaker(bind=engine)
        self.session = Session()

    def save_object(self, obj):
        self.session.add(obj)
        self.session.commit()
        self.session.refresh(obj)
        return obj

    def get_object(self, table, key):
        return self.session.query(table).get(key)

    def save_if_not_exist(self, obj, table, key):
        obj_db = self.get_object(table, key)
        if not obj_db:
            return self.save_object(obj)
        else:
            return obj_db

    def save_publication(self, publication_data):
        publication = Publications(**publication_data)
        publication = self.save_object(publication)

        authors = publication_data['authors']
        for author_data in authors:
            author = Authors(**author_data)
            author = self.save_if_not_exist(author, Authors, {'normalized_name': author.normalized_name})

            publication_authors = PublicationAuthors({'author_id': author.id, 'publication_id': publication.id})
            self.save_object(publication_authors)

        sources = publication_data['sources']
        for sources_data in sources:
            source = Sources(**sources_data)
            source = self.save_if_not_exist(source, Sources, {'title': source.title})
            publication_sources = PublicationSources({'source_id': source.id, 'publication_id': publication.id})
            self.save_object(publication_sources)

        fields_of_study = publication_data['fieldOfStudy']
        for fos_data in fields_of_study:
            fos = FieldOfStudy(**fos_data)
            fos = self.save_if_not_exist(fos, FieldOfStudy, {'normalized_name': fos.normalized_name})
            publication_fos = PublicationFieldsOfStudy({'field_of_study_id': fos.id, 'publication_id': publication.id})
            self.save_object(publication_fos)

        return publication
        # todo
        # publicationCitations = PublicationCitations()
        # publicationReferences = PublicationReferences(**author_data)
