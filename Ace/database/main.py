from typing import List

import aiosqlite

from ..utils import Account, Channels, GuildInfo, Info, Rank, WarnRecord, Record


class Base:
    conn: aiosqlite.Connection

    def __init__(self, table_query: str) -> None:
        self.table_query = table_query

    async def setup(self) -> None:
        self.conn = await aiosqlite.connect(Info.DB_FILE)
        cursor = await self.conn.cursor()
        await cursor.execute(self.table_query)
        await self.conn.commit()
        await cursor.close()

    @property
    def connection(self) -> aiosqlite.Connection | None:
        return self.conn
    
    @connection.setter
    def connection(self, conn: aiosqlite.Connection) -> None:
        self.conn = conn
    


class Economy(Base):
    def __init__(self) -> None:
        super().__init__("CREATE TABLE IF NOT EXISTS mainbank(user_id INTEGER, wallet INTEGER, bank INTEGER)")

    async def all_records(self) -> None | List[Account]:
        cursor = await self.conn.cursor()
        data = await (await cursor.execute("SELECT * FROM mainbank")).fetchall()
        await cursor.close()
        return None if not data else [Account(record[0], record[1], record[2]) for record in data]

    async def read(self, user_id: int) -> None | Account:
        cursor = await self.conn.cursor()
        data = await (await cursor.execute("SELECT * FROM mainbank WHERE user_id = ?", (user_id,))).fetchone()
        await cursor.close()
        return None if data is None else Account(data[0], data[1], data[2])

    async def create(self, user_id: int, wallet: int, bank: int) -> Account:
        if (check := await self.read(user_id)):
            return check
        cursor = await self.conn.cursor()
        await cursor.execute("INSERT INTO mainbank(user_id, wallet, bank) VALUES(?, ?, ?)", (user_id, wallet, bank,))
        await self.conn.commit()
        await cursor.close()
        return Account(user_id, wallet, bank)
    
    async def update(self, user_id: int, wallet: int = None, bank: int = None) -> bool:
        if not wallet and not bank:
            return False
        check = await self.read(user_id)
        if check is None:
            return False

        cursor = await self.conn.cursor()
        if wallet and not bank:
            await cursor.execute("UPDATE mainbank SET wallet = ? WHERE user_id = ?", (user_id,))
        elif bank and not wallet:
            await cursor.execute("UPDATE mainbank SET bank = ? WHERE user_id = ?", (bank, user_id,))
        elif bank and wallet:
            await cursor.execute("UPDATE mainbank SET wallet = ?, bank = ? WHERE user_id = ?", (wallet, bank, user_id,))
        await self.conn.commit()
        await cursor.close()
        return True

class GuildChannels(Base):
    
    def __init__(self) -> None:
        super().__init__("CREATE TABLE IF NOT EXISTS channels(guild_id INTEGER, welcome INTEGER, leave INTEGER, log INTEGER, vent INTEGER)")

    async def all_records(self) -> None | List[Channels]:
        cursor = await self.conn.cursor()
        data = await (await cursor.execute("SELECT * FROM channels")).fetchall()
        await cursor.close()
        return None if not data else [Channels(record[0], record[1], record[2], record[3], record[4]) for record in data]
    
    async def read(self, guild_id: int) -> None | Channels:
        cursor = await self.conn.cursor()
        record = await (await cursor.execute("SELECT * FROM channels WHERE guild_id = ?", (guild_id,))).fetchone()
        await cursor.close()
        return None if record is None else Channels(record[0], record[1], record[2], record[3], record[4])
    
    async def create(self, guild_id: int, welcome: int = 0, leave: int = 0, log: int = 0, vent: int = 0) -> Channels:
        if (check := await self.read(guild_id)):
            return check
        cursor = await self.conn.cursor()
        await cursor.execute("INSERT INTO channels(guild_id, welcome, leave, log, vent) VALUES(?, ?, ?, ?, ?)", (guild_id, welcome, leave, log, vent,))
        await self.conn.commit()
        await cursor.close()
        return Channels(guild_id, welcome, leave, log, vent)
    
    async def update(self, guild_id: int, welcome: int, leave: int, log: int, vent: int) -> bool:
        check = await self.read(guild_id)
        if check is None:
            return False
        
        cursor = await self.conn.cursor()

        await cursor.execute("UPDATE channels SET welcome = ? , leave = ? , log = ? , vent = ? WHERE guild_id = ?", (welcome, leave, log, vent, guild_id,))
        
        await self.conn.commit()
        await cursor.close()
        return True


class Experience(Base):
    conn: aiosqlite.Connection

    def __init__(self) -> None:
        super().__init__("CREATE TABLE IF NOT EXISTS exps(user_id INTEGER, guild_id INTEGER, xp INTEGER, level INTEGER)")

    async def all_records(self) -> None | List[Rank]:
        cursor = await self.conn.cursor()
        data = await (await cursor.execute("SELECT * FROM exps")).fetchall()
        await cursor.close()
        return None if not data else [Rank(record[0], record[1], record[2], record[3]) for record in data]
    
    async def all_guild_records(self, guild_id: int) -> None | List[Rank]:
        cursor = await self.conn.cursor()
        data = await (await cursor.execute("SELECT * FROM exps WHERE guild_id = ?", (guild_id,))).fetchall()
        await cursor.close()
        return None if not data else [Rank(record[0], record[1], record[2], record[3]) for record in data]
    
    async def _raw_guild_records(self, guild_id: int) -> None | List:
        cursor = await self.conn.cursor()
        data = await (await cursor.execute("SELECT * FROM exps WHERE guild_id = ?", (guild_id,))).fetchall()
        await cursor.close()
        return data

    async def read(self, user_id: int, guild_id: int) -> None | Rank:
        cursor = await self.conn.cursor()
        record = await (await cursor.execute('''SELECT * FROM exps WHERE user_id = ? AND guild_id = ?''', (user_id, guild_id,))).fetchone()
        await cursor.close()

        return None if record is None else Rank(record[0], record[1], record[2], record[3])

    async def create(self, user_id: int, guild_id: int, starting_xp: int=5, starting_level: int=1):
        if (check := await self.read(user_id, guild_id)):
            return check
        
        cursor = await self.conn.cursor()
        await cursor.execute('''INSERT INTO exps(user_id, guild_id, xp, level) VALUES(?, ?, ?, ?)''', (user_id, guild_id, starting_xp, starting_level,))
        await self.conn.commit()
        await cursor.close()
        return Rank(user_id, guild_id, starting_xp, starting_level)
        
    async def update(self, user_id: int, guild_id: int, *, xp: int=None, level: int=None) -> bool:
        if not xp and not level:
            return False
        
        check = await self.read(user_id, guild_id)
        if check is None:
            return False

        cursor = await self.conn.cursor()

        if xp and not level:
            await cursor.execute("UPDATE exps SET xp = ? WHERE user_id = ? AND guild_id = ?", (xp, user_id, guild_id,))
            
        if level and not xp:
            await cursor.execute("UPDATE exps SET level = ? WHERE user_id = ? AND guild_id = ?", (level, user_id, guild_id))
            
        if xp and level:
            await cursor.execute("UPDATE exps SET xp = ? , level = ? WHERE user_id = ? AND guild_id = ?",(xp,level,user_id, guild_id))
        
        await self.conn.commit()
        await cursor.close()
        return True

class Warns(Base):
    def __init__(self) -> None:
        super().__init__("CREATE TABLE IF NOT EXISTS warns(user_id INTEGER, guild_id INTEGER, warnings INTEGER)")
    
    async def all_records(self) -> None | List[WarnRecord]:
        cursor = await self.conn.cursor()
        records = await (await cursor.execute("SELECT * FROM warns")).fetchall()
        await cursor.close()
        return None if not records else [WarnRecord(record[0], record[1], record[2]) for record in records]

    async def read(self, user_id: int, guild_id: int) -> None | WarnRecord:
        cursor = await self.conn.cursor()
        record = await (await cursor.execute("SELECT * FROM warns WHERE user_id = ? AND guild_id = ?", (user_id, guild_id,))).fetchone()
        await cursor.close()
        
        return None if record is None else WarnRecord(record[0], record[1], record[2])
    
    async def create(self, user_id: int, guild_id: int, warns: int) -> WarnRecord:
        if (check := await self.read(user_id, guild_id)):
            return check

        cursor = await self.conn.cursor()
        await cursor.execute("INSERT INTO warns(user_id, guild_id, warnings) VALUES(?, ?, ?)", (user_id, guild_id, warns,))
        await self.conn.commit()
        await cursor.close()
        return WarnRecord(user_id, guild_id, warns)
    
    async def update(self, user_id: int, guild_id: int, warns: int) -> bool:
        check = await self.read(user_id, guild_id)
        if check is None:
            return False
        cursor = await self.conn.cursor()
        await cursor.execute("UPDATE warns SET warnings = ? WHERE user_id = ? AND guild_id = ? ", (warns, user_id, guild_id,))
        await self.conn.commit()
        await cursor.close()
        return True

class GuildInfo(Base):
    def __init__(self) -> None:
        super().__init__("CREATE TABLE IF NOT EXISTS info(guild_id INTEGER, kick_thresh INTEGER, ban_thresh INTEGER, on_join_role INTEGER)")
    
    async def all_records(self) -> None | List[GuildInfo]:
        cursor = await self.conn.cursor()
        records = await (await cursor.execute("SELECT * FROM info")).fetchall()
        await cursor.close()
        return None if records is None else [GuildInfo(record[0], record[1], record[2], record[3]) for record in records]

    async def read(self, guild_id: int) -> None | GuildInfo:
        cursor = await self.conn.cursor()
        record = await (await cursor.execute("SELECT * FROM info WHERE guild_id = ?", (guild_id,))).fetchone()
        await cursor.close()
        return None if record is None else GuildInfo(record[0], record[1], record[2], record[3])
    
    async def  create(self, guild_id: int, kick_thresh: int, ban_thresh: int, on_join_role: int) -> GuildInfo:
        if (check := await self.read(guild_id)):
            return check
        cursor = await self.conn.cursor()
        await cursor.execute("INSERT INTO info(guild_id, kick_thresh, ban_thresh, on_join_role) VALUES(?, ?, ?, ?)", (guild_id, kick_thresh, ban_thresh, on_join_role,))
        await self.conn.commit()
        await cursor.close()
        return GuildInfo(guild_id, kick_thresh, ban_thresh, on_join_role)
    
    async def update(self, guild_id: int, *, kick_thresh: int = None, ban_thresh: int = None, on_join_role: int = None) -> bool:
        check = await self.read(guild_id)
        if check is None:
            return False
        cursor = await self.conn.cursor()

        if kick_thresh is not None:
            await cursor.execute("UPDATE info SET kick_thresh = ? WHERE guild_id = ?", (kick_thresh, guild_id,))
            
        
        if ban_thresh is not None:
            await cursor.execute("UPDATE info SET ban_thresh = ? WHERE guild_id = ?", (ban_thresh, guild_id,))
        
        if on_join_role is not None:
            await cursor.execute("UPDATE info SET on_join_role = ? WHERE guild_id = ?", (on_join_role, guild_id,))
        
        await self.conn.commit()
        await cursor.close()
        return True

class MessageDB(Base):
    conn: aiosqlite.Connection

    def __init__(self) -> None:
        super().__init__("CREATE TABLE IF NOT EXISTS messages(user_id INTEGER, channel_id INTEGER, message_id INTEGER, guild_id INTEGER, dm_id INTEGER, dm_channel_id INTEGER)")


    async def read_user_message(self, user_id: int, message_id: int) -> None | Record:
        cursor = await self.conn.cursor()
        record = await (await cursor.execute("SELECT * FROM messages WHERE user_id = ? AND message_id = ?", (user_id, message_id,))).fetchone()
        if not record: return None
        return Record(record[2], record[0], record[3], record[1], record[4], record[5])

    async def read_message(self, message_id: int) -> None | List[Record]:
        cursor = await self.conn.cursor()
        records = await (await cursor.execute("SELECT * FROM messages WHERE message_id = ?", (message_id,))).fetchall()
        if not records: return None
        return [Record(record[2], record[0], record[3], record[1], record[4], record[5]) for record in records]

    async def read_user(self, user_id: int) -> None | List[Record]:
        cursor = await self.conn.cursor()
        record = await (await cursor.execute("SELECT * FROM messages WHERE user_id = ?", (user_id,))).fetchall()
        if not record: return None
        return [Record(record[2], record[0], record[3], record[1], record[4], record[5]) for record in record]

    async def create(self, user_id: int, channel_id: int, message_id: int, guild_id: int, dm_id: int, dm_channel_id: int) -> bool | Record:
        cursor = await self.conn.cursor()
        await cursor.execute("INSERT INTO messages(user_id, channel_id, message_id, guild_id, dm_id, dm_channel_id) VALUES(?, ?, ?, ?, ?, ?)", (user_id, channel_id, message_id, guild_id, dm_id, dm_channel_id,))
        await self.conn.commit()
        return Record(message_id, user_id, guild_id, channel_id, dm_id, dm_channel_id)
    
    async def remove(self, user_id: int, message_id: int) -> bool | Record:
        _check = await self.read_user_message(user_id, message_id)
        if _check is None:
            return False
        cursor = await self.conn.cursor()
        await cursor.execute("DELETE FROM messages WHERE user_id = ? AND message_id = ?", (_check.user_id, _check.message_id,))
        await self.conn.commit()
        return Record(_check.message_id, _check.user_id, _check.guild_id, _check.channel_id, _check.dm_id, _check.dm_channel_id)
    
    async def remove_user(self, user_id: int) -> bool:
        _check = await self.read_user(user_id)
        if _check is None:
            return False
        cursor = await self.conn.cursor()
        await cursor.execute("DELETE FROM messages WHERE user_id = ?", (user_id,))
        await self.conn.commit()
        return True
    
    async def remove_message(self, message_id: int) -> bool:
        _check = await self.read_message(message_id)
        if _check is None:
            return False
        cursor = await self.conn.cursor()
        await cursor.execute("DELETE FROM messages WHERE message_id = ?", (message_id,))
        await self.conn.commit()
        return True

class DatabaseManager:
    economy = Economy()
    channels = GuildChannels()
    info = GuildInfo()
    ranks = Experience()
    warns = Warns()
    messages = MessageDB()

    async def setup(self) -> None:
        await self.economy.setup()
        await self.channels.setup()
        await self.info.setup()
        await self.ranks.setup()
        await self.warns.setup()
        await self.messages.setup()