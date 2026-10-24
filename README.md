
# Study Buddy Chatbot

A beginner-friendly study assistant that helps students
learn from their own notes.

## Features

- Upload PDF and TXT study notes
- Paste notes directly into the app
- Search notes using question keywords
- Generate multiple-choice quizzes
- Check answers and view quiz scores
- Review the original sentences from notes

## Technologies Used

- Python
- Streamlit
- PyPDF2
- Regular Expressions
- Basic Retrieval-Augmented Generation concepts

## How It Works

The application extracts text from uploaded notes.
It retrieves sentences that match the student's question
and generates simple fill-in-the-blank MCQs from the notes.

This is a basic retrieval-based prototype, not a full
LLM-powered RAG system.

## Run Locally

Install the required libraries:

pip install -r requirements.txt

Start the application:

streamlit run app.py

## Future Improvements

- Add an AI language model
- Improve semantic search with embeddings
- Add summaries and flashcards
- Save quiz history
