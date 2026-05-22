# Database Service

This service provides PostgreSQL database with pgvector extension for ExamGrader.

## Running

```bash
docker-compose up -d
```

## Connection Details

- Host: localhost
- Port: 5432
- Database: examgrader
- User: postgres
- Password: password

## Tables

1. **exam_papers** - Stores exam papers
2. **student_answers** - Stores student submissions
3. **wrong_questions** - Stores wrong questions for each student
4. **knowledge_points** - Stores knowledge points with embeddings
