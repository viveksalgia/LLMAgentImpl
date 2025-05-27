import sqlite3
import uuid


def gen_session_id():
    return uuid.uuid4()


def get_session_id(db_name: str, user: str) -> str:
    conn = sqlite3.connect(db_name)

    cursor = conn.cursor()

    cursor.execute(
        "select * from agent_sessions where user_id = ? order by date(created_at) desc limit 1",
        (user,),
    )

    rows = cursor.fetchall()

    for row in rows:
        print(f"Session id - {row[0]}")
        print(f"Agent id - {row[1]}")
        print(f"User id - {row[2]}")
        print(f"Memory - {row[3]}")
        print(f"Agent data - {row[4]}")
        print(f"Session data - {row[4]}")

    return "Success"


if __name__ == "__main__":
    print(f"Session Id generated - {gen_session_id()}")
    get_session_id("../storage/knowledge_agent_storage.db", "vivek.salgia_15d5")
