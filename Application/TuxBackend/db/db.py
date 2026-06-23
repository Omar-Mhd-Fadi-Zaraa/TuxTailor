import sqlite3

from models.schemas import Role


class Database:

    def __init__(self):
        self.conn = sqlite3.connect("TuxTailor.db")
        self.cur = self.conn.cursor()
        self._createUsersTable()
        self._createChatsTable()
        self._createMessagesTable()
        self._createMessageCountIncrementTrigger()

    def _createChatsTable(self):
        query = """
        CREATE TABLE IF NOT EXISTS chats (
        chatId INTEGER PRIMARY KEY AUTOINCREMENT,
        userId INTEGER FORIEGN KEY,
        title TEXT NOT NULL,
        messageCount INTEGER
        )
        """
        try:
            self.cur.execute(query)
            self.conn.commit()
        except sqlite3.Error as e:
            raise sqlite3.OperationalError(f"Unable to create Chats table: {e}")

    def _createMessagesTable(self):
        query = """
        CREATE TABLE IF NOT EXISTS messages (
        messageId INTEGER PRIMARY KEY AUTOINCREMENT,
        chatId INTEGER FORIEGN KEY,
        userId INTEGER FORIEGN KEY,
        content TEXT NOT NULL,
        role TEXT NOT NULL,
        toolCall BOLEAN NOT NULL,
        toolId INTEGER,
        toolName TEXT
        )
        """
        try:
            self.cur.execute(query)
            self.conn.commit()
        except sqlite3.Error as e:
            raise sqlite3.OperationalError(f"Unable to create messages table: {e}")

    def _createUsersTable(self):
        query = """
        CREATE TABLE IF NOT EXISTS users (
        userId INTEGER PRIMARY KEY AUTOINCREMENT,
        level TEXT NOT NULL,
        systemPrompt TEXT,
        distroOfChoice TEXT
        )
        """
        try:
            self.cur.execute(query)
            self.conn.commit()
        except sqlite3.Error as e:
            raise sqlite3.OperationalError(f"Unable to create users table: {e}")

    def _createMessageCountIncrementTrigger(self):
        query = """
        CREATE TRIGGER IF NOT EXISTS increment_message_count
        AFTER INSERT ON messages
        BEGIN
            UPDATE chats SET messageCount = messageCount + 1 WHERE chatId = NEW.chatId;
        END;
        """
        try:
            self.cur.execute(query)
            self.conn.commit()
        except sqlite3.Error as e:
            raise sqlite3.OperationalError(
                f"Unable to create incement_message_count trigger: {e}"
            )

    def AddUser(
        self,
        level: str,
        systemPrompt: str | None = None,
        distroOfChoice: str | None = None,
    ):
        query = """
        INSERT INTO users(level,systemPrompt,distroOfChoice) VALUES (?,?,?)
        """
        try:
            self.cur.execute(query, level, systemPrompt, distroOfChoice)
            self.conn.commit()
        except sqlite3.Error as e:
            raise sqlite3.OperationalError(f"Unable to add user: {e}")

    def AddChat(self, userId: int, title: str):
        query = """
        INSERT INTO chats(userId,title,messageCount) VALUES (?,?,?)
        """
        try:
            self.cur.execute(query, userId, title, 1)
            self.conn.commit()
        except sqlite3.Error as e:
            raise sqlite3.OperationalError(f"Unable to add chat: {e}")

    def AddMessage(
        self,
        chatId: int,
        userId: int,
        content: str,
        role: Role,
        toolCall: bool,
        toolId: int | None = None,
        toolName: str | None = None,
    ):
        query = """
        INSERT INTO messages (chatId, userId, content, role, toolCall, toolId, toolName) VALUES (?,?,?,?,?,?,?)
        """
        try:
            self.cur.execute(
                query, chatId, userId, content, role, toolCall, toolId, toolName
            )
            self.conn.commit()
        except sqlite3.Error as e:
            raise sqlite3.OperationalError(f"Unable to add message: {e}")

    def GetChatMessages(self, chatId: int):
        query = """
        SELECT * FROM messages WHERE chatId = ?
        """
        try:
            self.cur.execute(query, chatId)
            self.conn.commit()
        except sqlite3.Error as e:
            raise sqlite3.OperationalError(
                f"Unable to find messages for chatId {chatId}: {e}"
            )
