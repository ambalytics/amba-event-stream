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
    __tablename__ = 'Publication'

    id = sa.Column(sa.BigInteger(), autoincrement=True, primary_key=True)
    doi = sa.Column(sa.String(), nullable=False, unique=True)
    type = sa.Column(sa.Enum(PublicationType))
    pubDate = sa.Column(sa.String())
    year = sa.Column(sa.Integer())
    publisher = sa.Column(sa.String())
    citationCount = sa.Column(sa.Integer())
    title = sa.Column(sa.String())
    normalizedTitle = sa.Column(sa.String())
    abstract = sa.Column(sa.Text())


class Source(Base):
    __tablename__ = 'Source'

    id = sa.Column(sa.BigInteger(), autoincrement=True, primary_key=True)
    title = sa.Column(sa.String())
    url = sa.Column(sa.String())
    license = sa.Column(sa.String())


class FieldOfStudy(Base):
    __tablename__ = 'FieldOfStudy'

    id = sa.Column(sa.BigInteger(), autoincrement=True, primary_key=True)
    name = sa.Column(sa.String())
    normalizedName = sa.Column(sa.String())
    level = sa.Column(sa.Integer())


class Author(Base):
    __tablename__ = 'Author'

    id = sa.Column(sa.BigInteger(), autoincrement=True, primary_key=True)
    name = sa.Column(sa.String())
    normalizedName = sa.Column(sa.String())


class PublicationCitation(Base):
    __tablename__ = 'PublicationCitation'

    publicationDoi = sa.Column(sa.String(), sa.ForeignKey('Publication.doi'), nullable=False, primary_key=True)
    citationId = sa.Column(sa.String(), sa.ForeignKey('Publication.doi'), nullable=False, primary_key=True)


class PublicationReference(Base):
    __tablename__ = 'PublicationReference'

    publicationDoi = sa.Column(sa.String(), sa.ForeignKey('Publication.doi'), nullable=False, primary_key=True)
    referenceId = sa.Column(sa.String(), sa.ForeignKey('Publication.doi'), nullable=False, primary_key=True)


class PublicationFieldOfStudy(Base):
    __tablename__ = 'PublicationFieldOfStudy'

    publicationDoi = sa.Column(sa.String(), sa.ForeignKey('Publication.doi'), nullable=False, primary_key=True)
    fieldOfStudyId = sa.Column(sa.BigInteger(), sa.ForeignKey('FieldOfStudy.id'), nullable=False, primary_key=True)


class PublicationAuthor(Base):
    __tablename__ = 'PublicationAuthor'

    publicationDoi = sa.Column(sa.String(), sa.ForeignKey('Publication.doi'), nullable=False, primary_key=True)
    authorId = sa.Column(sa.BigInteger(), sa.ForeignKey('Author.id'), nullable=False, primary_key=True)


class PublicationSource(Base):
    __tablename__ = 'PublicationSource'

    publicationDoi = sa.Column(sa.String(), sa.ForeignKey('Publication.doi'), nullable=False, primary_key=True)
    sourceId = sa.Column(sa.BigInteger(), sa.ForeignKey('Source.id'), nullable=False, primary_key=True)


class DiscussionData(Base):
    __tablename__ = 'DiscussionData'

    id = sa.Column(sa.BigInteger(), autoincrement=True, primary_key=True)
    publicationDoi = sa.Column(sa.String(), sa.ForeignKey('Publication.doi'))
    createdAt = sa.Column(sa.TIMESTAMP())
    score = sa.Column(sa.Float())
    timeScore = sa.Column(sa.Float())
    typeScore = sa.Column(sa.Float())
    userScore = sa.Column(sa.Float())
    language = sa.Column(sa.String())
    source = sa.Column(sa.String())
    abstractDifference = sa.Column(sa.Float())
    length = sa.Column(sa.Integer())
    questions = sa.Column(sa.Integer())
    exclamations = sa.Column(sa.Integer())
    type = sa.Column(sa.String())
    sentiment = sa.Column(sa.Float())
    subjId = sa.Column(sa.BigInteger())
    followers = sa.Column(sa.Integer())
    botScore = sa.Column(sa.Float())
    authorName = sa.Column(sa.String())
    authorLocation = sa.Column(sa.String())
    sourceId = sa.Column(sa.String())


class DiscussionEntity(Base):
    __tablename__ = 'DiscussionEntity'

    id = sa.Column(sa.BigInteger(), autoincrement=True, primary_key=True)
    entity = sa.Column(sa.String())


class DiscussionHashtag(Base):
    __tablename__ = 'DiscussionHashtag'

    id = sa.Column(sa.BigInteger(), autoincrement=True, primary_key=True)
    hashtag = sa.Column(sa.String())


class DiscussionWord(Base):
    __tablename__ = 'DiscussionWord'

    id = sa.Column(sa.BigInteger(), autoincrement=True, primary_key=True)
    word = sa.Column(sa.String())


class DiscussionAuthor(Base):
    __tablename__ = 'DiscussionAuthor'

    id = sa.Column(sa.BigInteger(), autoincrement=True, primary_key=True)
    name = sa.Column(sa.String())


class DiscussionEntityData(Base):
    __tablename__ = 'DiscussionEntityData'

    discussionDataId = sa.Column(sa.BigInteger(), sa.ForeignKey('DiscussionData.id'), nullable=False, primary_key=True)
    discussionEntityId = sa.Column(sa.BigInteger(), sa.ForeignKey('DiscussionEntity.id'), nullable=False,
                                   primary_key=True)


class DiscussionAuthorData(Base):
    __tablename__ = 'DiscussionAuthorData'

    discussionDataId = sa.Column(sa.BigInteger(), sa.ForeignKey('DiscussionData.id'), nullable=False, primary_key=True)
    discussionAuthorId = sa.Column(sa.BigInteger(), sa.ForeignKey('DiscussionAuthor.id'), nullable=False,
                                   primary_key=True)


class DiscussionWordData(Base):
    __tablename__ = 'DiscussionWordData'

    discussionDataId = sa.Column(sa.BigInteger(), sa.ForeignKey('DiscussionData.id'), nullable=False, primary_key=True)
    discussionWordId = sa.Column(sa.BigInteger(), sa.ForeignKey('DiscussionWord.id'), nullable=False, primary_key=True)
    count = sa.Column(sa.Integer())


class DiscussionHashtagData(Base):
    __tablename__ = 'DiscussionHashtagData'

    discussionDataId = sa.Column(sa.BigInteger(), sa.ForeignKey('DiscussionData.id'), nullable=False, primary_key=True)
    discussionHashtagId = sa.Column(sa.BigInteger(), sa.ForeignKey('DiscussionHashtag.id'), nullable=False,
                                    primary_key=True)


class AggregatedData(Base):
    __tablename__ = 'AggregatedData'

    id = sa.Column(sa.BigInteger(), autoincrement=True, primary_key=True)
    publicationDoi = sa.Column(sa.String(), sa.ForeignKey('Publication.doi'))
    score = sa.Column(sa.Float())


class DebugData(Base):
    __tablename__ = 'DebugData'

    id = sa.Column(sa.BigInteger(), autoincrement=True, primary_key=True)
    info = sa.Column(sa.String())
    data = sa.Column(JSON())
