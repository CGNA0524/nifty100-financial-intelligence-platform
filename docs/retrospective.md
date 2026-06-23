# Sprint 1 Retrospective

Sprint Goal:
Build a fully loaded and validated SQLite database for the N100 Financial Intelligence Platform.

Completed:
- Day 01 Environment Setup
- Day 02 Excel Loader & Normaliser
- Day 03 Schema Validator (DQ-01 to DQ-16)
- Day 04 SQLite Database Schema
- Day 05 Full Data Load
- Day 06 Manual Data Quality Review
- Day 07 Sprint Wrap-Up & Review

Achievements:
- 12 datasets processed
- SQLite database created successfully
- Foreign Key Check = 0
- 35/35 unit tests passed
- Critical DQ Issues = 0
- Exploratory SQL queries created

Challenges:
- Duplicate company-year records
- Multiple year formats
- Validator initially checking raw files instead of database

Resolutions:
- Added deduplication logic
- Improved year validation with regex
- Migrated validation to SQLite database

Final Outcome:
Sprint 1 Completed Successfully.