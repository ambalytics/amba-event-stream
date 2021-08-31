from event_stream.models.model import *
from sqlalchemy import Table, Column, MetaData, create_engine
import os
import urllib
import psycopg2
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker


class DAO(object):

    def __init__(self):
        host_server = os.environ.get('POSTGRES_HOST', 'postgres')
        db_server_port = urllib.parse.quote_plus(str(os.environ.get('POSTGRES_PORT', '5432')))
        database_name = os.environ.get('POSTGRES_DB', 'amba')
        db_username = urllib.parse.quote_plus(str(os.environ.get('POSTGRES_USER', 'streams')))
        db_password = urllib.parse.quote_plus(str(os.environ.get('POSTGRES_PASSWORD', 'REPLACE_ME')))

        # ssl_mode = urllib.parse.quote_plus(str(os.environ.get('ssl_mode','prefer')))
        DATABASE_URL = 'postgresql://{}:{}@{}:{}/{}'.format(db_username, db_password, host_server,
                                                            db_server_port, database_name)
        print(DATABASE_URL)
        # engine = create_engine('postgresql+psycopg2://streams:REPLACE_ME@postgres:5432/amba')
        engine = create_engine(DATABASE_URL)
        Base.metadata.create_all(engine)
        # database = databases.Database(DATABASE_URL)

        Session = sessionmaker(bind=engine)
        self.session = Session()

    def save_object(self, obj):
        try:
            self.session.add(obj)
            self.session.commit()
        except IntegrityError:
            self.session.rollback()

    def get_object(self, table, key):
        result = self.session.query(table).filter_by(**key).first()
        if not result:
            return None
        return result

    def save_if_not_exist(self, obj, table, kwargs):
        if hasattr(obj, 'id') and obj.id:
            obj_db = self.get_object(table, kwargs)
            if obj_db:
                print('does exists')
                return obj_db
            else:
                print('does not exists')
                self.save_object(obj)
                self.session.refresh(obj)
                return obj

    def get_publication(self, doi):
        return self.get_object(Publication, {'doi': doi})

    def save_publication(self, publication_data):
        publication = Publication(doi=publication_data['doi'], type=publication_data['type'],
                                  pubDate=publication_data['pubDate'], year=publication_data['year'],
                                  publisher=publication_data['publisher'],
                                  citationCount=publication_data['citationCount'],
                                  title=publication_data['title'],
                                  normalizedTitle=publication_data['normalizedTitle'],
                                  abstract=publication_data['abstract'])
        publication = self.save_if_not_exist(publication, Publication, {'doi': publication.doi})

        authors = publication_data['authors']
        for author_data in authors:
            author = Author(name=author_data['name'], normalizedName=author_data['normalizedName'])

            author = self.save_if_not_exist(author, Author, {'normalizedName': author.normalizedName})
            print(author)
            if author:
                publication_authors = PublicationAuthor(**{'authorId': author.id, 'publicationDoi': publication.doi})
                self.save_object(publication_authors)

        sources = publication_data['source_id']
        for sources_data in sources:
            source = Source(title=sources_data['title'], url=sources_data['url'])
            source = self.save_if_not_exist(source, Source, {'title': source.title})
            print(source)
            if source:
                publication_sources = PublicationSource(**{'sourceId': source.id, 'publicationDoi': publication.doi})
                self.save_object(publication_sources)

        fields_of_study = publication_data['fieldOfStudy']
        for fos_data in fields_of_study:
            fos = FieldOfStudy(name=fos_data['name'], normalizedName=fos_data['normalizedName'])
            fos.level = 2
            fos = self.save_if_not_exist(fos, FieldOfStudy, {'normalizedName': fos.normalizedName})
            print(fos)
            if fos:
                publication_fos = PublicationFieldOfStudy(**{'fieldOfStudyId': fos.id, 'publicationDoi': publication.doi})
                self.save_object(publication_fos)

        return publication
        # todo
        # publicationCitations = PublicationCitations()
        # publicationReferences = PublicationReferences(**author_data)
