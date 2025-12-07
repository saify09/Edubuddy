def load_css():
    return """
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');

        /* 
           ==========================================================================
           1. CSS VARIABLES (THEME TOKENS)
           ==========================================================================
        */
        :root {
            /* LIGHT MODE (Glassy) */
            --bg-color: #f0f4f8;
            --card-bg: rgba(255, 255, 255, 0.65);
            --glass-border: rgba(255, 255, 255, 0.5);
            --text-color: #1e293b;
            --text-secondary: #475569;
            --accent-color: #2563eb;
            --shadow-sm: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
            --shadow-md: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
            --gradient-start: #3b82f6;
            --gradient-end: #8b5cf6;
        }

        @media (prefers-color-scheme: dark) {
            :root {
                /* DARK MODE (Glassy) */
                --bg-color: #0f172a;
                --card-bg: rgba(30, 41, 59, 0.7);
                --glass-border: rgba(255, 255, 255, 0.1);
                --text-color: #f1f5f9;
                --text-secondary: #cbd5e1; /* Lightened from #94a3b8 for better readability */
                --accent-color: #818cf8;
                --shadow-sm: 0 4px 6px -1px rgba(0, 0, 0, 0.3);
                --shadow-md: 0 10px 15px -3px rgba(0, 0, 0, 0.5);
                --gradient-start: #6366f1;
                --gradient-end: #d8b4fe;
            }
        }

        /* 
           ==========================================================================
           2. GLOBAL RESETS & TYPOGRAPHY
           ==========================================================================
        */
        html, body, [class*="css"] {
            font-family: 'Inter', sans-serif;
            color: var(--text-color);
        }

        /* Force Streamlit's Main Container to match */
        .stApp {
            background-color: var(--bg-color);
            background-image: radial-gradient(circle at 10% 20%, rgba(37, 99, 235, 0.1) 0%, transparent 20%),
                              radial-gradient(circle at 90% 80%, rgba(139, 92, 246, 0.1) 0%, transparent 20%);
        }

        h1, h2, h3, h4, h5, h6 {
            font-weight: 700;
            letter-spacing: -0.025em;
            color: var(--text-color);
        }

        /* Subtitles / Secondary Text */
        .stMarkdown p, .caption {
            color: var(--text-color); /* Improved readability */
        }
        
        small, .small-text {
            color: var(--text-secondary);
        }

        /* 
           ==========================================================================
           3. COMPONENTS
           ==========================================================================
        */

        /* Cards (Glassmorphism) */
        .card, .auth-container, [data-testid="stForm"] {
            background-color: var(--card-bg);
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
            border: 1px solid var(--glass-border);
            border-radius: 16px;
            padding: 24px;
            margin-bottom: 20px;
            box-shadow: var(--shadow-sm);
            transition: all 0.3s ease;
        }
        
        .card:hover, [data-testid="stForm"]:hover {
            box-shadow: var(--shadow-md);
            transform: translateY(-2px);
            border-color: var(--accent-color);
        }

        /* Sidebar */
        section[data-testid="stSidebar"] {
            background-color: var(--card-bg);
            backdrop-filter: blur(12px);
            border-right: 1px solid var(--glass-border);
        }
        
        section[data-testid="stSidebar"] .block-container {
            padding-top: 2rem;
        }

        /* Buttons */
        .stButton > button {
            background: linear-gradient(135deg, var(--gradient-start), var(--gradient-end));
            color: #ffffff !important;
            font-weight: 600;
            border: none;
            border-radius: 10px;
            padding: 0.6rem 1.2rem;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            transition: all 0.2s;
        }
        
        .stButton > button:hover {
            opacity: 0.95;
            transform: scale(1.02);
            box-shadow: 0 6px 10px rgba(0,0,0,0.15);
        }

        /* Inputs (Text, Select, File) */
        .stTextInput > div > div > input,
        .stSelectbox > div > div > div,
        .stTextArea > div > div > textarea,
        .stFileUploader {
            background-color: var(--card-bg);
            border: 1px solid var(--glass-border);
            border-radius: 10px;
            color: var(--text-color);
        }
        
        .stTextInput > div > div > input:focus,
        .stTextArea > div > div > textarea:focus {
            border-color: var(--accent-color);
            box-shadow: 0 0 0 2px rgba(37, 99, 235, 0.2);
        }

        /* Input Labels */
        .stTextInput label, .stSelectbox label, .stFileUploader label, .stTextArea label {
            font-weight: 600;
            font-size: 0.9rem;
            color: var(--text-color);
        }

        /* Metrics */
        [data-testid="stMetricValue"] {
            background: linear-gradient(135deg, var(--gradient-start), var(--gradient-end));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-size: 2.2rem;
            font-weight: 800;
        }
        
        [data-testid="stMetricLabel"] {
            color: var(--text-secondary) !important;
        }

        /* Tabs */
        .stTabs [data-baseweb="tab-list"] {
            gap: 8px;
            background-color: transparent;
            border-bottom: 1px solid var(--glass-border);
        }

        .stTabs [data-baseweb="tab"] {
            height: 40px;
            background-color: transparent;
            border-radius: 8px;
            color: var(--text-secondary);
            font-weight: 600;
            border: none;
        }

        .stTabs [aria-selected="true"] {
            background-color: rgba(255,255,255,0.1);
            color: var(--accent-color) !important;
            box-shadow: inset 0 0 0 1px var(--glass-border);
        }

        /* 
           ==========================================================================
           4. UTILITIES
           ==========================================================================
        */
        /* Gradient Text for Title */
        h1 {
            background: linear-gradient(135deg, var(--gradient-start), var(--gradient-end));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 1rem;
        }
        
        /* Mobile Adjustments */
        @media only screen and (max-width: 768px) {
            .card { padding: 16px; }
            h1 { font-size: 1.75rem !important; }
        }
    </style>
    """
