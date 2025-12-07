def load_css():
    return """
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');

        /* 
           ==========================================================================
           1. CSS VARIABLES (THEME TOKENS) - HIGH CONTRAST EDITION
           ==========================================================================
        */
        :root {
            /* LIGHT MODE */
            --bg-color: #f8fafc; /* Very light blue-grey */
            --card-bg: rgba(255, 255, 255, 0.90); /* High opacity for readability */
            --glass-border: rgba(0, 0, 0, 0.1);
            --text-color: #0f172a; /* Slate 900 - Near Black */
            --text-secondary: #334155; /* Slate 700 - Dark Grey */
            --accent-color: #2563eb;
            --shadow-sm: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
            --shadow-md: 0 10px 15px -3px rgba(0, 0, 0, 0.15);
            --gradient-start: #3b82f6;
            --gradient-end: #8b5cf6;
        }

        @media (prefers-color-scheme: dark) {
            :root {
                /* DARK MODE */
                --bg-color: #020617; /* Slate 950 - Very Dark */
                --card-bg: rgba(15, 23, 42, 0.85); /* Dark Slate with high opacity */
                --glass-border: rgba(255, 255, 255, 0.2);
                --text-color: #ffffff; /* Pure White */
                --text-secondary: #e2e8f0; /* Slate 200 - Very Light Grey */
                --accent-color: #818cf8;
                --shadow-sm: 0 4px 6px -1px rgba(0, 0, 0, 0.5);
                --shadow-md: 0 10px 15px -3px rgba(0, 0, 0, 0.7);
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
            color: var(--text-color) !important; /* Force override */
        }

        /* Force Streamlit's Main Container to match */
        .stApp {
            background-color: var(--bg-color);
            background-image: radial-gradient(circle at 10% 20%, rgba(37, 99, 235, 0.05) 0%, transparent 20%),
                              radial-gradient(circle at 90% 80%, rgba(139, 92, 246, 0.05) 0%, transparent 20%);
        }

        h1, h2, h3, h4, h5, h6 {
            color: var(--text-color) !important;
            font-weight: 700;
        }

        p, .stMarkdown, .caption, label, .stTextInput label, .stSelectbox label {
            color: var(--text-color) !important;
        }
        
        small, .small-text, [data-testid="stMetricLabel"] {
            color: var(--text-secondary) !important;
            opacity: 1 !important; /* Prevent Streamlit from dimming it */
        }

        /* 
           ==========================================================================
           3. COMPONENTS
           ==========================================================================
        */

        /* Cards (Glassmorphism) */
        .card, .auth-container, [data-testid="stForm"] {
            background-color: var(--card-bg);
            backdrop-filter: blur(16px);
            -webkit-backdrop-filter: blur(16px);
            border: 1px solid var(--glass-border);
            border-radius: 16px;
            padding: 24px;
            margin-bottom: 20px;
            box-shadow: var(--shadow-sm);
        }
        
        /* Inputs - High Contrast Borders */
        .stTextInput > div > div > input,
        .stSelectbox > div > div > div,
        .stTextArea > div > div > textarea,
        .stFileUploader {
            background-color: var(--bg-color) !important; /* Use solid bg for inputs */
            border: 2px solid var(--glass-border) !important;
            color: var(--text-color) !important;
            font-weight: 500;
        }
        
        /* Focused Input */
        .stTextInput > div > div > input:focus,
        .stTextArea > div > div > textarea:focus {
            border-color: var(--accent-color) !important;
            background-color: var(--card-bg) !important;
        }

        /* Buttons */
        .stButton > button {
            background: linear-gradient(135deg, var(--gradient-start), var(--gradient-end));
            color: #ffffff !important;
            font-weight: 700;
            border: none;
            box-shadow: 0 4px 6px rgba(0,0,0,0.2);
        }

        /* Metrics Values */
        [data-testid="stMetricValue"] {
            background: linear-gradient(135deg, var(--gradient-start), var(--gradient-end));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-weight: 800;
            filter: drop-shadow(0 2px 4px rgba(0,0,0,0.1));
        }
        
        /* DataFrame/Table Text */
        [data-testid="stDataFrame"] {
            color: var(--text-color) !important;
        }

        /* Mobile Adjustments */
        @media only screen and (max-width: 768px) {
            .card { padding: 16px; }
            h1 { font-size: 1.75rem !important; }
        }
    </style>
    """
