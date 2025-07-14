import praw
import prawcore
from datetime import datetime
import re
from collections import defaultdict
import sys

def clean_text(text):
    """Clean and format text for persona generation"""
    if not text:
        return ""
    
    text = re.sub(r'\[(.*?)\]\(.*?\)', r'\1', text)
    text = re.sub(r'`{3}.*?`{3}', '', text, flags=re.DOTALL)
    text = re.sub(r'`.*?`', '', text)
    text = re.sub(r'&[#\w]+;', '', text)
    text = re.sub(r'http\S+', '', text)
    text = re.sub(r'\n+', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def extract_username_from_url(url):
    """Extract username from various Reddit URL formats"""
    url = url.strip().lower()
    
    patterns = [
        r'reddit\.com/user/([^/]+)',
        r'reddit\.com/u/([^/]+)',
        r'reddit\.com/user/([^/]+)/',
        r'reddit\.com/u/([^/]+)/',
        r'^/user/([^/]+)',
        r'^/u/([^/]+)'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    
    return url.split('/')[-1].split('?')[0]

def initialize_reddit():
    """Initialize and return a Reddit instance with error handling"""
    try:
        reddit = praw.Reddit(
            client_id='VsLE8-ZPXO2Kp5ezsthxOg',
            client_secret='biwUgrlpA5NFZGxPM3ayagi-JRM9ew',
            user_agent='Calm_Piano_1083'
        )
        # Test the connection
        reddit.user.me()
        return reddit
    except Exception as e:
        print(f"Failed to initialize Reddit API: {str(e)}")
        print("Please verify your client ID and client secret")
        sys.exit(1)

def get_user_data(reddit, username):
    """Collect user data with improved error handling"""
    try:
        user = reddit.redditor(username)
        user._fetch()  # Force fetch user data
    except prawcore.exceptions.NotFound:
        print(f"Error: User u/{username} not found")
        return None
    except prawcore.exceptions.Forbidden:
        print(f"Error: Access to u/{username}'s profile is forbidden (may be banned or private)")
        return None
    except Exception as e:
        print(f"Error accessing user {username}: {str(e)}")
        return None

    try:
        user_data = {
            'username': username,
            'created_utc': datetime.utcfromtimestamp(user.created_utc).strftime('%Y-%m-%d'),
            'comment_karma': user.comment_karma,
            'link_karma': user.link_karma,
            'is_mod': user.is_mod,
            'is_gold': user.is_gold,
            'comments': [],
            'posts': [],
            'citations': []
        }
    except Exception as e:
        print(f"Error fetching user info: {str(e)}")
        return None

    # Collect comments
    try:
        comments = list(user.comments.new(limit=100))
        for comment in comments:
            try:
                user_data['comments'].append({
                    'id': comment.id,
                    'created': datetime.utcfromtimestamp(comment.created_utc).strftime('%Y-%m-%d'),
                    'subreddit': str(comment.subreddit.display_name),
                    'score': comment.score,
                    'text': clean_text(comment.body),
                    'url': f"https://reddit.com{comment.permalink}"
                })
            except Exception as e:
                print(f"Error processing comment {comment.id}: {str(e)}")
                continue
    except Exception as e:
        print(f"Error fetching comments: {str(e)}")

    # Collect posts
    try:
        submissions = list(user.submissions.new(limit=50))
        for submission in submissions:
            try:
                user_data['posts'].append({
                    'id': submission.id,
                    'created': datetime.utcfromtimestamp(submission.created_utc).strftime('%Y-%m-%d'),
                    'subreddit': str(submission.subreddit.display_name),
                    'score': submission.score,
                    'title': clean_text(submission.title),
                    'text': clean_text(submission.selftext) if submission.selftext else '',
                    'url': f"https://reddit.com{submission.permalink}",
                    'is_self': submission.is_self
                })
            except Exception as e:
                print(f"Error processing post {submission.id}: {str(e)}")
                continue
    except Exception as e:
        print(f"Error fetching posts: {str(e)}")

    return user_data

def calculate_account_age(created_date):
    """Calculate account age in years with months"""
    created = datetime.strptime(created_date, '%Y-%m-%d')
    delta = datetime.now() - created
    years = delta.days // 365
    months = (delta.days % 365) // 30
    return f"{years} years, {months} months"

def analyze_interests(user_data):
    """Analyze user's interests based on subreddit activity"""
    subreddit_counts = defaultdict(int)
    
    for comment in user_data['comments']:
        subreddit_counts[comment['subreddit'].lower()] += 1
    
    for post in user_data['posts']:
        subreddit_counts[post['subreddit'].lower()] += 1
    
    top_subreddits = sorted(subreddit_counts.items(), key=lambda x: x[1], reverse=True)[:5]
    
    interest_categories = defaultdict(list)
    category_mapping = {
        'technology': ['programming', 'python', 'technology', 'android', 'apple', 'linux'],
        'gaming': ['gaming', 'games', 'pcgaming', 'ps4', 'xbox'],
        'sports': ['sports', 'nba', 'nfl', 'soccer', 'baseball'],
        'movies': ['movies', 'television', 'netflix', 'marvel'],
        'science': ['science', 'space', 'physics', 'askscience'],
        'health': ['fitness', 'nutrition', 'loseit', 'bodybuilding'],
        'finance': ['personalfinance', 'investing', 'stocks', 'financialindependence']
    }
    
    for sub, count in top_subreddits:
        matched = False
        for category, keywords in category_mapping.items():
            if any(keyword in sub for keyword in keywords):
                interest_categories[category].append(sub)
                matched = True
                break
        if not matched:
            interest_categories['other'].append(sub)
    
    return {
        'top_subreddits': [sub[0] for sub in top_subreddits],
        'interest_categories': dict(interest_categories)
    }

def analyze_personality(user_data):
    """Analyze personality traits from text content"""
    personality = {
        'traits': [],
        'communication_style': '',
        'sentiment': 'neutral'
    }
    
    all_text = ' '.join([c['text'] for c in user_data['comments']] + [p['text'] for p in user_data['posts']]).lower()
    
    trait_indicators = {
        'analytical': ['data', 'research', 'study', 'evidence', 'according to', 'statistics'],
        'emotional': ['i feel', 'emotion', 'relationship', 'happy', 'sad', 'angry'],
        'helpful': ['help', 'advice', 'suggestion', 'support', 'recommend'],
        'humorous': ['joke', 'funny', 'lol', 'haha', 'lmao'],
        'curious': ['why', 'how', 'what if', 'question', 'wonder'],
        'opinionated': ['i think', 'i believe', 'in my opinion', 'the truth is']
    }
    
    for trait, indicators in trait_indicators.items():
        if any(indicator in all_text for indicator in indicators):
            personality['traits'].append(trait)
    
    avg_comment_length = sum(len(c['text']) for c in user_data['comments']) / max(1, len(user_data['comments']))
    if avg_comment_length > 300:
        personality['communication_style'] = 'detailed/verbose'
    elif avg_comment_length > 100:
        personality['communication_style'] = 'balanced'
    else:
        personality['communication_style'] = 'concise'
    
    positive_words = ['love', 'great', 'awesome', 'amazing', 'happy', 'wonderful']
    negative_words = ['hate', 'awful', 'terrible', 'bad', 'angry', 'frustrated']
    
    positive_count = sum(1 for word in positive_words if word in all_text)
    negative_count = sum(1 for word in negative_words if word in all_text)
    
    if positive_count > negative_count + 3:
        personality['sentiment'] = 'positive'
    elif negative_count > positive_count + 3:
        personality['sentiment'] = 'negative'
    
    return personality

def extract_goals_frustrations(user_data):
    """Extract goals and frustrations with citations"""
    goals = []
    frustrations = []
    
    goal_patterns = [
        r'i (want|need|would like) to (.*?)(\.|\?|$)',
        r'my goal is to (.*?)(\.|\?|$)',
        r'i\'m trying to (.*?)(\.|\?|$)'
    ]
    
    frustration_patterns = [
        r'i (hate|dislike) (.*?)(\.|\?|$)',
        r'it\'s (annoying|frustrating) that (.*?)(\.|\?|$)',
        r'the problem with (.*?)(\.|\?|$)',
        r'i wish (.*?)(\.|\?|$)'
    ]
    
    for comment in user_data['comments']:
        text = comment['text'].lower()
        
        for pattern in goal_patterns:
            matches = re.finditer(pattern, text)
            for match in matches:
                goal = match.group(2).strip()
                if goal and len(goal.split()) > 2:
                    goals.append(goal)
                    user_data['citations'].append({
                        'type': 'goal',
                        'text': goal,
                        'source': comment['url']
                    })
        
        for pattern in frustration_patterns:
            matches = re.finditer(pattern, text)
            for match in matches:
                frustration = match.group(2).strip() if len(match.groups()) > 1 else match.group(1).strip()
                if frustration and len(frustration.split()) > 2:
                    frustrations.append(frustration)
                    user_data['citations'].append({
                        'type': 'frustration',
                        'text': frustration,
                        'source': comment['url']
                    })
    
    for post in user_data['posts']:
        text = (post['title'] + ' ' + post['text']).lower()
        
        for pattern in goal_patterns:
            matches = re.finditer(pattern, text)
            for match in matches:
                goal = match.group(2).strip()
                if goal and len(goal.split()) > 2:
                    goals.append(goal)
                    user_data['citations'].append({
                        'type': 'goal',
                        'text': goal,
                        'source': post['url']
                    })
        
        for pattern in frustration_patterns:
            matches = re.finditer(pattern, text)
            for match in matches:
                frustration = match.group(2).strip() if len(match.groups()) > 1 else match.group(1).strip()
                if frustration and len(frustration.split()) > 2:
                    frustrations.append(frustration)
                    user_data['citations'].append({
                        'type': 'frustration',
                        'text': frustration,
                        'source': post['url']
                    })
    
    return {
        'goals': list(set(goals)),
        'frustrations': list(set(frustrations))
    }

def analyze_behavior(user_data):
    """Analyze user behavior patterns"""
    behavior = {
        'post_frequency': len(user_data['posts']),
        'comment_frequency': len(user_data['comments']),
        'post_types': {
            'text': 0,
            'link': 0
        },
        'engagement_patterns': {
            'questions': 0,
            'opinions': 0,
            'information_sharing': 0,
            'humor': 0,
            'debate': 0
        },
        'active_times': defaultdict(int)
    }
    
    for post in user_data['posts']:
        if post['is_self']:
            behavior['post_types']['text'] += 1
        else:
            behavior['post_types']['link'] += 1
    
    for comment in user_data['comments']:
        text = comment['text'].lower()
        
        if '?' in text:
            behavior['engagement_patterns']['questions'] += 1
        if any(word in text for word in ['i think', 'i believe', 'in my opinion']):
            behavior['engagement_patterns']['opinions'] += 1
        if any(word in text for word in ['source:', 'according to', 'study shows', 'research indicates']):
            behavior['engagement_patterns']['information_sharing'] += 1
        if any(word in text for word in ['lol', 'haha', 'funny', 'joke']):
            behavior['engagement_patterns']['humor'] += 1
        if any(word in text for word in ['actually', 'wrong', 'disagree', 'but']):
            behavior['engagement_patterns']['debate'] += 1
        
        hour = datetime.strptime(comment['created'], '%Y-%m-%d').hour
        behavior['active_times'][f"{hour}:00-{hour+1}:00 UTC"] += 1
    
    sorted_times = sorted(behavior['active_times'].items(), key=lambda x: x[1], reverse=True)[:3]
    behavior['top_active_times'] = [time[0] for time in sorted_times]
    
    return behavior

def generate_persona_report(user_data):
    account_age = calculate_account_age(user_data['created_utc'])
    interests = analyze_interests(user_data)
    personality = analyze_personality(user_data)
    goals_frustrations = extract_goals_frustrations(user_data)
    behavior = analyze_behavior(user_data)

    star = "★"
    divider = "═" * 60
    sub_divider = "-" * 50

    report = f"{star*3} REDDIT USER PERSONA REPORT — u/{user_data['username']} {star*3}\n"
    report += divider + "\n\n"

    # 🔹 BASIC PROFILE
    report += f"👤 USER SNAPSHOT\n{sub_divider}\n"
    report += f"• Account Age     : {account_age}\n"
    report += f"• Comment Karma   : {user_data['comment_karma']:,}\n"
    report += f"• Post Karma      : {user_data['link_karma']:,}\n"
    report += f"• Premium Member  : {'✅ Yes' if user_data['is_gold'] else '❌ No'}\n"
    report += f"• Moderator Role  : {'✅ Yes' if user_data['is_mod'] else '❌ No'}\n"

    # 🔹 INTERESTS
    report += f"\n💡 INTEREST AREAS\n{sub_divider}\n"
    report += f"Most Active Subreddits: {', '.join(interests['top_subreddits']) or 'N/A'}\n\n"
    report += "Interest Categories:\n"
    for category, subs in interests['interest_categories'].items():
        if subs:
            report += f"  🔸 {category.capitalize():<12}: {', '.join(subs)}\n"

    # 🔹 BEHAVIOR PATTERNS
    report += f"\n📈 BEHAVIOR INSIGHTS\n{sub_divider}\n"
    report += f"• Posts Made     : {behavior['post_frequency']}\n"
    report += f"• Comments Made  : {behavior['comment_frequency']}\n"
    report += f"• Post Types     : 📝 {behavior['post_types']['text']} text | 🔗 {behavior['post_types']['link']} link\n"
    report += f"• Active Hours   : {', '.join(behavior['top_active_times']) or 'N/A'}\n\n"
    report += "Engagement Style:\n"
    report += f"  ❓ Questions          : {behavior['engagement_patterns']['questions']}\n"
    report += f"  💬 Opinions           : {behavior['engagement_patterns']['opinions']}\n"
    report += f"  📚 Information Sharing: {behavior['engagement_patterns']['information_sharing']}\n"
    report += f"  😄 Humor              : {behavior['engagement_patterns']['humor']}\n"
    report += f"  🔁 Debate             : {behavior['engagement_patterns']['debate']}\n"

    # 🔹 PERSONALITY
    report += f"\n🧠 PERSONALITY OVERVIEW\n{sub_divider}\n"
    traits = ', '.join(personality['traits']) if personality['traits'] else "Not enough data"
    report += f"• Traits             : {traits}\n"
    report += f"• Communication Style: {personality['communication_style']}\n"
    report += f"• General Sentiment  : {personality['sentiment'].capitalize()}\n"

    # 🔹 GOALS
    if goals_frustrations['goals']:
        report += f"\n🎯 GOALS & ASPIRATIONS\n{sub_divider}\n"
        for goal in goals_frustrations['goals']:
            report += f"• {goal.capitalize()}\n"

    # 🔹 FRUSTRATIONS
    if goals_frustrations['frustrations']:
        report += f"\n⚠️  FRUSTRATIONS & PAIN POINTS\n{sub_divider}\n"
        for frustration in goals_frustrations['frustrations']:
            report += f"• {frustration.capitalize()}\n"

    # 🔹 CITATIONS
    if user_data['citations']:
        report += f"\n🔗 INSIGHT SOURCES\n{sub_divider}\n"
        for citation in user_data['citations']:
            report += (
                f"[{citation['type'].capitalize()}] \"{citation['text'].capitalize()}\"\n"
                f" ↳ Source: {citation['source']}\n\n"
            )

    report += divider + "\n📄 Report generated by Reddit Persona Script\n"
    return report

def save_persona_to_file(persona_text, username):
    """Save the persona to a text file"""
    filename = f"{username}_persona.txt"
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(persona_text)
    return filename

def main():
    print("Reddit User Persona Generator")
    print("Created by Ash — built for fun, not perfection ")
    print("----------------------------")
    print("This tool analyzes a Reddit user's activity to create a comprehensive persona.")
    print("Note: You need Reddit API credentials (client ID and client secret) to use this tool.\n")
    
    try:
        reddit = initialize_reddit()
    except Exception as e:
        print(f"Critical error: {str(e)}")
        sys.exit(1)

    profile_url = input("Enter Reddit profile URL or username: ").strip()
    username = extract_username_from_url(profile_url)
    
    if not username:
        print("Error: Could not extract username from the provided input")
        return
    
    print(f"\nAnalyzing user: u/{username}")
    
    try:
        user_data = get_user_data(reddit, username)
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        return
    
    if not user_data:
        print("Failed to generate persona (no user data available)")
        return
    
    try:
        persona_report = generate_persona_report(user_data)
    except Exception as e:
        print(f"Error generating persona: {str(e)}")
        return
    
    try:
        output_file = save_persona_to_file(persona_report, username)
        print(f"\nPersona generated successfully!")
        print(f"Saved to: {output_file}")
    except Exception as e:
        print(f"Error saving persona file: {str(e)}")

if __name__ == "__main__":
    main()