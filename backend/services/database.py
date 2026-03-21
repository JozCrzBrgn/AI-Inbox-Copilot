import psycopg2

from ..core.config import get_settings

cnf = get_settings()

# PostgreSQL Configuration
DB_CONFIG = {
    'host': cnf.db.host,
    'port': cnf.db.port,
    'database': cnf.db.name,
    'user': cnf.db.user,
    'password': cnf.db.password
}

def get_connection():
    """Obtains a connection to PostgreSQL"""
    return psycopg2.connect(**DB_CONFIG)

def init_database():
    """Initialize the database by creating the table if it does not exist"""
    conn = get_connection()
    cur = conn.cursor()
    
    # Create email table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS emails (
            id SERIAL PRIMARY KEY,
            date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            customer_name VARCHAR(255),
            intent VARCHAR(255),
            priority VARCHAR(50),
            sentiment VARCHAR(50),
            summary TEXT,
            reply TEXT
        )
    """)
    
    conn.commit()
    cur.close()
    conn.close()

def save_email(customer_name: str, intent: str, priority: str, sentiment: str, summary: str, reply: str):
    """Save an analyzed email in the database"""
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("""
        INSERT INTO emails (customer_name, intent, priority, sentiment, summary, reply)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (customer_name, intent, priority, sentiment, summary, reply))
    
    conn.commit()
    cur.close()
    conn.close()

def get_all_emails():
    """It retrieves all emails from the history."""
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("""
        SELECT id, date, customer_name, intent, priority, sentiment, summary, reply
        FROM emails
        ORDER BY date DESC
    """)
    
    rows = cur.fetchall()
    
    emails = []
    for row in rows:
        emails.append({
            'id': row[0],
            'date': row[1].isoformat() if row[1] else None,
            'customer_name': row[2],
            'intent': row[3],
            'priority': row[4],
            'sentiment': row[5],
            'summary': row[6],
            'reply': row[7]
        })
    
    cur.close()
    conn.close()
    
    return emails

# Initialize the database when importing the module
try:
    init_database()
except Exception as e:
    # Keep the application running in test/local context without an active database.
    print(f"Warning: The database could not be initialized: {e}")
