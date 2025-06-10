# ZenFlowIt
**Focus, Flow & Freedom in one place**

🌐 **Live Application:** [www.zenflowit.com](http://www.zenflowit.com)

ZenFlowIt is an AI-powered productivity application designed to help users overcome procrastination, build momentum, and accomplish their goals without stress. The application combines smart task management, focus tools, vision boards, and an AI assistant to create a comprehensive productivity ecosystem.


![Screenshot 2025-06-10 140508](https://github.com/user-attachments/assets/5d8412ff-2089-4b82-a60a-385bd2d8cc79)

## 🚀 Features

### Core Features
- **Smart Task Management**: Create, organize, and track tasks with AI-generated subtasks and action plans
- **AI Assistant (ZenCoach)**: Get personalized productivity advice powered by Google's Gemini AI
- **Focus Tools**: Pomodoro technique and focus-enhancing tools with progress tracking
- **Vision Board**: Customizable vision board with different themes, layouts, and goal visualization
- **User Authentication**: Secure user accounts with personal workspaces
- **Rewards System**: Badge rewards for task completion and productivity milestones

### Advanced Features
- **AI-Powered Task Breakdown**: Automatically generate subtasks and detailed action plans
- **Focus Statistics**: Track and visualize focus progress with interactive gauges
- **Customizable Workflows**: Adapt the system to your personal productivity style
- **Multi-Theme Support**: Choose from various color themes and layouts
- **Progress Analytics**: Comprehensive tracking of task completion and productivity trends

## 🎯 Problem Statement

In today's digital world, people are overwhelmed by fragmented productivity tools that create more stress than productivity. ZenFlowIt addresses the **Productivity Paradox** by providing:

- **Unified Experience**: All productivity tools in one intuitive platform
- **Emotional Intelligence**: Recognizes and adapts to user emotions and procrastination patterns
- **Mindful Design**: Calm, stress-free interface that promotes focus and balance
- **AI-Powered Insights**: Smart recommendations based on user behavior and goals

## 🛠️ Technology Stack

### Frontend & Backend
- **Streamlit**: Main application framework
- **Python**: Core programming language
- **HTML/CSS**: Custom styling and layout

### Database & Cloud Services
- **PostgreSQL**: Production database hosted on Amazon RDS (Aurora)
- **SQLite**: Initial development database
- **AWS**: Cloud infrastructure and deployment

### AI & Integration
- **Google Gemini AI**: Powers the ZenCoach assistant
- **Email Services**: User notifications and welcome emails
- **Authentication**: Secure user management system

### Deployment & Domain
- **Custom Domain**: www.zenflowit.com
- **Cloud Hosting**: AWS-based deployment
- **SSL Certificate**: Secure HTTPS connection

## 📁 Project Structure

```
zenflowit/
├── app.py                 # Main application entry point
├── models/                # Database models and features
├── static/                # Static assets (images, logos, etc.)
├── utils/                 # Utility functions
│   ├── ai.py              # AI integration with Gemini
│   ├── auth.py            # Authentication utilities
│   ├── db.py              # Database utilities
│   ├── email_service.py   # Email services
│   ├── theme.py           # Theme management
│   └── verify_env.py      # Environment verification
├── views/                 # UI view components
│   ├── assistant.py       # AI assistant interface
│   ├── auth.py            # Authentication views
│   ├── dashboard.py       # Main dashboard
│   ├── focus.py           # Focus tools and timer
│   ├── landing.py         # Landing page
│   ├── tasks.py           # Task management
│   ├── vision_board.py    # Vision board interface
│   └── rewards.py         # Rewards system
└── requirements.txt       # Python dependencies
```

## 🏗️ Development Journey

### Week 1: Market Research & Validation
- **Problem Identification**: Conducted market research analyzing 2,615+ Reddit posts about productivity struggles
- **Customer Survey**: Collected 57+ responses identifying key pain points
- **Competitor Analysis**: Analyzed existing solutions (Notion, Forest, Todoist, etc.)
- **Landing Page**: Created initial landing page using Gamma AI
- **Waitlist Building**: Gathered 54+ early sign-ups through targeted outreach

### Week 2: MVP Development
- **Solution Design**: Defined core features and user journey
- **UI/UX Design**: Created wireframes and user flow diagrams
- **Initial Development**: Built basic Streamlit application structure
- **Feature Planning**: Prioritized primary and secondary features
- **User Testing**: Conducted initial user experience testing

### Week 3-4: Production Development
- **Database Migration**: Transitioned from SQLite to PostgreSQL on AWS RDS
- **AI Integration**: Integrated Google Gemini AI for the ZenCoach assistant
- **Advanced Features**: Implemented vision board, focus tools, and reward system
- **Cloud Deployment**: Set up AWS infrastructure for scalable hosting
- **Domain Setup**: Acquired and configured custom domain www.zenflowit.com

### Production & Market Launch
- **Security Implementation**: Added SSL certificates and secure authentication
- **Performance Optimization**: Database optimization and caching strategies
- **Market Strategy**: Developed user acquisition and retention strategies
- **Analytics Setup**: Implemented user behavior tracking and app analytics
- **Continuous Improvement**: Ongoing bug fixes and feature enhancements

## 📊 Market Research Insights

Our comprehensive market analysis revealed:

### User Pain Points
- **Tool Fragmentation**: Users struggle with 3-4 different productivity apps
- **Emotional Barriers**: Anxiety and perfectionism prevent task initiation
- **Feature Overload**: Complex interfaces create additional stress
- **Lack of Personalization**: One-size-fits-all solutions don't work

### Competitive Advantages
- **Emotional Intelligence**: Addresses psychological aspects of productivity
- **AI-Powered Personalization**: Adapts to individual user patterns
- **Holistic Approach**: Combines task management, focus tools, and vision planning
- **Stress-Free Design**: Calm, intuitive interface promotes mental well-being

## 🚀 Installation & Setup

### Prerequisites
- Python 3.8+
- Virtual environment (recommended)
- PostgreSQL (for production) or SQLite (for development)

### Local Development
```bash
# Clone the repository
git clone https://github.com/your-username/zenflowit.git
cd zenflowit

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your API keys and database configuration

# Run the application
streamlit run app.py
```

### Environment Variables
Create a `.env` file with the following configuration:
```
GEMINI_API_KEY=your_gemini_api_key
DATABASE_URL=your_postgresql_connection_string
EMAIL_SERVICE_KEY=your_email_service_key
SECRET_KEY=your_secret_key
```

## 🎯 Key Metrics & Achievements

- **54+ Waitlist Sign-ups** during pre-launch phase
- **Comprehensive Market Research** analyzing 2,615+ social media posts
- **57+ Customer Survey Responses** validating problem-solution fit
- **Full-Stack Implementation** from SQLite to PostgreSQL on AWS
- **Custom Domain Deployment** with SSL security
- **AI-Powered Features** providing personalized productivity coaching

## 🔮 Future Enhancements

- **Mobile Application**: Native iOS and Android apps
- **Team Collaboration**: Multi-user workspaces and shared goals
- **Advanced Analytics**: Detailed productivity insights and reporting
- **Integration APIs**: Connect with popular tools like Google Calendar, Slack
- **Machine Learning**: Enhanced AI recommendations based on usage patterns
- **Gamification**: Expanded reward system and productivity challenges

## 🤝 Contributing

We welcome contributions! Please see our contributing guidelines for details on how to submit pull requests, report issues, and suggest improvements.


## 🌟 Acknowledgments

- **Google Gemini AI**: For powering our intelligent assistant
- **Streamlit Community**: For the excellent framework and support
- **AWS**: For reliable cloud infrastructure
- **Our Beta Users**: For valuable feedback and testing

---

**"ZenFlow helps you find focus, flow, and freedom — all in one beautifully crafted space."**

🌐 **Visit us at:** [www.zenflowit.com](http://www.zenflowit.com)
