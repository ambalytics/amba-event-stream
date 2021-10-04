import datetime
import json
import logging

from event_stream.models.model import *
from sqlalchemy import Table, Column, MetaData, create_engine, inspect, text, bindparam, desc
import os
import urllib
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker, scoped_session


def save_newest_discussion_subj(session, e):
    max_count = 10

    entities = []
    if 'context_annotations' in e['subj']['data']:
        context_entity = e['subj']['data']['context_annotations']
        for entity_data in context_entity:
            entities.append(entity_data['entity']['name'])

    obj = DiscussionNewestSubj(
        type='twitter',
        publication_doi=e['obj']['data']['doi'],
        sub_id=e['subj_id'],
        created_at=datetime.datetime.now(),
        score=e['subj']['processed']['score'],
        bot_rating=e['subj']['processed']['bot_rating'],
        followers=e['subj']['processed']['followers'],
        sentiment_raw=e['subj']['processed']['sentiment_raw'],
        contains_abstract_raw=e['subj']['processed']['contains_abstract_raw'],
        lang=e['subj']['data']['lang'],
        location=e['subj']['processed']['location'],
        source=e['subj']['data']['source'],
        subj_type=e['subj']['processed']['tweet_type'],
        question_mark_count=e['subj']['processed']['question_mark_count'],
        exclamation_mark_count=e['subj']['processed']['exclamation_mark_count'],
        length=e['subj']['processed']['length'],
        entities=json.dumps(entities)
    )

    table = DiscussionNewestSubj
    key = {'publication_doi': e['obj']['data']['doi'], 'type': 'twitter'}
    count = session.query(table).filter_by(**key).count()

    if count >= max_count:
        # update oldest
        oldest = session.query(table).filter_by(**key).order_by(DiscussionNewestSubj.created_at).first()
        print(oldest.created_at)

        oldest.sub_id = obj.sub_id
        oldest.created_at = obj.created_at
        oldest.score = obj.score
        oldest.bot_rating = obj.bot_rating
        oldest.followers = obj.followers
        oldest.sentiment_raw = obj.sentiment_raw
        oldest.contains_abstract_raw = obj.contains_abstract_raw
        oldest.lang = obj.lang
        oldest.location = obj.location
        oldest.source = obj.source
        oldest.subj_type = obj.subj_type
        oldest.question_mark_count = obj.question_mark_count
        oldest.exclamation_mark_count = obj.exclamation_mark_count
        oldest.length = obj.length
        oldest.entities = obj.entities

        session.commit()
        return True

    else:
        DAO.save_object(session, obj)
        return True


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
            logging.exception('save object')
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
    def save_or_update_count(session, obj, table, kwargs):
        obj_db = DAO.get_object(session, table, kwargs)
        if obj_db:
            # add count to existing object
            obj_db.count += obj.count
            session.commit()
            return obj_db

        DAO.save_object(session, obj)
        return obj

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
        params = {'doi': doi, }

        session = Session()
        # pub = session.query(Publication).filter_by(doi=doi).all()
        p = text("""SELECT * FROM publication WHERE doi=:doi""")
        p = p.bindparams(bindparam('doi'))
        resultproxy = session.execute(p, params)
        pub = [dict(row) for row in resultproxy]
        result = None

        if pub:
            a = text("""SELECT name FROM publication_author as p
                        JOIN author as a on (a.id = p.author_id)
                        WHERE p.publication_doi=:doi""")
            a = a.bindparams(bindparam('doi'))
            resultproxy = session.execute(a, params)
            authors = [dict(row) for row in resultproxy]

            f = text("""SELECT name FROM publication_field_of_study as p
                        JOIN field_of_study as a on (a.id = p.field_of_study_id)
                        WHERE p.publication_doi=:doi""")
            f = f.bindparams(bindparam('doi'))
            resultproxy = session.execute(f, params)
            fos = [dict(row) for row in resultproxy]

            s = text("""SELECT title, url FROM publication_source as p
                        JOIN source as a on (a.id = p.source_id)
                        WHERE p.publication_doi=:doi""")
            s = s.bindparams(bindparam('doi'))
            resultproxy = session.execute(s, params)
            sources = [dict(row) for row in resultproxy]

            result = pub[0]
            result['authors']: authors
            result['fields_of_study']: fos
            result['source_id']: sources

        session.close()
        return result

    def save_publication(self, publication_data):
        session_factory = sessionmaker(bind=self.engine)
        Session = scoped_session(session_factory)
        session = Session()

        publication = Publication(doi=publication_data['doi'], type=publication_data['type'],
                                  pub_date=publication_data['pub_date'], year=publication_data['year'],
                                  publisher=publication_data['publisher'],
                                  citation_count=publication_data['citation_count'],
                                  title=publication_data['title'],
                                  normalized_title=publication_data['normalized_title'],
                                  abstract=publication_data['abstract'])
        publication = self.save_if_not_exist(session, publication, Publication, {'doi': publication.doi})

        logging.debug('publication.doi')
        logging.debug(publication.doi)
        # logging.warning(publication.id)

        authors = publication_data['authors']
        for author_data in authors:
            author = Author(name=author_data['name'], normalized_name=author_data['normalized_name'])
            author = self.save_if_not_exist(session, author, Author, {'normalized_name': author.normalized_name})

            if author.id:
                publication_authors = PublicationAuthor(**{'author_id': author.id, 'publication_doi': publication.doi})
                self.save_if_not_exist(session, publication_authors, PublicationAuthor,
                                       {'author_id': author.id, 'publication_doi': publication.doi})

        if 'source_id' in publication_data:
            sources = publication_data['source_id']
            for sources_data in sources:
                source = Source(title=sources_data['title'], url=sources_data['url'])  # todo no doi url ?
                source = self.save_if_not_exist(session, source, Source, {'title': source.title})

                if source.id:
                    publication_sources = PublicationSource(
                        **{'source_id': source.id, 'publication_doi': publication.doi})
                    self.save_if_not_exist(session, publication_sources, PublicationSource,
                                           {'source_id': source.id, 'publication_doi': publication.doi})

        if 'fields_of_study' in publication_data:
            fields_of_study = publication_data['fields_of_study']
            for fos_data in fields_of_study:
                fos = FieldOfStudy(name=fos_data['name'], normalized_name=fos_data['normalized_name'])
                fos = self.save_if_not_exist(session, fos, FieldOfStudy, {'normalized_name': fos.normalized_name})

                if fos.id:
                    publication_fos = PublicationFieldOfStudy(
                        **{'field_of_study_id': fos.id, 'publication_doi': publication.doi})
                    self.save_if_not_exist(session, publication_fos, PublicationFieldOfStudy,
                                           {'field_of_study_id': fos.id, 'publication_doi': publication.doi})

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
        publication_doi = event_data['obj']['data']['doi']

        if 'context_annotations' in event_data['subj']['data']:
            context_entity = event_data['subj']['data']['context_annotations']
            for entity_data in context_entity:
                entity = DiscussionData(value=entity_data['entity']['name'], type='entity')
                entity = self.save_if_not_exist(session, entity, DiscussionData,
                                                {'value': entity.value, 'type': 'entity'})

                if entity.id:
                    publication_entity = DiscussionDataPoint(
                        **{'publication_doi': publication_doi, 'discussion_data_point_id': entity.id, 'count': 1})
                    self.save_or_update_count(session, publication_entity, DiscussionDataPoint,
                                              {'publication_doi': publication_doi, 'discussion_data_point_id': entity.id})

        if 'words' in event_data['subj']['processed']:
            words = event_data['subj']['processed']['words']
            for words_data in words:
                word = DiscussionData(value=words_data[0], type='word')
                word = self.save_if_not_exist(session, word, DiscussionData, {'value': word.value, 'type': 'word'})

                if word.id:
                    publication_words = DiscussionDataPoint(
                        **{'publication_doi': publication_doi, 'discussion_data_point_id': word.id, 'count': words_data[1]})
                    self.save_or_update_count(session, publication_words, DiscussionDataPoint,
                                              {'publication_doi': publication_doi, 'discussion_data_point_id': word.id})

        if 'entities' in event_data['subj']['data'] and 'hashtags' in event_data['subj']['data']['entities']:
            hashtags = event_data['subj']['data']['entities']['hashtags']
            for h_data in hashtags:
                hashtag = DiscussionData(value=h_data['tag'], type='hashtag')
                hashtag = self.save_if_not_exist(session, hashtag, DiscussionData,
                                                 {'value': hashtag.value, 'type': 'hashtag'})

                if hashtag.id:
                    publication_h = DiscussionDataPoint(
                        **{'publication_doi': publication_doi, 'discussion_data_point_id': hashtag.id, 'count': 1})
                    self.save_or_update_count(session, publication_h, DiscussionDataPoint,
                                              {'publication_doi': publication_doi, 'discussion_data_point_id': hashtag.id})

        if 'name' in event_data['subj']['processed']:
            author = DiscussionData(value=event_data['subj']['processed']['name'], type='name')
            author = self.save_if_not_exist(session, author, DiscussionData,
                                            {'value': author.value, 'type': 'author'})

            if author.id:
                publication_author = DiscussionDataPoint(**{'discussion_data_point_id': author.id, 'count': 1,
                                                            'publication_doi': publication_doi})
                self.save_or_update_count(session, publication_author, DiscussionDataPoint,
                                          {'publication_doi': publication_doi, 'discussion_data_point_id': author.id})

        if 'location' in event_data['subj']['processed']:
            location = DiscussionData(value=event_data['subj']['processed']['location'], type='location')
            location = self.save_if_not_exist(session, location, DiscussionData,
                                              {'value': location.value, 'type': 'location'})

            if location.id:
                publication_location = DiscussionDataPoint(**{'discussion_data_point_id': location.id, 'count': 1,
                                                              'publication_doi': publication_doi})
                self.save_or_update_count(session, publication_location, DiscussionDataPoint,
                                          {'publication_doi': publication_doi, 'discussion_data_point_id': location.id})

        if 'tweet_type' in event_data['subj']['processed']:
            dd_type = DiscussionData(value=event_data['subj']['processed']['tweet_type'], type='tweet_type')
            dd_type = self.save_if_not_exist(session, dd_type, DiscussionData, {'value': dd_type.value, 'type': 'tweet_type'})

            if dd_type.id:
                publication_type = DiscussionDataPoint(**{'discussion_data_point_id': dd_type.id, 'count': 1,
                                                          'publication_doi': publication_doi})
                self.save_or_update_count(session, publication_type, DiscussionDataPoint,
                                          {'publication_doi': publication_doi, 'discussion_data_point_id': dd_type.id})

        if 'lang' in event_data['subj']['data']:
            lang = DiscussionData(value=event_data['subj']['data']['lang'], type='lang')
            lang = self.save_if_not_exist(session, lang, DiscussionData, {'value': lang.value, 'type': 'lang'})

            if lang.id:
                publication_lang = DiscussionDataPoint(**{'discussion_data_point_id': lang.id, 'count': 1,
                                                          'publication_doi': publication_doi})
                self.save_or_update_count(session, publication_lang, DiscussionDataPoint,
                                          {'publication_doi': publication_doi, 'discussion_data_point_id': lang.id})

        if 'source' in event_data['subj']['data']:
            source = DiscussionData(value=event_data['subj']['data']['source'], type='source')
            source = self.save_if_not_exist(session, source, DiscussionData, {'value': source.value, 'type': 'source'})

            if source.id:
                publication_source = DiscussionDataPoint(**{'discussion_data_point_id': source.id, 'count': 1,
                                                            'publication_doi': publication_doi})
                self.save_or_update_count(session, publication_source, DiscussionDataPoint,
                                          {'publication_doi': publication_doi, 'discussion_data_point_id': source.id})
        save_newest_discussion_subj(session, event_data)

        session.close()
        return True

    def save_publication_not_found(self, doi, pub_is_done):
        session_factory = sessionmaker(bind=self.engine)
        Session = scoped_session(session_factory)
        session = Session()

        obj = PublicationNotFound(
            publication_doi=doi,
            last_try=datetime.datetime.now(),
            pub_missing=pub_is_done,
        )

        table = PublicationNotFound
        kwargs = {'publication_doi': doi}
        obj_db = DAO.get_object(session, table, kwargs)
        if obj_db:
            # add count to existing object
            obj_db.last_try = datetime.datetime.now()
            session.commit()
            session.close()
            return obj_db

        DAO.save_object(session, obj)
        session.close()
        return obj