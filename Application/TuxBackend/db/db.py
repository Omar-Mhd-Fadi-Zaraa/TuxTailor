import sqlite3
from typing import Any

from models.schemas import Role
from Agents.agents import ToolCallStatus


class Database:

    def __init__(self):
        self.conn = sqlite3.connect("TuxTailor.db", check_same_thread=False)
        self.cur = self.conn.cursor()
        self._createUsersTable()
        self._createChatsTable()
        self._createMessagesTable()
        self._createMessageCountIncrementTrigger()

    def close(self):
        self.conn.close()

    def _createChatsTable(self):
        query = """
        CREATE TABLE IF NOT EXISTS chats (
        chatId INTEGER PRIMARY KEY AUTOINCREMENT,
        userId INTEGER FORIEGN KEY REFERENCES usersr (userId),
        title TEXT NOT NULL,
        messageCount INTEGER,
        dateCreated DATE NOT NULL
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
        chatId INTEGER FORIEGN KEY REFERENCES chats (chatId) NOT NULL,
        userId INTEGER FORIEGN KEY REFERENCES users (userId) NOT NULL,
        content TEXT NOT NULL,
        role TEXT NOT NULL,
        toolCall BOOLEAN,
        toolCalls TEXT,
        toolCallStatus TEXT,
        preceedingMessage TEXT,
        dateSent DATE NOT NULL
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
        distroOfChoice TEXT,
        dateCreated DATE NOT NULL
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

    async def AddUser(
        self,
        level: str,
        dateCreated: str,
        systemPrompt: str | None = None,
        distroOfChoice: str | None = None,
    ) -> sqlite3.OperationalError | None:
        query = """
        INSERT INTO users(level,systemPrompt,distroOfChoice,dateCreated) VALUES (?,?,?,?)
        """
        try:
            self.cur.execute(query, (level, systemPrompt, distroOfChoice, dateCreated))
            self.conn.commit()
        except sqlite3.Error as e:
            raise sqlite3.OperationalError(f"Unable to add user: {e}")

    async def AddChat(
        self, userId: int, title: str, dateCreated: str
    ) -> sqlite3.OperationalError | None:
        query = """
        INSERT INTO chats(userId,title,messageCount,dateCreated) VALUES (?,?,?,?)
        """
        try:
            self.cur.execute(query, (userId, title, 1, dateCreated))
            self.conn.commit()
        except sqlite3.Error as e:
            raise sqlite3.OperationalError(f"Unable to add chat: {e}")

    async def AddMessage(
        self,
        chatId: int,
        userId: int,
        content: str,
        role: Role,
        dateSent: str,
        toolCall: bool | None = None,
        toolCalls: str | None = None,
        toolCallStatus: ToolCallStatus | None = None,
        preceedingMessage: str | None = None,
    ) -> sqlite3.OperationalError | None:
        query = """
        INSERT INTO messages (chatId, userId, content, role, toolCall, toolCalls, toolCallStatus, preceedingMessage, dateSent) 
        VALUES (?,?,?,?,?,?,?,?,?)
        """
        try:
            self.cur.execute(
                query,
                (chatId,
                userId,
                content,
                role,
                toolCall,
                toolCalls,
                toolCallStatus,
                preceedingMessage,
                dateSent,)
            )
            self.conn.commit()
        except sqlite3.Error as e:
            raise sqlite3.OperationalError(f"Unable to add message: {e}")

    async def GetChatMessages(self, chatId: int) -> list[Any]:
        query = """
        SELECT * FROM messages WHERE chatId = ?
        """
        try:
            self.cur.execute(query, (chatId,))
            messages = self.cur.fetchall()
        except sqlite3.Error as e:
            raise sqlite3.OperationalError(
                f"Unable to find messages for chatId {chatId}: {e}"
            )
        return messages

    async def GetUserSysPrompt(self, userId: int) -> str:
        query = """
        SELECT systemPrompt FROM users WHERE userId = ?
        """
        try:
            self.cur.execute(query, (userId,))
            prompt = self.cur.fetchone()
        except sqlite3.Error as e:
            raise sqlite3.OperationalError(
                f"Unable to find system prompt for user {userId}: {e}"
            )
        return str(prompt)
