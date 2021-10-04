import sqlalchemy as sa
from sqlalchemy import JSON
from sqlalchemy.ext.declarative import declarative_base
from enum import Enum

Base = declarative_base()


class PublicationType(str, Enum):
    BOOK = 'BOOK'
    BOOK_CHAPTER = 'BOOK_CHAPTER'
    BOOK_REFERENCE_ENTRY = 'BOOK_REFERENCE_ENTRY'
    CONFERENCE_PAPER = 'CONFERENCE_PAPER'
    DATASET = 'DATASET'
    JOURNAL_ARTICLE = 'JOURNAL_ARTICLE'
    PATENT = 'PATENT'
    REPOSITORY = 'REPOSITORY'
    THESIS = 'THESIS'
    UNKNOWN = 'UNKNOWN'


class Publication(Base):
    __tablename__ = 'publication'

    id = sa.Column(sa.BigInteger(), autoincrement=True, primary_key=True)
    doi = sa.Column(sa.String(), nullable=False, unique=True)
    type = sa.Column(sa.Enum(PublicationType))
    pub_date = sa.Column(sa.String())
    year = sa.Column(sa.Integer())
    publisher = sa.Column(sa.String())
    citation_count = sa.Column(sa.Integer())
    title = sa.Column(sa.String())
    normalized_title = sa.Column(sa.String())
    abstract = sa.Column(sa.Text())


class PublicationCitation(Base):
    __tablename__ = 'publication_citation'

    publication_doi = sa.Column(sa.String(), sa.ForeignKey('publication.doi'), nullable=False, primary_key=True)
    citation_doi = sa.Column(sa.String(), sa.ForeignKey('publication.doi'), nullable=False, primary_key=True)


class PublicationReference(Base):
    __tablename__ = 'publication_reference'

    publication_doi = sa.Column(sa.String(), sa.ForeignKey('publication.doi'), nullable=False, primary_key=True)
    reference_doi = sa.Column(sa.String(), sa.ForeignKey('publication.doi'), nullable=False, primary_key=True)


class Source(Base):
    __tablename__ = 'source'

    id = sa.Column(sa.BigInteger(), autoincrement=True, primary_key=True)
    title = sa.Column(sa.String())
    url = sa.Column(sa.String())
    license = sa.Column(sa.String())


class PublicationSource(Base):
    __tablename__ = 'publication_source'

    publication_doi = sa.Column(sa.String(), sa.ForeignKey('publication.doi'), nullable=False, primary_key=True)
    source_id = sa.Column(sa.BigInteger(), sa.ForeignKey('source.id'), nullable=False, primary_key=True)


class Author(Base):
    __tablename__ = 'author'

    id = sa.Column(sa.BigInteger(), autoincrement=True, primary_key=True)
    name = sa.Column(sa.String())
    normalized_name = sa.Column(sa.String())


class PublicationAuthor(Base):
    __tablename__ = 'publication_author'

    publication_doi = sa.Column(sa.String(), sa.ForeignKey('publication.doi'), nullable=False, primary_key=True)
    author_id = sa.Column(sa.BigInteger(), sa.ForeignKey('author.id'), nullable=False, primary_key=True)


class FieldOfStudy(Base):
    __tablename__ = 'field_of_study'

    id = sa.Column(sa.BigInteger(), autoincrement=True, primary_key=True)
    name = sa.Column(sa.String())
    normalized_name = sa.Column(sa.String())


class PublicationFieldOfStudy(Base):
    __tablename__ = 'publication_field_of_study'

    publication_doi = sa.Column(sa.String(), sa.ForeignKey('publication.doi'), nullable=False, primary_key=True)
    field_of_study_id = sa.Column(sa.BigInteger(), sa.ForeignKey('field_of_study.id'), nullable=False, primary_key=True)


class PublicationNotFound(Base):

    __tablename__ = 'publication_not_found'

    publication_doi = sa.Column(sa.String(), primary_key=True)
    last_try = sa.Column(sa.DateTime())
    pub_missing = sa.Column(sa.String())


class DiscussionData(Base):

    __tablename__ = 'discussion_data'

    id = sa.Column(sa.BigInteger(), autoincrement=True, primary_key=True)
    value = sa.Column(sa.String())
    type = sa.Column(sa.String())


class DiscussionDataPoint(Base):

    __tablename__ = 'discussion_data_point'

    publication_doi = sa.Column(sa.String(), sa.ForeignKey('publication.doi'), nullable=False, primary_key=True)
    discussion_data_point_id = sa.Column(sa.BigInteger(), sa.ForeignKey('discussion_data.id'), nullable=False, primary_key=True)
    count = sa.Column(sa.Integer())


class DiscussionNewestSubj(Base):
    __tablename__ = 'discussion_newest_subj'

    id = sa.Column(sa.BigInteger(), autoincrement=True, primary_key=True)
    type = sa.Column(sa.String())
    publication_doi = sa.Column(sa.String(), sa.ForeignKey('publication.doi'))
    sub_id = sa.Column(sa.String())
    created_at = sa.Column(sa.DateTime())
    score = sa.Column(sa.Float())
    bot_rating = sa.Column(sa.Float())
    followers = sa.Column(sa.Integer())
    sentiment_raw = sa.Column(sa.Float())
    contains_abstract_raw = sa.Column(sa.Float())
    lang = sa.Column(sa.String())
    location = sa.Column(sa.String())
    source = sa.Column(sa.String())
    subj_type = sa.Column(sa.String())
    question_mark_count = sa.Column(sa.Integer())
    exclamation_mark_count = sa.Column(sa.Integer())
    length = sa.Column(sa.Integer())
    entities = sa.Column(JSON())


class Trending(Base):
    __tablename__ = 'trending'

    id = sa.Column(sa.BigInteger(), autoincrement=True, primary_key=True)
    publication_doi = sa.Column(sa.String(), sa.ForeignKey('publication.doi'))
    duration = sa.Column(sa.String())
    score = sa.Column(sa.Float())
    count = sa.Column(sa.Integer())
    median_sentiment = sa.Column(sa.Float())
    sum_followers = sa.Column(sa.Integer())
    abstract_difference = sa.Column(sa.Float())
    median_age = sa.Column(sa.Float())
    median_length = sa.Column(sa.Float())
    mean_questions = sa.Column(sa.Float())
    mean_exclamations = sa.Column(sa.Float())
    mean_bot_rating = sa.Column(sa.Float())
    projected_change = sa.Column(sa.Float())
    trending = sa.Column(sa.Float())
    ema = sa.Column(sa.Float())
    kama = sa.Column(sa.Float())
    ker = sa.Column(sa.Float())
    mean_score = sa.Column(sa.Float())
    stddev = sa.Column(sa.Float())



