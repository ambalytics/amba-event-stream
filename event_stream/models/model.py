import sqlalchemy as sa
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


class Publications(Base):
    __tablename__ = 'publications'

    id = sa.Column(sa.Integer(), autoincrement=True, primary_key=True)
    doi = sa.Column(sa.String(), nullable=False, unique=True)
    type = sa.Column(sa.Enum(PublicationType))
    pubDate = sa.Column(sa.String())
    year = sa.Column(sa.Integer())
    publisher = sa.Column(sa.String())
    citation_count = sa.Column(sa.Integer())
    title = sa.Column(sa.String())
    normalized_title = sa.Column(sa.String())
    abstract = sa.Column(sa.Text())

    def __repr__(self):
        return "<Publication %r>" % self.doi


class Sources(Base):
    __tablename__ = 'sources'

    id = sa.Column(sa.Integer(), autoincrement=True, primary_key=True)
    title = sa.Column(sa.String())
    url = sa.Column(sa.String())
    license = sa.Column(sa.String())


class FieldOfStudy(Base):
    __tablename__ = 'field_of_study'

    id = sa.Column(sa.Integer(), autoincrement=True, primary_key=True)
    name = sa.Column(sa.String())
    normalized_name = sa.Column(sa.String())
    level = sa.Column(sa.Integer())


class Authors(Base):
    __tablename__ = 'authors'

    id = sa.Column(sa.Integer(), autoincrement=True, primary_key=True)
    name = sa.Column(sa.String())
    normalized_name = sa.Column(sa.String())


class PublicationCitations(Base):
    __tablename__ = 'publication_citations'

    publication_doi = sa.Column(sa.Integer(), sa.ForeignKey('publications.doi'))
    citation_id = sa.Column(sa.Integer(), sa.ForeignKey('publications.doi'))


class PublicationReferences(Base):
    __tablename__ = 'publication_references'

    publication_doi = sa.Column(sa.Integer(), sa.ForeignKey('publications.doi'))
    reference_id = sa.Column(sa.Integer(), sa.ForeignKey('publications.doi'))


class PublicationFieldsOfStudy(Base):
    __tablename__ = 'publication_fields_of_study'

    publication_doi = sa.Column(sa.Integer(), sa.ForeignKey('publications.doi'))
    field_of_study_id = sa.Column(sa.Integer(), sa.ForeignKey('field_of_study.id'))


class PublicationAuthors(Base):
    __tablename__ = 'publication_authors'

    publication_doi = sa.Column(sa.Integer(), sa.ForeignKey('publications.doi'))
    author_id = sa.Column(sa.Integer(), sa.ForeignKey('authors.id'))


class PublicationSources(Base):
    __tablename__ = 'publication_sources'

    publication_doi = sa.Column(sa.Integer(), sa.ForeignKey('publications.doi'))
    source_id = sa.Column(sa.Integer(), sa.ForeignKey('sources.id'))


# --------------------------------------------------------------------------------------------------------------------

class DiscussionData(Base):
    __tablename__ = 'discussion_data'

    id = sa.Column(sa.Integer(), autoincrement=True, primary_key=True)
    publication_id = sa.Column(sa.Integer(), sa.ForeignKey('publications.id'))
    created_at = sa.Column(sa.TIMESTAMP())
    score = sa.Column(sa.Integer())
    abstractDifference = sa.Column(sa.Float())
    length = sa.Column(sa.Integer())
    questions = sa.Column(sa.Integer())
    exclamations = sa.Column(sa.Integer())
    type = sa.Column(sa.String())
    sentiment = sa.Column(sa.Float())
    subj_id = sa.Column(sa.Integer())
    followers = sa.Column(sa.Integer())
    verified = sa.Column(sa.Boolean())
    bot_score = sa.Column(sa.Float())
    author_name = sa.Column(sa.String())
    author_location = sa.Column(sa.String())
    source_id = sa.Column(sa.String())


class DiscussionEntities(Base):
    __tablename__ = 'discussion_entities'

    id = sa.Column(sa.Integer(), autoincrement=True, primary_key=True)
    entity = sa.Column(sa.String())


class DiscussionHashtags(Base):
    __tablename__ = 'discussion_hashtags'

    id = sa.Column(sa.Integer(), autoincrement=True, primary_key=True)
    hashtag = sa.Column(sa.String())


class DiscussionWords(Base):
    __tablename__ = 'discussion_words'

    id = sa.Column(sa.Integer(), autoincrement=True, primary_key=True)
    word = sa.Column(sa.String())


class DiscussionAuthors(Base):
    __tablename__ = 'discussion_authors'

    id = sa.Column(sa.Integer(), autoincrement=True, primary_key=True)
    name = sa.Column(sa.String())


class DiscussionAuthorsData(Base):
    __tablename__ = 'discussion_authors_data'

    discussion_data_id = sa.Column(sa.Integer(), sa.ForeignKey('discussion_data.id'))
    discussion_author_id = sa.Column(sa.Integer(), sa.ForeignKey('discussion_authors.id'))


class DiscussionWordsData(Base):
    __tablename__ = 'discussion_words_data'

    discussion_data_id = sa.Column(sa.Integer(), sa.ForeignKey('discussion_data.id'))
    discussion_word_id = sa.Column(sa.Integer(), sa.ForeignKey('discussion_words.id'))


class DiscussionHashtagsData(Base):
    __tablename__ = 'discussion_hashtags_data'

    discussion_data_id = sa.Column(sa.Integer(), sa.ForeignKey('discussion_data.id'))
    discussion_hashtag_id = sa.Column(sa.Integer(), sa.ForeignKey('discussion_hashtags.id'))


class DiscussionEntitiesData(Base):
    __tablename__ = 'discussion_entities_data'

    discussion_data_id = sa.Column(sa.Integer(), sa.ForeignKey('discussion_data.id'))
    discussion_entities_id = sa.Column(sa.Integer(), sa.ForeignKey('discussion_entities.id'))
