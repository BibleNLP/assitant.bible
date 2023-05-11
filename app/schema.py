'''Defines all input and output classes for API endpoints'''
#pylint: disable=too-many-lines
from typing import Optional, List
from enum import Enum
from pydantic import BaseModel, Field, AnyUrl#, constr, validator

class NormalResponse(BaseModel):
    '''Response with only a message'''
    message : str = Field(...,example="App is up and running")

class ErrorResponse(BaseModel):
    '''Common error response format'''
    error: str = Field(...,example="Database Error")
    details: str = Field(...,example="Violation of unique constraint blah blah blah")

class DBSelector(BaseModel):
    '''The credentials to connect to a remotely hosted chorma DB'''
    dbHost: str = Field(..., desc="Host name to connect to a remote chroma DB deployment")
    dbPort: str = Field(..., desc="Port to connect to a remote chroma DB deployment")
    collectionName:str = Field(..., desc="Collection to connect to a remote chroma DB deployment")

class ChatIn(BaseModel):
    '''Input chat text from the user'''
    text: str = Field(...,example="Who is Jesus?")
    chatId: Optional[str] = Field(None, example=10001)
    sources: List[str] = Field(None,
        desc = "The list of documents to be used for answering",
        example=["tyndale", "Open Bible Stories", "Paratext User Manual", "The Bible"])
    db: DBSelector = Field(None)

class ChatOut(BaseModel):
    '''Chat response from bot to user'''
    text: str = Field(...,example="Good Morning to you too!")
    chatId: str = Field(...,example=10001)
    sources: List[AnyUrl] = Field(None,
        example=["https://www.biblegateway.com/passage/?search=Genesis+1%3A1&version=NIV",
                 "https://git.door43.org/Door43-Catalog/en_tw/src/branch/master/"+\
                 "bible/other/creation.md"])
    media: List[AnyUrl] = Field(None,
        example=["https://www.youtube.com/watch?v=teu7BCZTgDs"])

class JobStatus(str, Enum):
    '''Valid values for Background Job Status'''
    QUEUED = 'queued'
    STARTED = 'started'
    FINISHED = 'finished'
    FAILED = 'failed'

class Job(BaseModel):
    '''Response object of Background Job status check'''
    jobId: int = Field(..., example=100000)
    status: JobStatus = Field(..., example="started")
    output: dict = Field(None, example={
        'error': 'Gateway Error',
        'details': 'Connect to OpenAI terminated unexpectedly'
        })

class SourceSentence(BaseModel):
    '''List of sentences to be vectorised and stored for later querying'''
    sentId: str = Field(...,
                        example="NIV Bible Mat 1:1-20",
                        desc="Unique for a sentence. Used by the LLM to specify which document "+\
                        "it answers from. Better to combine the source tag and a serial number.")
    sourceTag: str = Field(...,
                        example="paratext user manual",
                        desc="The common tag for all sentences under a set. "+\
                        "Used for specifying access rules and filtering during querying")
    text: str = Field(..., desc="The sentence to be vectorised and used for question answering")
    link: AnyUrl = Field(None, desc="The links to fetch the actual resource. "+\
                        "To be used by end user link a search result")
    media: List[AnyUrl] = Field(None, desc="Additional media links, like images, videos etc "+\
                        "to be used in output to make the chat interface multimodel")