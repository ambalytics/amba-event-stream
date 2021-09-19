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

    publication_doi = sa.Column(sa.String(), sa.ForeignKey('publication.doi'), primary_key=True)
    citation_doi = sa.Column(sa.String(), sa.ForeignKey('publication.doi'), nullable=False)


class PublicationReference(Base):
    __tablename__ = 'publication_reference'

    publication_doi = sa.Column(sa.String(), sa.ForeignKey('publication.doi'), primary_key=True)
    reference_doi = sa.Column(sa.String(), sa.ForeignKey('publication.doi'), nullable=False)


class Source(Base):
    __tablename__ = 'source'

    id = sa.Column(sa.BigInteger(), autoincrement=True, primary_key=True)
    title = sa.Column(sa.String())
    url = sa.Column(sa.String())
    license = sa.Column(sa.String())


class PublicationSource(Base):
    __tablename__ = 'publication_source'

    publication_doi = sa.Column(sa.String(), sa.ForeignKey('publication.doi'), primary_key=True)
    source_id = sa.Column(sa.BigInteger(), sa.ForeignKey('source.id'), nullable=False)


class Author(Base):
    __tablename__ = 'author'

    id = sa.Column(sa.BigInteger(), autoincrement=True, primary_key=True)
    name = sa.Column(sa.String())
    normalized_name = sa.Column(sa.String())


class PublicationAuthor(Base):
    __tablename__ = 'publication_author'

    publication_doi = sa.Column(sa.String(), sa.ForeignKey('publication.doi'), primary_key=True)
    author_id = sa.Column(sa.BigInteger(), sa.ForeignKey('author.id'), nullable=False)


class FieldOfStudy(Base):
    __tablename__ = 'field_of_study'

    id = sa.Column(sa.BigInteger(), autoincrement=True, primary_key=True)
    name = sa.Column(sa.String())
    normalized_name = sa.Column(sa.String())
    level = sa.Column(sa.Integer())


class PublicationFieldOfStudy(Base):
    __tablename__ = 'publication_field_of_study'

    publication_doi = sa.Column(sa.String(), sa.ForeignKey('publication.doi'), primary_key=True)
    field_of_study_id = sa.Column(sa.BigInteger(), sa.ForeignKey('field_of_study.id'), nullable=False)


class FieldOfStudyChildren(Base):
    __tablename__ = 'field_of_study_children'

    field_of_study_id = sa.Column(sa.BigInteger(), sa.ForeignKey('field_of_study.id'), primary_key=True)
    child_field_of_study_id = sa.Column(sa.BigInteger(), sa.ForeignKey('field_of_study.id'), nullable=False)


class DiscussionEntity(Base):
    __tablename__ = 'discussion_entity'

    id = sa.Column(sa.BigInteger(), autoincrement=True, primary_key=True)
    entity = sa.Column(sa.String())


class DiscussionEntityData(Base):
    __tablename__ = 'discussion_entity_data'

    publication_doi = sa.Column(sa.String(), sa.ForeignKey('publication.doi'), primary_key=True)
    discussion_entity_id = sa.Column(sa.BigInteger(), sa.ForeignKey('discussion_entity.id'), nullable=False)
    count = sa.Column(sa.Integer())


class DiscussionHashtag(Base):
    __tablename__ = 'discussion_hashtag'

    id = sa.Column(sa.BigInteger(), autoincrement=True, primary_key=True)
    hashtag = sa.Column(sa.String())


class DiscussionHashtagData(Base):
    __tablename__ = 'discussion_hashtag_data'

    publication_doi = sa.Column(sa.String(), sa.ForeignKey('publication.doi'), primary_key=True)
    discussion_hashtag_id = sa.Column(sa.BigInteger(), sa.ForeignKey('discussion_hashtag.id'), nullable=False)
    count = sa.Column(sa.Integer())


class DiscussionWord(Base):
    __tablename__ = 'discussion_word'

    id = sa.Column(sa.BigInteger(), autoincrement=True, primary_key=True)
    word = sa.Column(sa.String())


class DiscussionWordData(Base):
    __tablename__ = 'discussion_word_data'

    publication_doi = sa.Column(sa.String(), sa.ForeignKey('publication.doi'), primary_key=True)
    discussion_word_id = sa.Column(sa.BigInteger(), sa.ForeignKey('discussion_word.id'), nullable=False)
    count = sa.Column(sa.Integer())


class Trending(Base):
    __tablename__ = 'trending'

    id = sa.Column(sa.BigInteger(), autoincrement=True, primary_key=True)
    publication_doi = sa.Column(sa.String(), sa.ForeignKey('publication.doi'))
    duration = sa.Column(sa.Integer())
    score = sa.Column(sa.Float())
    count = sa.Column(sa.Integer())
    median_sentiment = sa.Column(sa.Float())
    sum_follower = sa.Column(sa.Integer())
    abstract_difference = sa.Column(sa.Float())
    tweet_author_diversity = sa.Column(sa.Float())
    hashtag_diversity = sa.Column(sa.Float())
    words_diversity = sa.Column(sa.Float())
    lan_diversity = sa.Column(sa.Float())
    location_diversity = sa.Column(sa.Float())
    median_age = sa.Column(sa.Float())
    median_length = sa.Column(sa.Float())
    avg_questions = sa.Column(sa.Float())
    avg_exclamations = sa.Column(sa.Float())
    bot_percentage = sa.Column(sa.Float())
    projected_change = sa.Column(sa.Float())
    is_trending = sa.Column(sa.Boolean())

