
from uuid import uuid4

from sqlmodel import select

from db.crud import (load_history, load_summary, load_transcript, save_message,
                     save_summary, save_transcript)
from db.models import ChatMessage
from tests.conftest import in_memory_db


# Test for save_message and load_history
def test_save_and_load_message_history(in_memory_db):
    user_id = str(uuid4())
    video_id = "test_video_123"
    question_1 = "Q1?"
    answer_1 = "A1!"
    question_2 = "Q2?"
    answer_2 = "A2!"
    # Save first message
    save_message(db=in_memory_db, question=question_1, answer=answer_1, video_id=video_id, user_id=user_id)
    statement = select(ChatMessage)
    result = in_memory_db.exec(statement).all()
    
    assert len(result) == 1
    assert result[0].question == question_1
    assert result[0].answer == answer_1

    # Save second message
    save_message(db=in_memory_db, question=question_2, answer=answer_2, video_id=video_id, user_id=user_id)

    # Load history using crud
    history = load_history(db = in_memory_db, user_id= user_id, video_id=video_id)

    # Verify both messages are loaded in correct order
    assert len(history) == 2
    assert history[0].question == question_1
    assert history[0].answer == answer_1
    assert history[1].question == question_2
    assert history[1].answer == answer_2

    empty_history = load_history(db=in_memory_db, user_id="non_existent_user", video_id="non_existent_video")
    assert len(empty_history) == 0

# Test for save_summary and load_summary
def test_save_and_load_summary(in_memory_db):
    video_id = "summary_video_id"
    title = "Video title"
    metadata = {"source":"youtube"}
    summary_text = "This is a concise summary of the video content."

    # Save the summary
    save_summary(db=in_memory_db, video_id=video_id, title=title, summary=summary_text, metadata=metadata)

    # Load the summaries
    loaded_summary = load_summary(db=in_memory_db, video_id=video_id)

    assert loaded_summary is not None
    assert loaded_summary.video_id == video_id
    assert loaded_summary.title == title
    assert loaded_summary.summary == summary_text
    assert loaded_summary.doc_metadata == metadata

    # Test loading a non-existent summary
    non_existent_summary = load_summary(db=in_memory_db, video_id="non_existent_summary_video_id")
    assert non_existent_summary is None


# Test for save_transcript and load_transcript
def test_save_and_load_transcript(in_memory_db):
    video_id = "summary_video_id"
    title = "Video title"
    metadata = {"source":"youtube"}
    transcript = "This is a transcript of the video content."    

    # Save the transcript
    save_transcript(db=in_memory_db, video_id=video_id, title=title, transcript=transcript, metadata=metadata)

    # Load the transcript
    loaded_transcript = load_transcript(db=in_memory_db, video_id=video_id)

    assert loaded_transcript is not None
    assert loaded_transcript.video_id == video_id
    assert loaded_transcript.title == title
    assert loaded_transcript.transcript == transcript
    assert loaded_transcript.doc_metadata == metadata

    # Test loading a non-existent summary
    non_existent_transcript = load_transcript(db=in_memory_db, video_id="non_existent_transcript_video_id")
    assert non_existent_transcript is None