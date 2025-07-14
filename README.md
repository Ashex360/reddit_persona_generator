# REDDIT USER PERSONA GENERATOR

A Python tool that analyzes a Reddit user's public activity (posts and comments) to generate a psychological and behavioral persona report.

♦️ PROJECT OVERVIEW

This script uses the Reddit API to collect and analyze a user’s posts and comments. It extracts insights such as:

* Top interests based on subreddit activity
* Personality traits (analytical, emotional, helpful, etc.)
* Communication style and sentiment
* Goals and frustrations (with direct citations)
* Behavior patterns like posting frequency, humor, opinions, etc.

The output is a clean `.txt` report that’s ideal for user research, academic analysis, or persona generation.

♦️ USE CASES

* Product teams doing user research
* Students or professionals doing behavior analysis
* Content strategists or UX researchers
* Developers experimenting with natural language analysis


♦️ TECH STACK

* Python (Core logic)
* PRAW (Python Reddit API Wrapper)
* Regex (Pattern matching and extraction)
* datetime, collections (Data formatting and processing)

♦️ FEATURES

* Clean up markdown, links, and Reddit formatting
* Detect subreddit interests and categorize them
* Analyze user behavior (active hours, question use, debates)
* Infer personality using text pattern recognition
* Extract goals and frustrations from text
* Save result as a local `.txt` report


♦️ REQUIREMENTS

* Python 3.8 or higher
* Reddit API credentials (client ID, secret)

To install dependencies:
pip install praw

♦️ HOW TO USE

1. Clone the project:
   git clone : https://github.com/Ashex360/reddit_persona_generator.git

2. Create a Reddit script app:
   Go to [https://www.reddit.com/prefs/apps](https://www.reddit.com/prefs/apps) and create a script app to get credentials.

3. Edit the script and insert your Reddit API keys:
   client\_id='your\_client\_id'
   client\_secret='your\_client\_secret'
   user\_agent='any\_name\_you\_like'

4. Run the script:
   python reddit\_persona\_generator.py

5. Enter a Reddit username (or full profile URL) when prompted.

6. The script will generate a detailed persona and save it as:
   \[username]\_persona.txt

♦️ SAMPLE OUTPUT (snippet)

REDDIT USER PERSONA: U/SPEZ

Account Age: 16 years, 3 months
Karma: 42,000 (comment) | 10,000 (post)
Premium Member: No
Moderator: Yes

Top Interests:

* Technology: programming, linux
* Movies: marvel, television

Personality Traits:

* Traits: analytical, curious, opinionated
* Communication Style: detailed
* Sentiment: positive

Goals:

* I want to understand how Linux works at the kernel level.

Frustrations:

* It's frustrating that Apple locks everything down.

 ♦️WHAT I LEARNED

* How to use Reddit API securely
* Working with real-time text data and regex
* Generating human-like insights from user behavior
* Writing modular and clean Python code for practical use cases

---

♦️ FUTURE IMPROVEMENTS

* Export report as PDF
* Add visualization (matplotlib/bar charts of subreddit activity)
* Add sentiment scoring using NLP tools
* Build a web interface with Streamlit or Flask


♦️ ABOUT ME

Hi, I’m Ashish Sarda, a student of Electronics & Computer Engineering.
I love solving real-world problems with smart backend logic, and this project reflects my interest in combining psychology with technology.

LinkedIn: https://www.linkedin.com/in/ashish-sarda-5051982a3/
GitHub: https://github.com/Ashex360


## LICENSE

MIT License
