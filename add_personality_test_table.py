"""
Add personality test results table to database
"""

import asyncpg
import asyncio

async def add_personality_test_table():
    """Add personality test results table"""
    try:
        conn = await asyncpg.connect(
            user='postgres',
            password='123',
            database='caelio_care',
            host='localhost',
            port=5432
        )
        
        # Create personality test results table
        await conn.execute('''
            CREATE TABLE IF NOT EXISTS personality_test_results (
                result_id SERIAL PRIMARY KEY,
                user_id INTEGER REFERENCES users(user_id),
                test_type VARCHAR(50) NOT NULL,  -- 'discovery' or 'professional'
                answers JSONB NOT NULL,
                primary_group VARCHAR(100) NOT NULL,
                secondary_group VARCHAR(100),
                primary_score INTEGER NOT NULL,
                secondary_score INTEGER,
                synthesizer_score INTEGER,
                is_synthesizer BOOLEAN DEFAULT FALSE,
                is_multi_motivated BOOLEAN DEFAULT FALSE,
                profile_name VARCHAR(200),
                english_name VARCHAR(200),
                all_scores JSONB,
                field VARCHAR(100),  -- For professional test
                motivation VARCHAR(100),  -- For professional test
                learning_style VARCHAR(100),  -- For professional test
                presentation_preference VARCHAR(100),  -- For professional test
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create index
        await conn.execute('''
            CREATE INDEX IF NOT EXISTS idx_personality_test_user_id 
            ON personality_test_results(user_id)
        ''')
        
        await conn.execute('''
            CREATE INDEX IF NOT EXISTS idx_personality_test_type 
            ON personality_test_results(test_type)
        ''')
        
        print("✅ Personality test results table created successfully")
        
        await conn.close()
        
    except Exception as e:
        print(f"❌ Error creating table: {e}")
        raise e

if __name__ == "__main__":
    asyncio.run(add_personality_test_table())
