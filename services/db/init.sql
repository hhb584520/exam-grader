CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS exam_papers (
    paper_id TEXT PRIMARY KEY,
    title TEXT,
    subject TEXT,
    content TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS student_answers (
    id SERIAL PRIMARY KEY,
    paper_id TEXT,
    student_id TEXT,
    answers TEXT,
    score FLOAT,
    graded BOOLEAN DEFAULT FALSE,
    graded_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS wrong_questions (
    id SERIAL PRIMARY KEY,
    question_id TEXT,
    student_id TEXT,
    paper_id TEXT,
    question_content TEXT,
    student_answer TEXT,
    correct_answer TEXT,
    knowledge_points TEXT,
    difficulty TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    step_analysis TEXT,
    correct_steps TEXT,
    common_mistakes TEXT,
    teaching_suggestions TEXT
);

CREATE TABLE IF NOT EXISTS knowledge_points (
    id SERIAL PRIMARY KEY,
    point_id TEXT,
    subject TEXT,
    topic TEXT,
    description TEXT,
    correct_methods TEXT,
    common_errors TEXT,
    teaching_tips TEXT,
    solving_steps TEXT,
    example_questions TEXT,
    difficulty_level TEXT,
    embedding vector(1024),
    related_topics TEXT,
    prerequisite_knowledge TEXT,
    common_pitfalls TEXT,
    troubleshooting_guide TEXT,
    best_practices TEXT,
    alternative_methods TEXT,
    shortcut_techniques TEXT,
    optimization_tips TEXT
);

CREATE TABLE IF NOT EXISTS step_templates (
    id SERIAL PRIMARY KEY,
    subject TEXT,
    topic TEXT,
    method_name TEXT,
    steps TEXT,
    examples TEXT,
    common_mistakes TEXT,
    error_types TEXT,
    correction_strategies TEXT,
    embedding vector(1024),
    step_checkpoints TEXT,
    common_errors_by_step TEXT,
    step_scoring_guide TEXT,
    hints_for_each_step TEXT,
    common_confusions TEXT,
    misconception_explanations TEXT
);

CREATE TABLE IF NOT EXISTS student_analysis (
    id SERIAL PRIMARY KEY,
    student_id TEXT,
    analysis_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    weak_topics TEXT,
    error_patterns TEXT,
    learning_style TEXT,
    improvement_suggestions TEXT
);

CREATE TABLE IF NOT EXISTS class_analysis (
    id SERIAL PRIMARY KEY,
    class_id TEXT,
    analysis_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    overall_performance TEXT,
    common_errors TEXT,
    teaching_focus TEXT,
    student_progress TEXT
);

CREATE TABLE IF NOT EXISTS learning_materials (
    id SERIAL PRIMARY KEY,
    material_id TEXT UNIQUE,
    title TEXT,
    material_type TEXT,
    subject TEXT,
    topic TEXT,
    knowledge_points TEXT,
    description TEXT,
    url TEXT,
    duration_minutes INTEGER,
    difficulty_level TEXT,
    target_audience TEXT,
    tags TEXT,
    author TEXT,
    source TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    embedding vector(1024),
    effectiveness_score FLOAT DEFAULT 0.0,
    usage_count INTEGER DEFAULT 0,
    avg_rating FLOAT DEFAULT 0.0
);

CREATE TABLE IF NOT EXISTS material_ratings (
    id SERIAL PRIMARY KEY,
    material_id TEXT,
    student_id TEXT,
    rating INTEGER CHECK (rating >= 1 AND rating <= 5),
    effectiveness_score FLOAT,
    learning_outcome TEXT,
    time_spent_minutes INTEGER,
    completed BOOLEAN DEFAULT FALSE,
    feedback TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (material_id) REFERENCES learning_materials(material_id)
);

CREATE TABLE IF NOT EXISTS exam_papers_archive (
    id SERIAL PRIMARY KEY,
    year INTEGER,
    province TEXT,
    subject TEXT,
    paper_type TEXT,
    title TEXT,
    content TEXT,
    knowledge_points TEXT,
    difficulty_distribution TEXT,
    total_score INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    embedding vector(1024)
);

CREATE TABLE IF NOT EXISTS knowledge_mastery (
    id SERIAL PRIMARY KEY,
    student_id TEXT,
    knowledge_point_id TEXT,
    mastery_level FLOAT CHECK (mastery_level >= 0 AND mastery_level <= 1),
    practice_count INTEGER DEFAULT 0,
    correct_count INTEGER DEFAULT 0,
    last_practice_at TIMESTAMP,
    improvement_trend TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(student_id, knowledge_point_id)
);

CREATE TABLE IF NOT EXISTS review_plans (
    id SERIAL PRIMARY KEY,
    student_id TEXT,
    plan_type TEXT,
    start_date TIMESTAMP,
    end_date TIMESTAMP,
    target_knowledge_points TEXT,
    daily_tasks TEXT,
    progress FLOAT DEFAULT 0.0,
    status TEXT DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS grading_templates (
    id SERIAL PRIMARY KEY,
    template_id TEXT UNIQUE,
    subject TEXT,
    question_type TEXT,
    template_name TEXT,
    scoring_rules TEXT,
    step_scoring TEXT,
    common_errors TEXT,
    auto_comments TEXT,
    created_by TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    embedding vector(1024)
);

CREATE TABLE IF NOT EXISTS student_material_assignments (
    id SERIAL PRIMARY KEY,
    student_id TEXT,
    material_id TEXT,
    assigned_by TEXT,
    assigned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    due_date TIMESTAMP,
    status TEXT DEFAULT 'assigned',
    completed_at TIMESTAMP,
    effectiveness_score FLOAT,
    FOREIGN KEY (material_id) REFERENCES learning_materials(material_id)
);

CREATE TABLE IF NOT EXISTS exam_knowledge_analysis (
    id SERIAL PRIMARY KEY,
    exam_id TEXT,
    year INTEGER,
    subject TEXT,
    knowledge_point_id TEXT,
    frequency INTEGER DEFAULT 1,
    difficulty_level TEXT,
    question_types TEXT,
    avg_score FLOAT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_student_wrong_questions ON wrong_questions(student_id);
CREATE INDEX IF NOT EXISTS idx_paper_id ON exam_papers(paper_id);
CREATE INDEX IF NOT EXISTS idx_knowledge_subject ON knowledge_points(subject);
CREATE INDEX IF NOT EXISTS idx_material_type ON learning_materials(material_type);
CREATE INDEX IF NOT EXISTS idx_material_knowledge ON learning_materials(knowledge_points);
CREATE INDEX IF NOT EXISTS idx_mastery_student ON knowledge_mastery(student_id);
CREATE INDEX IF NOT EXISTS idx_exam_year ON exam_papers_archive(year);
