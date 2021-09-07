import logging

from event_stream.models.model import *
from sqlalchemy import Table, Column, MetaData, create_engine, inspect, text, bindparam
import os
import urllib
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
    def object_as_dict(obj):
        return {c.key: getattr(obj, c.key)
                for c in inspect(obj).mapper.column_attrs}

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

        # todo add sources

        session = Session()
        pub = session.query(Publication).filter_by(doi=doi).all()

        result = None
        if pub:
            params = {'doi': doi, }

            a = text("""SELECT name FROM "PublicationAuthor" as p
                        JOIN "Author" as a on (a.id = p."authorId")
                        WHERE p."publicationDoi"=:doi""")
            a = a.bindparams(bindparam('doi'))
            authors = session.execute(a, params).fetchall()

            f = text("""SELECT name FROM "PublicationFieldOfStudy" as p
                        JOIN "FieldOfStudy" as a on (a.id = p."fieldOfStudyId")
                        WHERE p."publicationDoi"=:doi""")
            f = f.bindparams(bindparam('doi'))
            fos = session.execute(f, params).fetchall()

            s = text("""SELECT name FROM "PublicationSource" as p
                        JOIN "Source" as a on (a.id = p."fieldOfStudyId")
                        WHERE p."publicationDoi"=:doi""")
            s = s.bindparams(bindparam('doi'))
            sources = session.execute(s, params).fetchall()

            result = pub
            result['authors']: authors
            result['fieldsOfStudy']: fos
            result['source_id']: sources

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

        logging.debug('publication.doi')
        logging.debug(publication.doi)
        # logging.warning(publication.id)

        authors = publication_data['authors']
        for author_data in authors:
            author = Author(name=author_data['name'], normalizedName=author_data['normalizedName'])

            author = self.save_if_not_exist(session, author, Author, {'normalizedName': author.normalizedName})
            if author.id:
                publication_authors = PublicationAuthor(**{'authorId': author.id, 'publicationDoi': publication.doi})
                self.save_if_not_exist(session, publication_authors, PublicationAuthor, {'authorId': author.id, 'publicationDoi': publication.doi})

        if 'source_id' in publication_data:
            sources = publication_data['source_id']
            for sources_data in sources:
                source = Source(title=sources_data['title'], url=sources_data['url']) # todo no doi url ?
                source = self.save_if_not_exist(session, source, Source, {'title': source.title})
                if source.id:
                    publication_sources = PublicationSource(**{'sourceId': source.id, 'publicationDoi': publication.doi})
                    self.save_if_not_exist(session, publication_sources, PublicationSource, {'sourceId': source.id, 'publicationDoi': publication.doi})

        if 'fieldsOfStudy' in publication_data:
            fields_of_study = publication_data['fieldsOfStudy']
            for fos_data in fields_of_study:
                fos = FieldOfStudy(name=fos_data['name'], normalizedName=fos_data['normalizedName'])
                fos.level = 2
                fos = self.save_if_not_exist(session, fos, FieldOfStudy, {'normalizedName': fos.normalizedName})
                if fos.id:
                    publication_fos = PublicationFieldOfStudy(**{'fieldOfStudyId': fos.id, 'publicationDoi': publication.doi})
                    self.save_if_not_exist(session, publication_fos, PublicationFieldOfStudy, {'fieldOfStudyId': fos.id, 'publicationDoi': publication.doi})

        session.close()
        return publication
        # todo add perculator!!!!!!
        # use different names for config until we remove gql?
        # publicationCitations = PublicationCitations()
        # publicationReferences = PublicationReferences(**author_data)

    def save_discussion_data(self, event_data):
        """save a discussion data row from event data

        Argumetns:
            event_data: to be saved
        """
        session_factory = sessionmaker(bind=self.engine)
        Session = scoped_session(session_factory)
        session = Session()
        event_data['sourceId'] = 'twitter'  # todo
        if 'location' not in event_data['subj']['processed']:
            event_data['subj']['processed']['location'] = 'unknown'
        if 'contains_abstract' not in event_data['subj']['processed']:
            event_data['subj']['processed']['contains_abstract'] = 0
        if 'sentiment' not in event_data['subj']['processed']:
            event_data['subj']['processed']['sentiment'] = 0
        if 'name' not in event_data['subj']['processed']:
            event_data['subj']['processed']['name'] = 'unknown'

        discussion_data = DiscussionData(
            publicationDoi=event_data['obj']['data']['doi'],
            createdAt=event_data['timestamp'],
            score=event_data['subj']['processed']['score'],
            timeScore=event_data['subj']['processed']['time_score'],
            typeScore=event_data['subj']['processed']['type_score'],
            userScore=event_data['subj']['processed']['user_score'],
            language=event_data['subj']['data']['lang'],
            source=event_data['subj']['data']['source'],
            abstractDifference=event_data['subj']['processed']['contains_abstract'],
            length=event_data['subj']['processed']['length'],
            questions=event_data['subj']['processed']['question_mark_count'],
            exclamations=event_data['subj']['processed']['exclamation_mark_count'],
            type=event_data['subj']['processed']['tweet_type'],
            sentiment=event_data['subj']['processed']['sentiment'],
            subjId=event_data['subj']['alternative-id'],
            followers=event_data['subj']['processed']['followers'],
            botScore=event_data['subj']['processed']['bot_rating'],
            authorName=event_data['subj']['processed']['name'],  # make this a table?
            authorLocation=event_data['subj']['processed']['location'],
            sourceId=event_data['sourceId'])
        self.save_object(session, discussion_data)

        if 'context_annotations' in event_data['subj']['data']:
            context_entity = event_data['subj']['data']['context_annotations']
            for entity_data in context_entity:
                entity = DiscussionEntity(entity=entity_data['entity']['name'])
                entity = self.save_if_not_exist(session, entity, DiscussionEntity, {'entity': entity.entity})

                publication_entity = DiscussionEntityData(
                    **{'discussionDataId': discussion_data.id, 'discussionEntityId': entity.id})
                self.save_if_not_exist(session, publication_entity, DiscussionEntityData,
                                       {'discussionDataId': discussion_data.id, 'discussionEntityId': entity.id})

        if 'words' in event_data['subj']['processed']:
            words = event_data['subj']['processed']['words']
            for words_data in words:
                word = DiscussionWord(word=words_data[0])
                word = self.save_if_not_exist(session, word, DiscussionWord, {'word': word.word})

                publication_words = DiscussionWordData(
                    **{'discussionDataId': discussion_data.id, 'discussionWordId': word.id, 'count': words_data[1]})
                self.save_object(session, publication_words)
                self.save_if_not_exist(session, publication_words, DiscussionWordData,
                                       {'discussionDataId': discussion_data.id, 'discussionWordId': word.id})

        if 'entities' in event_data['subj']['data'] and 'hashtags' in event_data['subj']['data']['entities']:
            hashtags = event_data['subj']['data']['entities']['hashtags']
            for h_data in hashtags:
                hashtag = DiscussionHashtag(hashtag=h_data['tag'])
                hashtag = self.save_if_not_exist(session, hashtag, DiscussionHashtag, {'hashtag': hashtag.hashtag})

                publication_h = DiscussionHashtagData(
                    **{'discussionDataId': discussion_data.id, 'discussionHashtagId': hashtag.id})
                self.save_object(session, publication_h)
                self.save_if_not_exist(session, publication_h, DiscussionHashtagData,
                                       {'discussionDataId': discussion_data.id, 'discussionHashtagId': hashtag.id})

        session.close()
        return discussion_data
