import logging

from event_stream.models.model import *
from sqlalchemy import Table, Column, MetaData, create_engine
import os
import urllib
import psycopg2
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker, scoped_session


class DAO(object):
    # session = None

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
        self.engine = create_engine(DATABASE_URL, pool_size=20, max_overflow=0)
        Base.metadata.create_all(self.engine)
        # database = databases.Database(DATABASE_URL)

        # Session = sessionmaker(bind=engine)
        # session_factory = sessionmaker(bind=self.engine)
        # Session = scoped_session(session_factory)
        # self.session = Session()

    @staticmethod
    def save_object(session, obj):
        try:
            session.add(obj)
            session.commit()
        except IntegrityError:
            print('IntegrityError')
            session.rollback()

    @staticmethod
    def get_object(session, table, key):
        result = session.query(table).filter_by(**key).first()
        if not result:
            return None
        return result

    @staticmethod
    def save_if_not_exist(session, obj, table, kwargs):
        obj_db = DAO.get_object(session, table, kwargs)
        if obj_db:
            return obj_db

        DAO.save_object(session, obj)
        return obj

    def get_publication(self, doi):
        session_factory = sessionmaker(bind=self.engine)
        Session = scoped_session(session_factory)
        session = Session()
        result = self.get_object(session, Publication, {'doi': doi})
        session.close()
        return result

    def save_publication(self, publication_data):
        session_factory = sessionmaker(bind=self.engine)
        Session = scoped_session(session_factory)
        session = Session()

        publication = Publication(doi=publication_data['doi'], type=publication_data['type'],
                                  pubDate=publication_data['pubDate'], year=publication_data['year'],
                                  publisher=publication_data['publisher'],
                                  citationCount=publication_data['citationCount'],
                                  title=publication_data['title'],
                                  normalizedTitle=publication_data['normalizedTitle'],
                                  abstract=publication_data['abstract'])
        publication = self.save_if_not_exist(session, publication, Publication, {'doi': publication.doi})

        logging.warning('publication.doi')
        logging.warning(publication.doi)
        logging.warning(publication.id)

        authors = publication_data['authors']
        for author_data in authors:
            author = Author(name=author_data['name'], normalizedName=author_data['normalizedName'])

            author = self.save_if_not_exist(session, author, Author, {'normalizedName': author.normalizedName})
            logging.warning('author.id')
            logging.warning(author.id)
            if author.id:
                publication_authors = PublicationAuthor(**{'authorId': author.id, 'publicationDoi': publication.doi})
                self.save_if_not_exist(session, publication_authors, PublicationAuthor, {'authorId': author.id, 'publicationDoi': publication.doi})

        sources = publication_data['source_id']
        for sources_data in sources:
            source = Source(title=sources_data['title'], url=sources_data['url']) # todo no doi url ?
            source = self.save_if_not_exist(session, source, Source, {'title': source.title})
            logging.warning('source.id')
            logging.warning(source.id)
            if source.id:
                publication_sources = PublicationSource(**{'sourceId': source.id, 'publicationDoi': publication.doi})
                self.save_if_not_exist(session, publication_sources, PublicationSource, {'sourceId': source.id, 'publicationDoi': publication.doi})

        if 'fieldsOfStudy' in publication_data:
            fields_of_study = publication_data['fieldsOfStudy']
            for fos_data in fields_of_study:
                fos = FieldOfStudy(name=fos_data['name'], normalizedName=fos_data['normalizedName'])
                fos.level = 2
                fos = self.save_if_not_exist(session, fos, FieldOfStudy, {'normalizedName': fos.normalizedName})
                logging.warning('fos.id')
                logging.warning(fos.id)
                if fos.id:
                    publication_fos = PublicationFieldOfStudy(**{'fieldOfStudyId': fos.id, 'publicationDoi': publication.doi})
                    self.save_if_not_exist(session, publication_fos, PublicationFieldOfStudy, {'fieldOfStudyId': fos.id, 'publicationDoi': publication.doi})

        session.close()
        return publication
        # todo add perculator!!!!!!
        # use different names for config until we remove gql?
        # publicationCitations = PublicationCitations()
        # publicationReferences = PublicationReferences(**author_data)
