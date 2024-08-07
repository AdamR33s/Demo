### AUTHOR: Adzz (A.K.A R4ptor or Tot4ll3d) ###
### EMAIL:
# Adzz.GSAU@Gmail.com - My Personal Email
# R4ptor@KYRGaming.com - My Gaming Server Queries Email
# Tot4ll3d@KYRGaming.com - My Community Queries Email
### CREATED: 07/08/2024 ### (COPY)
### VERSION: V2.0.0 ###
### SUMMARY: New Database Manager, fully Async using AIO MySQL and SQLAlchemy with full ORM features and Type Inference"

import sys
import aiomysql
import data.db_data as scars_data
import sqlalchemy as sa
import utils
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession  # New
from sqlalchemy.orm import (
    declarative_base,
    sessionmaker,
    Mapped,
    mapped_column,
    relationship,
    selectinload,
)  # New
from colorama import Fore, Back, Style
from datetime import datetime
from typing import Optional

################################################################################################
############################################# Async DB Connection ###############################
################################################################################################

db_url = "*****************************"
async_bot_engine = create_async_engine(db_url)

async_session = sessionmaker(
    bind=async_bot_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

Base = declarative_base()

################################################################################################
############################################## ORM API Pass Model #############################
################################################################################################


class DB_Passwd(Base):
    __tablename__ = "main_api_pass"
    passwd: Mapped[str] = mapped_column(sa.String(50), primary_key=True)

    @classmethod
    async def load(cls) -> "DB_Passwd":
        async with async_session() as session:
            statement = sa.select(cls)
            result = (await session.scalars(statement)).first()
            return result.passwd if result else None


################################################################################################
############################################## ORM Survivor Model #############################
################################################################################################


class _DB_Survivor(Base):
    __tablename__ = "survivors"
    discord_id: Mapped[int] = mapped_column(
        sa.BigInteger, primary_key=True, autoincrement=False
    )
    username: Mapped[str] = mapped_column(sa.String(50))
    display_name: Mapped[str] = mapped_column(sa.String(50), nullable=True)
    super_user: Mapped[bool] = mapped_column(sa.Boolean, default=False)
    pz: Mapped[bool] = mapped_column(sa.Boolean, default=False)
    tarkov: Mapped[bool] = mapped_column(sa.Boolean, default=False)
    factorio: Mapped[bool] = mapped_column(sa.Boolean, default=False)
    minecraft: Mapped[bool] = mapped_column(sa.Boolean, default=False)
    l4d2: Mapped[bool] = mapped_column(sa.Boolean, default=False)
    pz_userdata: Mapped[Optional["_DB_PZ_UserData"]] = relationship(
        "_DB_PZ_UserData",
        back_populates="survivor",
        uselist=False,
        cascade="all, delete-orphan",
        primaryjoin="_DB_PZ_UserData.discord_id == _DB_Survivor.discord_id",
    )
    tarkov_userdata: Mapped[Optional["_DB_Tarkov_UserData"]] = relationship(
        "_DB_Tarkov_UserData",
        back_populates="survivor",
        uselist=False,
        cascade="all, delete-orphan",
        primaryjoin="_DB_Tarkov_UserData.discord_id == _DB_Survivor.discord_id",
    )

    @classmethod
    async def _load(cls, discord_id: int) -> Optional["_DB_Survivor"]:
        async with async_session() as session:
            survivor = await session.get(
                cls,
                discord_id,
                options=[
                    selectinload(cls.pz_userdata).selectinload(
                        _DB_PZ_UserData.challenges
                    ),
                    selectinload(cls.pz_userdata).selectinload(
                        _DB_PZ_UserData.completed_challenges
                    ),
                    selectinload(cls.tarkov_userdata),
                ],
            )
            return survivor if survivor else None

    @classmethod
    async def _load_all(cls) -> Optional[list["_DB_Survivor"]]:
        async with async_session() as session:
            statement = sa.select(cls).options(
                selectinload(cls.pz_userdata).selectinload(_DB_PZ_UserData.challenges),
                selectinload(cls.pz_userdata).selectinload(
                    _DB_PZ_UserData.completed_challenges
                ),
                selectinload(cls.tarkov_userdata),
            )
            survivors = (await session.scalars(statement)).all()
            return survivors if survivors else None

    @classmethod
    async def _load_all_pz(cls) -> Optional[list["_DB_Survivor"]]:
        async with async_session() as session:
            statement = (
                sa.select(cls)
                .options(
                    selectinload(cls.pz_userdata).selectinload(
                        _DB_PZ_UserData.challenges
                    ),
                    selectinload(cls.pz_userdata).selectinload(
                        _DB_PZ_UserData.completed_challenges
                    ),
                    selectinload(cls.tarkov_userdata),
                )
                .filter_by(pz=True)
            )
            survivors = (await session.scalars(statement)).all()
            return survivors if survivors else None

    async def _save(self) -> None:
        async with async_session() as session:
            async with session.begin():
                session.add(self)
                await session.commit()

    async def _update(self) -> None:
        async with async_session() as session:
            async with session.begin():
                await session.merge(self)
                await session.commit()

    async def _delete(self) -> None:
        async with async_session() as session:
            async with session.begin():
                await session.delete(self)
                await session.commit()


################################################################################################
############################################## ORM LL_PZ_Data Model #############################
################################################################################################


class _DB_PZ_UserData(Base):
    __tablename__ = "ll_pz_userdata"
    discord_id: Mapped[int] = mapped_column(
        sa.BigInteger,
        sa.ForeignKey("survivors.discord_id"),
        primary_key=True,
        autoincrement=False,
    )
    current: Mapped[dict] = mapped_column(sa.JSON)
    short: Mapped[dict] = mapped_column(sa.JSON)
    long: Mapped[dict] = mapped_column(sa.JSON)
    survivor: Mapped[_DB_Survivor] = relationship(
        "_DB_Survivor", back_populates="pz_userdata"
    )
    challenges: Mapped[list["_DB_PZ_Challenge"]] = relationship(
        "_DB_PZ_Challenge", back_populates="pz_userdata"
    )
    completed_challenges: Mapped[list["_DB_PZ_Challenge"]] = relationship(
        "_DB_PZ_Challenge", back_populates="pz_userdata", overlaps="challenges"
    )

    async def _update(self):
        async with async_session() as session:
            async with session.begin():
                await session.merge(self)
                await session.commit()


################################################################################################
############################################## ORM LL_PZ_ChallengeData Model #############################
################################################################################################


class _DB_PZ_Challenge(Base):
    __tablename__ = "ll_pz_challenges"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    discord_id: Mapped[int] = mapped_column(
        sa.BigInteger, sa.ForeignKey("ll_pz_userdata.discord_id"), nullable=True
    )
    assigned: Mapped[datetime] = mapped_column(sa.DateTime, nullable=True)
    name: Mapped[str] = mapped_column(sa.String(50))
    description: Mapped[str] = mapped_column(sa.String(250))
    time_limit: Mapped[int] = mapped_column(sa.Integer)
    targets: Mapped[dict] = mapped_column(sa.JSON, nullable=True)
    targets_completed: Mapped[dict] = mapped_column(sa.JSON, nullable=True)
    reward: Mapped[int] = mapped_column(sa.Integer)
    warned: Mapped[bool] = mapped_column(sa.Boolean)
    data_snapshot: Mapped[dict] = mapped_column(sa.JSON, nullable=True)
    completed: Mapped[datetime] = mapped_column(sa.DateTime, nullable=True)
    pz_userdata: Mapped[int] = relationship(
        "_DB_PZ_UserData", back_populates="challenges"
    )

    @classmethod
    async def _load_available(cls):
        async with async_session() as session:
            statement = (
                sa.select(cls)
                .options(selectinload(cls.pz_userdata))
                .filter_by(assigned=None)
            )
            available_assignments = (await session.scalars(statement)).all()
            return available_assignments if available_assignments else None

    async def _save_new(self):
        async with async_session() as session:
            async with session.begin():
                session.add(self)
                await session.commit()

    async def _update(self):
        async with async_session() as session:
            async with session.begin():
                await session.merge(self)
                await session.commit()


################################################################################################
############################################## ORM LL_Tarkov_Data Model #############################
################################################################################################


class _DB_Tarkov_UserData(Base):
    __tablename__ = "ll_tarkov_userdata"
    discord_id: Mapped[int] = mapped_column(
        sa.BigInteger,
        sa.ForeignKey("survivors.discord_id"),
        primary_key=True,
        autoincrement=False,
    )
    joined: Mapped[datetime] = mapped_column(sa.DateTime)
    market_tracking: Mapped[dict] = mapped_column(sa.JSON)
    targets: Mapped[dict] = mapped_column(sa.JSON)
    ran_kits: Mapped[dict] = mapped_column(sa.JSON)
    assignments: Mapped[dict] = mapped_column(sa.JSON)
    updates: Mapped[dict] = mapped_column(sa.JSON)
    survivor: Mapped["_DB_Survivor"] = relationship(
        "_DB_Survivor", back_populates="tarkov_userdata"
    )


################################################################################################
############################################## ORM Control Model #############################
################################################################################################


class _DB_Control(Base):
    __tablename__ = "controls"
    name: Mapped[str] = mapped_column(
        sa.String(50), primary_key=True, autoincrement=False
    )
    type: Mapped[str] = mapped_column(sa.String(5))
    active: Mapped[bool] = mapped_column(sa.Boolean, nullable=True)
    timer: Mapped[datetime] = mapped_column(sa.DateTime, nullable=True)
    number: Mapped[int] = mapped_column(sa.Integer, nullable=True)
    text: Mapped[str] = mapped_column(sa.String(50), nullable=True)
    data: Mapped[dict] = mapped_column(sa.JSON, nullable=True)

    @classmethod
    async def _load_by_name(cls, name: str) -> Optional["_DB_Control"]:
        async with async_session() as session:
            control = await session.get(cls, name)
            return control if control else None

    async def _save(self) -> None:
        async with async_session() as session:
            async with session.begin():
                session.add(self)
                await session.commit()

    async def _update(self) -> None:
        async with async_session() as session:
            async with session.begin():
                await session.merge(self)
                await session.commit()


################################################################################################
############################################## ORM Server Model #############################
################################################################################################


class _DB_Server(Base):
    __tablename__ = "servers"
    id: Mapped[str] = mapped_column(
        sa.String(10), primary_key=True, autoincrement=False
    )
    game: Mapped[str] = mapped_column(sa.String(10))
    test_server: Mapped[bool] = mapped_column(sa.Boolean)
    iwbums_server: Mapped[bool] = mapped_column(sa.Boolean)
    name: Mapped[str] = mapped_column(sa.String(50))
    ip: Mapped[str] = mapped_column(sa.String(50))
    active: Mapped[bool] = mapped_column(sa.Boolean)
    wiped: Mapped[datetime] = mapped_column(sa.DateTime, nullable=True)
    apiport: Mapped[int] = mapped_column(sa.Integer)
    apipasswd: Mapped[str] = mapped_column(sa.String(50))

    @classmethod
    async def _load(cls, server_id) -> Optional["_DB_Server"]:
        async with async_session() as session:
            server = await session.get(cls, server_id)
            return server if server else None

    @classmethod
    async def _load_all_by_game(cls, game: str) -> Optional[list["_DB_Server"]]:
        async with async_session() as session:
            statement = sa.select(cls).filter_by(game=game)
            servers = (await session.scalars(statement)).all()
            return servers if servers else None

    async def _update(self) -> None:
        async with async_session() as session:
            async with session.begin():
                await session.merge(self)
                await session.commit()


################################################################################################
############################################## ORM LL_Message Model #############################
################################################################################################


class _DB_LL_Message(Base):
    __tablename__ = "ll_messages"
    id: Mapped[int] = mapped_column(sa.Integer, primary_key=True, autoincrement=True)
    type: Mapped[str] = mapped_column(sa.String(50))
    channel: Mapped[str] = mapped_column(sa.String(50))
    title: Mapped[str] = mapped_column(sa.String(50))
    body: Mapped[str] = mapped_column(sa.String(250))
    added: Mapped[datetime] = mapped_column(sa.DateTime)
    sent: Mapped[bool] = mapped_column(sa.Boolean)

    @classmethod
    async def _load_all(cls) -> Optional[list["_DB_LL_Message"]]:
        async with async_session() as session:
            statement = sa.select(cls)
            messages = (await session.scalars(statement)).all()
            return messages if messages else None

    @classmethod
    async def _load_all_unsent(cls) -> Optional[list["_DB_LL_Message"]]:
        async with async_session() as session:
            statement = sa.select(cls).filter_by(sent=False)
            messages = (await session.scalars(statement)).all()
            return messages if messages else None

    async def _save(self) -> None:
        async with async_session() as session:
            async with session.begin():
                session.add(self)
                await session.commit()

    async def _update(self) -> None:
        async with async_session() as session:
            async with session.begin():
                await session.merge(self)
                await session.commit()

    async def _delete(self) -> None:
        async with async_session() as session:
            async with session.begin():
                await session.delete(self)
                await session.commit()


################################################################################################
############################################## ORM LL_Template Model ###########################
################################################################################################


class _DB_LL_Template(Base):
    __tablename__ = "ll_templates"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    game: Mapped[str] = mapped_column(sa.String(50))
    event_type: Mapped[str] = mapped_column(sa.String(50))
    level: Mapped[str] = mapped_column(sa.Enum("New", "Bronze", "Silver", "Gold"))
    title: Mapped[str] = mapped_column(sa.String(50))
    body: Mapped[str] = mapped_column(sa.String(250))

    @classmethod
    async def _load_random(cls, game, event_type, level) -> Optional["_DB_LL_Template"]:
        async with async_session() as session:
            statement = (
                sa.select(cls)
                .filter_by(game=game, event_type=event_type, level=level)
                .order_by(sa.func.rand())
                .limit(1)
            )
            template = (await session.scalars(statement)).all()
            return template if template else None


################################################################################################
########################################### DB Setup #####################################
###############################################################################################
preset_tables = ["survivors_data", "controls_data", "servers_data", "ll_templates_data"]


async def build_tables():
    async with async_bot_engine.begin() as engine:
        await engine.run_sync(Base.metadata.create_all)


async def table_check(type):
    async with async_session() as session:
        statement = sa.select(type).limit(1)
        existing_data = (await session.scalars(statement)).all()
        if existing_data:
            return True
        return False


async def insert_preset_data():
    async with async_session() as session:
        async with session.begin():
            for table_name in preset_tables:
                try:
                    data_list = scars_data.new_table_data[f"{table_name}"]
                    for data in data_list:
                        instance = None
                        if table_name == "survivors_data":
                            instance = _DB_Survivor(**data)
                            existing_data = await table_check(_DB_Survivor)
                            if not existing_data:
                                session.add(instance)
                        elif table_name == "controls_data":
                            instance = _DB_Control(**data)
                            existing_data = await table_check(_DB_Control)
                            if not existing_data:
                                session.add(instance)
                        elif table_name == "servers_data":
                            instance = _DB_Server(**data)
                            existing_data = await table_check(_DB_Server)
                            if not existing_data:
                                session.add(instance)
                        elif table_name == "ll_templates_data":
                            instance = _DB_LL_Template(**data)
                            existing_data = await table_check(_DB_LL_Template)
                            if not existing_data:
                                session.add(instance)
                except sa.exc.OperationalError as e:
                    print(
                        f"<S.C.A.R.S> {Style.BRIGHT}{Fore.RED}{Back.BLACK}Database Data Error: {e}{Style.RESET_ALL}"
                    )
            await session.commit()
    print(
        f"<S.C.A.R.S> DATA CONSTRUCTION : {Style.BRIGHT}{Fore.GREEN}{Back.BLACK}[OK]{Style.RESET_ALL}"
    )
    print("---------------------------------------------------------------")


async def db_setup():
    print("---------------------------------------------------------------")
    print(
        f"<S.C.A.R.S> {Style.BRIGHT}{Fore.YELLOW}{Back.BLACK}Checking Database... {Style.RESET_ALL}"
    )
    try:
        await build_tables()
    except Exception as e:
        print(
            f"<S.C.A.R.S> {Style.BRIGHT}{Fore.RED}{Back.BLACK}Database Creation Error: {e}{Style.RESET_ALL}"
        )
        print("---------------------------------------------------------------")
        sys.exit(1)
    await insert_preset_data()
    print(
        f"<S.C.A.R.S> {Style.BRIGHT}{Fore.GREEN}{Back.BLACK}Database ::OK:: {Style.RESET_ALL}"
    )
    print("---------------------------------------------------------------")


################################################################################################
########################################### 3rd Party DB Connections ###########################
################################################################################################
class Database:
    def __init__(self, engine):
        self.conn = None
        try:
            self.engine = engine
            self.conn = self.engine.connect()
        except sa.exc.OperationalError as e:
            print(e)
            print("Error: Unable to connect to the database")

    def exe_Bool(self, query):
        try:
            with self.conn.begin() as t:
                result = self.conn.execute(query)
                first_row = result.fetchone()
                return bool(first_row) if first_row else False
        except sa.exc.OperationalError as e:
            self.conn.rollback()
            print(e)
            print("Error: Unable to execute query")

    def exe_Lite(self, query):
        try:
            with self.conn.begin() as t:
                result = self.conn.execute(query).fetchone()
                if result is None:
                    return None
                return result._asdict()
        except sa.exc.OperationalError as e:
            print(e)
            print("Error: Unable to execute query")

    def exe_Lite_multi(self, query):
        try:
            with self.conn.begin() as t:
                result = self.conn.execute(query).fetchall()
                if result is None:
                    return None
                return [rows._asdict() for rows in result]
        except sa.exc.OperationalError as e:
            print(e)
            print("Error: Unable to execute query")


################################################################################################
########################################### Sync DB Connections #####################################
################################################################################################
pzdb_engine = sa.create_engine("**********************")
lkdb_engine = sa.create_engine(
    "*********************************************",
    pool_size=5,
    max_overflow=2,
    pool_recycle=1800,
    execution_options={"autocommit": True},
)

################################################################################################
########################################### Sync DB Inspectors #####################################
################################################################################################
pzdb_inspec = sa.inspect(pzdb_engine)
lkdb_inspec = sa.inspect(lkdb_engine)

################################################################################################
########################################### Sync DB Instances #####################################
################################################################################################
pzdb = Database(pzdb_engine)
lkdb = Database(lkdb_engine)

################################################################################################
########################################### Sync PZ Tables #####################################
################################################################################################
pzmetadata = sa.MetaData()
pzmetadata.reflect(bind=pzdb_engine)
player = pzmetadata.tables["player"]
player_xp = pzmetadata.tables["player_xp"]


################################################################################################
########################################## LL PZ Functions #####################################
################################################################################################
def get_pz_char(server_id, username):
    result = pzdb.exe_Lite(
        sa.select(player.c.server_id, player.c.username).where(
            sa.and_(
                player.c.server_id == server_id,
                player.c.username == username,
                player.c.died_ingame.is_(None),
            )
        )
    )
    return result


def get_pz_charname(server_id, username):
    result = pzdb.exe_Lite(
        sa.select(player.c.fullname.label("charname"))
        .where(sa.and_(player.c.server_id == server_id, player.c.username == username))
        .order_by(player.c.player_id.desc())
        .limit(1)
    )
    return result


def check_pzchar_exists(server_id, username):
    result = pzdb.exe_Bool(
        sa.select(player.c.username).where(
            sa.and_(
                player.c.username == username,
                player.c.died_ingame.is_(None),
                player.c.server_id == server_id,
            )
        )
    )
    return result


def get_pz_kills(server_id, username):
    result = pzdb.exe_Lite(
        sa.select(player.c.vp.label("kills")).where(
            sa.and_(
                player.c.server_id == server_id,
                player.c.username == username,
                player.c.died_ingame.is_(None),
            )
        )
    )
    return result


def get_pz_total_kills(server_id, username):
    result = pzdb.exe_Lite(
        sa.select(sa.func.sum(player.c.vp).label("kills")).where(
            sa.and_(player.c.server_id == server_id, player.c.username == username)
        )
    )
    return result


def get_pz_skill(server_id, username, skill):
    result = pzdb.exe_Lite(
        sa.select(player_xp.c.current.label(skill))
        .select_from(
            player_xp.join(player, player_xp.c.player_id == player.c.player_id)
        )
        .where(
            sa.and_(
                player.c.server_id == server_id,
                player.c.username == username,
                player_xp.c.perk_name == skill,
                player.c.died_ingame.is_(None),
            )
        )
        .order_by(player_xp.c.perk_name.desc())
        .limit(1)
    )
    return result


def get_pz_deaths(server_id, username):
    result = pzdb.exe_Lite_multi(
        sa.select(player.c.died_ingame.label("deaths")).where(
            sa.and_(
                player.c.server_id == server_id,
                player.c.username == username,
                player.c.died_ingame.isnot(None),
            )
        )
    )
    return result


def get_pz_last_death(server_id, username):
    result = pzdb.exe_Lite(
        sa.select(player.c.died_ingame.label("last_death"))
        .where(player.c.server_id == server_id)
        .where(player.c.username == username)
        .where(player.c.died_ingame.isnot(None))
        .order_by(player.c.died_ingame.desc())
        .limit(1)
    )
    return result


def get_pz_last_death_rt(server_id, username):
    result = pzdb.exe_Lite(
        sa.select(player.c.died_time.label("last_death_rt"))
        .where(player.c.server_id == server_id)
        .where(player.c.username == username)
        .where(player.c.died_ingame.isnot(None))
        .order_by(player.c.died_ingame.desc())
        .limit(1)
    )
    return result
