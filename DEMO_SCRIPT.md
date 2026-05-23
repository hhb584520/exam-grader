# ExamGrader Demo Video Script

## Video Overview
- **Duration**: Approximately 3 minutes
- **Style**: Professional, clear, rhythmic
- **Target Audience**: Educators, school administrators, technical decision makers

---

## Scene Script

### Scene 1: Opening Introduction (0:00 - 0:15)
| Screen | Narration | Subtitles |
|--------|----------|-----------|
| Screen shows ExamGrader Logo, gradient background | "Hello everyone, welcome to the ExamGrader Intelligent Exam Grading System feature demonstration." | ExamGrader - Intelligent Exam Grading System |
| Logo fades in, displaying core feature icons | "ExamGrader is an AI-based education solution that achieves automated exam grading, intelligent wrong question analysis, and personalized review suggestions in a complete learning closed loop." | Smart Grading · Wrong Question Analysis · Personalized Review |

### Scene 2: Upload Exam Paper (0:15 - 0:45)
| Screen | Narration | Subtitles |
|--------|----------|-----------|
| Switch to Web interface, showing "Upload Exam" page | "First, let's upload an exam paper." | 📤 Upload Exam |
| Presenter clicks file selection button, selects an exam file | "The system supports multiple file formats, including PDF, Word, and text files." | Supports PDF, Word, TXT |
| Fill in exam information: Exam ID, title, subject | "Fill in basic exam information, including unique identifier, title, and subject." | Exam ID · Title · Subject |
| Click "Upload Exam" button, showing success prompt | "Click upload, and the exam paper is successfully saved in the system." | ✅ Upload Successful |

### Scene 3: Exam Grading (0:45 - 1:30)
| Screen | Narration | Subtitles |
|--------|----------|-----------|
| Switch to "Exam Grading" page | "Next is the core feature - Intelligent Exam Grading." | ✏️ Exam Grading |
| Enter Exam ID and Student ID | "Enter the Exam ID and Student ID to grade." | Exam ID · Student ID |
| Enter student answers (JSON format) | "Enter student answers, can be in JSON format or upload answer file directly." | Student Answers |
| Click "Start Grading" button, showing loading animation | "Click start grading, AI will automatically analyze each question." | 🤖 AI Intelligent Grading... |
| Display grading results: score, accuracy, detailed analysis | "Grading complete! The system provides total score, accuracy rate, and detailed analysis for each question." | Score: 85/100 · Accuracy: 85% |
| Show wrong question details: error reasons, knowledge point tags | "For wrong questions, the system marks error reasons and involved knowledge points." | ❌ Error Reasons · Knowledge Points |

### Scene 4: Wrong Question Book (1:30 - 2:00)
| Screen | Narration | Subtitles |
|--------|----------|-----------|
| Switch to "Wrong Question Book" page | "The system automatically collects student wrong questions, forming a personal wrong question notebook." | 📚 Wrong Question Book |
| Display wrong question list, sorted by time | "Wrong questions are sorted chronologically for easy student review." | Sorted by Time |
| Click on a wrong question to expand details | "Each wrong question includes question content, student answer, and correct answer comparison." | Answer Comparison |
| Display difficulty tags and knowledge point tags | "The system also tags question difficulty levels and related knowledge points." | Difficulty: Medium · Knowledge Points |

### Scene 5: Review Suggestions (2:00 - 2:30)
| Screen | Narration | Subtitles |
|--------|----------|-----------|
| Switch to "Review Suggestions" page | "Based on wrong question analysis, the system generates personalized review suggestions." | 🎯 Review Suggestions |
| Click "Get Suggestions" button | "Click get suggestions, AI will analyze student weak areas." | Analyzing Weak Areas |
| Display knowledge point analysis chart | "The system displays knowledge point mastery analysis." | 📊 Knowledge Point Analysis |
| Display weak knowledge point list | "Identifies weak knowledge points that need key review." | ⚠️ Weak Knowledge Points |
| Display review suggestions and learning plan | "Provides targeted review suggestions and learning plan." | 💡 Review Suggestions · 📅 Learning Plan |

### Scene 6: Check Paper Generation (2:30 - 3:00)
| Screen | Narration | Subtitles |
|--------|----------|-----------|
| Switch to "Check Paper" page | "Finally, the system can generate personalized check papers based on student weak areas." | 📝 Check Paper Generation |
| Enter number of questions, click "Generate Check Paper" | "Set the number of questions, and the system will automatically generate targeted questions." | Number of Questions: 10 |
| Display generated check paper | "The check paper includes various question types, covering knowledge points students need to strengthen." | Personalized Check Paper |
| Display reference answers and knowledge points for each question | "Each question comes with reference answer and knowledge points examined." | Reference Answer · Knowledge Points |

### Scene 7: Closing (3:00 - 3:15)
| Screen | Narration | Subtitles |
|--------|----------|-----------|
| Return to ExamGrader Logo page | "Above are the core feature demonstrations of ExamGrader." | ExamGrader |
| Display technical architecture diagram | "ExamGrader is built on OPEA components, supporting large-scale deployment." | Built on OPEA |
| Display contact information | "Thank you for watching! For more information, please contact us." | Thank You! |

---

## Recording Guide

### Preparation
1. **Environment Setup**
   - Start LLM Service (vLLM)
   - Start Embedding Service
   - Start PostgreSQL + pgvector
   - Start Agent Service
   - Start API Service
   - Start Web UI

2. **Test Data Preparation**
   - Prepare a sample exam (including multiple choice, fill-in-the-blank, essay questions)
   - Prepare a student answer sheet
   - Ensure test data exists in the database

3. **Recording Tools**
   - Screen recording software (such as OBS Studio, Camtasia)
   - Microphone (ensure clear audio quality)
   - Presenter preparation

### Recording Steps
1. Open browser, access Web UI (http://localhost:5173)
2. Demonstrate each feature in script order
3. Pay attention to operation speed, ensure audience can see clearly
4. Can record without narration first, add later in post-production
5. Ensure each feature demonstration is complete

### Post-Production
1. Add background music (soft background music)
2. Add narration
3. Add subtitles
4. Add transition effects
5. Adjust video rhythm
6. Export as MP4 format

---

## Demo Data Examples

### Exam Content Example
```
Exam ID: math_test_001
Title: High School Math Midterm Exam
Subject: Math

1. Multiple Choice (5 points each)
   1.1 Given function f(x) = x² + 2x + 1, then f(2) = ?
      A. 5 B. 8 C. 9 D. 10
   
2. Fill-in-the-blank (5 points each)
   2.1 The 10th term of arithmetic sequence 1, 3, 5, 7, ... is ____

3. Essay Questions (20 points each)
   3.1 Find the extreme points of function y = x³ - 3x² + 2
```

### Student Answer Example
```json
{
  "question_1": "C",
  "question_2": "19",
  "question_3": "Differentiating the function gives y' = 3x² - 6x = 3x(x-2), set y' = 0, get x = 0 or x = 2. When x = 0, get maximum value, when x = 2, get minimum value."
}
```

---

## Notes
1. Ensure stable network connection during demonstration
2. Test all features in advance to avoid errors during demonstration
3. Keep operations smooth without too many pauses
4. Narration should be clear, professional, moderate speaking speed
5. Subtitles should be accurate and concise
