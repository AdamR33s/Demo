### AUTHOR: Adzz (A.K.A R4ptor or Tot4ll3d) ###
### EMAIL: 
# Adzz.GSAU@Gmail.com - My Personal Email
# R4ptor@KYRGaming.com - My Gaming Server Queries Email
# Tot4ll3d@KYRGaming.com - My Community Queries Email
### CREATED: 07/08/2024 ### (COPY)
### VERSION: v1.0.0 ###
### SUMMARY: Old Database Module using Sync Blocking Calls, PyMySQL and some elements of SQL Alchemy ###

import sys
import pymysql
import traceback
import sqlalchemy as sa
import data.sql as sql
from sqlalchemy import select, and_, update, insert
from data.sql import(
                botdb_metadata, 
                survivors_tbl, 
                channels_tbl, 
                responses_tbl, 
                controls_tbl,
                servers_tbl, 
                ll_templates_tbl,
                ll_messages_tbl,   
                ll_pz_sdrop_tbl,
                ll_pz_sdrop_orders_tbl, 
                ll_pz_challenges_tbl, 
                ll_pz_data_tbl, 
                ll_pz_data_longcopy_tbl,
                ll_pz_data_shortcopy_tbl,
                ll_pz_data_challengecopy_tbl, 
                main_api_tbl, 
                mini_api_tbl
                )
from colorama import Fore, Back, Style
import logs

################################################################################################
############################################# Table Defs #######################################
################################################################################################
survivors_tbl = botdb_metadata.tables['survivors']
channels_tbl = botdb_metadata.tables['channels']
responses_tbl = botdb_metadata.tables['responses']
controls_tbl = botdb_metadata.tables['controls']
servers_tbl = botdb_metadata.tables['servers']
ll_templates_tbl = botdb_metadata.tables['ll_templates']
ll_messages_tbl = botdb_metadata.tables['ll_messages']
ll_pz_sdrop_tbl = botdb_metadata.tables['ll_pz_sdrop']
ll_pz_sdrop_orders_tbl = botdb_metadata.tables['ll_pz_sdrop_orders']
ll_pz_challenges_tbl = botdb_metadata.tables['ll_pz_challenges']
ll_pz_data_tbl = botdb_metadata.tables['ll_pz_data']
ll_pz_data_longcopy_tbl = botdb_metadata.tables['ll_pz_data_longcopy']
ll_pz_data_shortcopy_tbl = botdb_metadata.tables['ll_pz_data_shortcopy']
ll_pz_data_challengecopy_tbl = botdb_metadata.tables['ll_pz_data_challengecopy']
main_api_tbl = botdb_metadata.tables['main_api_pass']
mini_api_tbl = botdb_metadata.tables['mini_api_pass']

################################################################################################
########################################### DB Class & Methods #####################################
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

    def exe(self, query):
        try:
            with self.conn.begin() as t:
                result = self.conn.execute(query)
                assert result.rowcount <= 1, f"{Style.BRIGHT}{Fore.RED}{Back.BLACK}<S.C.A.R.S> ERROR{Style.RESET_ALL} : Multiple rows returned for single row query"
                return result.fetchone()._asdict() if result.rowcount else None
        except sa.exc.OperationalError as e:
            self.conn.rollback()
            print(e)
            print("Error: Unable to execute query")

    def exe_Multi(self, query):
        try:
            with self.conn.begin() as t:
                result = self.conn.execute(query)
                if result is not None and result.rowcount >= 1:
                    return [rows._asdict() for rows in result.fetchall()]
                return None
        except sa.exc.OperationalError as e:
            self.conn.rollback()
            print(e)
            print("Error: Unable to execute query")

    def exe_Commit(self, query):
        try:
            with self.conn.begin() as t:
                result = self.conn.execute(query)
                return result if result else None
        except sa.exc.OperationalError as e:
            self.conn.rollback()
            print(e)
            print("Error: Unable to execute query")

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
########################################### DB Connections #####################################
################################################################################################
bot_engine = sa.create_engine('***************************', pool_size=2, max_overflow=2, pool_recycle=3600, execution_options={"autocommit": True})
pzdb_engine = sa.create_engine('***************************')
lkdb_engine = sa.create_engine(
    "***************************",
    pool_size=2,
    max_overflow=2,
    pool_recycle=3600,
    execution_options={"autocommit": True},
)

################################################################################################
########################################### DB Inspectors #####################################
################################################################################################
bot_inspec = sa.inspect(bot_engine)
pzdb_inspec = sa.inspect(pzdb_engine)
lkdb_inspec = sa.inspect(lkdb_engine)

################################################################################################
########################################### DB Instances #####################################
################################################################################################
botdb = Database(bot_engine)
pzdb = Database(pzdb_engine)
lkdb = Database(lkdb_engine)

################################################################################################
########################################### PZ Tables #####################################
################################################################################################
pzmetadata = sa.MetaData()
pzmetadata.reflect(bind=pzdb_engine)
player = pzmetadata.tables['player']
player_xp = pzmetadata.tables['player_xp']

################################################################################################
########################################### DB Setup #####################################
################################################################################################
tables = [
    "survivors", 
    "channels", 
    "responses", 
    "controls",
    "servers", 
    "ll_templates",
    "ll_messages",
    "ll_pz_sdrop",
    "ll_pz_sdrop_orders", 
    "ll_pz_challenges",   
    "ll_pz_data", 
    "ll_pz_data_longcopy",
    "ll_pz_data_shortcopy", 
    "ll_pz_data_challengecopy",
    "main_api_pass", 
    "mini_api_pass"
    ]
data_inserts = sql.new_table_data.keys()

def check_Sdb_tables():
    for table_name in tables:
        if bot_inspec.has_table(table_name):
            print("---------------------------------------------------------------")
            print(f"<S.C.A.R.S> {Style.BRIGHT}{Fore.YELLOW}{Back.BLACK}CHECKING{Style.RESET_ALL} : SDB Table - {table_name}... {Style.BRIGHT}{Fore.GREEN}{Back.BLACK}[OK]{Style.RESET_ALL}")
        else:
            print("---------------------------------------------------------------")
            print(f"<S.C.A.R.S> {Style.BRIGHT}{Fore.YELLOW}{Back.BLACK}CHECKING{Style.RESET_ALL} : SDB Table - {table_name}... {Style.BRIGHT}{Fore.YELLOW}{Back.BLACK}[NOT FOUND]{Style.RESET_ALL}")
            print(f"<S.C.A.R.S> {Style.BRIGHT}{Fore.YELLOW}{Back.BLACK}CONSTRUCTING{Style.RESET_ALL} :  SDB Table {table_name}...")
            table = botdb_metadata.tables[table_name]
            table.create(botdb.engine)
            print(f"<S.C.A.R.S> TABLE CONSTRUCTION : {Style.BRIGHT}{Fore.GREEN}{Back.BLACK}[OK]{Style.RESET_ALL}")
            insert_Table_data(table_name, table)
botdb.conn.commit()

def insert_Table_data(table_name, table):
    if f"{table_name}_data" in data_inserts:
        print(f"<S.C.A.R.S> {Style.BRIGHT}{Fore.YELLOW}{Back.BLACK}CONSTRUCTING{Style.RESET_ALL} : SDB {table_name} Data...")
        data_list = sql.new_table_data[f"{table_name}_data"]
        for data in data_list:
            try:
                botdb.exe_Commit(table.insert().values(**data))
            except sa.exc.OperationalError as e:
                print("Error Inserting Data")
                print(e)
        print(f"<S.C.A.R.S> DATA CONSTRUCTION : {Style.BRIGHT}{Fore.GREEN}{Back.BLACK}[OK]{Style.RESET_ALL}")
    else:
        print("---------------------------------------------------------------")

################################################################################################
######################################## Active Channels List ##################################
################################################################################################
active_channels = {}
def get_Channels_list(client):
    print(f"<S.C.A.R.S> {Style.BRIGHT}{Fore.YELLOW}{Back.BLACK}CHECKING{Style.RESET_ALL} : Active Channel List...")
    for i in range (2):
        for channel in getall_Channels():
            try:
                channel_obj = client.get_channel(channel['id'])
                if channel_obj:
                    active_channels[channel_obj.name] = channel_obj
                else:
                    print(f"<S.C.A.R.S> Channel {channel['name']} {Style.BRIGHT}{Fore.YELLOW}{Back.BLACK}[INACTIVE]{Style.RESET_ALL}")
            except Exception as err:
                traceback.print_exc()
                logs.log_Event(f"Error in Active Channel List - OBJECT ERROR: ", err)
                logs.log_Event(f"Error in Active Channel List - STACKTRACE: ", traceback.format_exc())
                sys.exit("ACTIVE CHANNEL LIST ERROR - TERMINATING BOT")
        return active_channels

################################################################################################
################################################ Channel Functions ##########################################
################################################################################################
def get_Channel_byname(name: str):
    result = botdb.exe(select(channels_tbl.c.id, channels_tbl.c.name, channels_tbl.c.type).where(channels_tbl.c.name == name))
    return result

def get_Channel_by_id(id: int):
    result = botdb.exe(select(channels_tbl.c.id, channels_tbl.c.name, channels_tbl.c.type).where(channels_tbl.c.id == id))
    return result

def getall_Channels():
    result = botdb.exe_Multi(channels_tbl.select())
    return result

def update_Channel(channel):
    botdb.exe_Commit(channels_tbl.update().where(channels_tbl.c.id == channel.id).values(id=channel.id, name=channel.name, type=channel.type))

def save_Channel(channel):
    botdb.exe_Commit(channels_tbl.insert().values(id=channel.id, name=channel.name, type=channel.type))

def remove_Channel_by_id(id: int):
    botdb.exe_Commit(channels_tbl.delete().where(channels_tbl.c.id == id))

################################################################################################
########################################### Admin Functions #####################################
################################################################################################
def check_Superuser_by_did(discord_id: int):
    result = botdb.exe_Bool(select(survivors_tbl.c.username).where(survivors_tbl.c.discord_id == discord_id).where(survivors_tbl.c.super_user.isnot(None)))
    return result

def getall_Superusers():
    result = botdb.exe_Multi(survivors_tbl.select().where(survivors_tbl.c.super_user.isnot(None)))
    return result

################################################################################################
########################################### Surv Functions #####################################
################################################################################################
def get_Surv_by_did(discord_id: int):
    result = botdb.exe(
        select(
            survivors_tbl.c.discord_id, 
            survivors_tbl.c.username, 
            survivors_tbl.c.display_name, 
            survivors_tbl.c.pz, 
            survivors_tbl.c.l4d2, 
            survivors_tbl.c.super_user
        )
        .where(survivors_tbl.c.discord_id == discord_id))
    return result

def get_All_survs():
    result = botdb.exe_Multi(
        select(
            survivors_tbl.c.discord_id, 
            survivors_tbl.c.username, 
            survivors_tbl.c.display_name, 
            survivors_tbl.c.pz, 
            survivors_tbl.c.l4d2, 
            survivors_tbl.c.super_user
            )
        )
    return result

def save_Surv(survivor):
    botdb.exe_Commit(
        survivors_tbl.insert().values(
            discord_id=survivor.discord_id, 
            username=survivor.username, 
            display_name=survivor.display_name, 
            pz=survivor.pz, 
            l4d2=survivor.l4d2, 
            super_user=survivor.super_user
        )
    )

def update_Surv(survivor):
    botdb.exe_Commit(
        survivors_tbl.update().where(
            survivors_tbl.c.discord_id == survivor.discord_id
        ).values(
            username=survivor.username, 
            display_name=survivor.display_name, 
            pz=survivor.pz, 
            l4d2=survivor.l4d2, 
            super_user=survivor.super_user
        )
    )

def remove_Surv_by_did(discord_id: int):
    botdb.exe_Commit(survivors_tbl.delete().where(survivors_tbl.c.discord_id == discord_id))

################################################################################################
########################################## Response Functions ###################################
################################################################################################
def get_Response_by_title(title: str):
    result = botdb.exe(select(responses_tbl.c.title. responses_tbl.c.section, responses_tbl.c.body).where(responses_tbl.c.title == title))
    return result

def get_Random_response_by_sec(section: str):
    result = botdb.exe(select(responses_tbl.c.title, responses_tbl.c.section, responses_tbl.c.body).where(responses_tbl.c.section == section).order_by(sa.func.rand()).limit(1))
    return result

def get_All_responses():
    result = botdb.exe_Multi(responses_tbl.select())
    return result

################################################################################################
########################################## SYS Control Functions ###################################
################################################################################################
def get_SYS_controls_by_name(name: str):
    result = botdb.exe(select(
        controls_tbl.c.name, 
        controls_tbl.c.bool, 
        controls_tbl.c.dt, 
        controls_tbl.c.int, 
        controls_tbl.c.str,
        controls_tbl.c.json)
        .where(and_(controls_tbl.c.type == "sys", controls_tbl.c.name == name)))
    return result

def update_SYS_controls(controls):
    botdb.exe_Commit(controls_tbl.update().where(
        controls_tbl.c.name == controls.name)
        .values(
            bool=controls.bool, 
            dt=controls.dt, 
            int=controls.int, 
            str=controls.str,
            json=controls.json
            )
        )

################################################################################################
########################################## Server Functions ###################################
################################################################################################
def get_All_pz_servers():
    result = botdb.exe_Multi(select(servers_tbl.c.id, servers_tbl.c.game, servers_tbl.c.iwbums_server, servers_tbl.c.test_server, servers_tbl.c.name, servers_tbl.c.ip, servers_tbl.c.port, servers_tbl.c.active, servers_tbl.c.wiped, servers_tbl.c.passwd, servers_tbl.c.adminpw, servers_tbl.c.apiport, servers_tbl.c.apipasswd))
    return result

def update_pz_server(server):
    botdb.exe_Commit(servers_tbl.update().where(servers_tbl.c.id == server.id).values(
        game=server.game, 
        iwbums_server=server.iwbums_server, 
        test_server=server.test_server, 
        name=server.name, 
        ip=server.ip, 
        port=server.port, 
        active=server.active, 
        wiped=server.wiped, 
        passwd=server.passwd, 
        adminpw=server.adminpw, 
        apiport=server.apiport, 
        apipasswd=server.apipasswd
        ))

################################################################################################
########################################### API's #####################################
################################################################################################
def save_Api_pass(password: str) -> None:
    botdb.exe_Commit(main_api_tbl.insert().values(password=password))
    botdb.exe_Commit(mini_api_tbl.insert().values(password=password))

def get_Main_api_pass() -> str:
    result = botdb.exe(select(main_api_tbl.c.password))
    return result

def get_Mini_api_pass() -> str:
    result = botdb.exe(select(mini_api_tbl.c.password))
    return result

# password = "requesttokyrapi"
# if __name__ == "__main__":
#    store_API_password(password)

################################################################################################
######################################### Live Link Functions ##################################
################################################################################################

################################################################################################
######################################### LL Control Functions #################################
################################################################################################
def get_LL_controls_by_name(name):
    result = botdb.exe(select(
        controls_tbl.c.name, 
        controls_tbl.c.bool, 
        controls_tbl.c.dt, 
        controls_tbl.c.int, 
        controls_tbl.c.str, 
        controls_tbl.c.json)
        .where(and_(controls_tbl.c.type == "ll", controls_tbl.c.name == name)))
    return result

def update_LL_controls(controls):
    botdb.exe_Commit(controls_tbl.update().where(
        controls_tbl.c.name == controls.name)
        .values(
            bool=controls.bool, 
            dt=controls.dt, 
            int=controls.int, 
            str=controls.str, 
            json=controls.json
            )
        )

################################################################################################
########################################## LL Event Functions ##################################
################################################################################################

def get_LL_template(game:str, event_type: str, level: str):
    result = botdb.exe(select(ll_templates_tbl.c.title, ll_templates_tbl.c.body).where(and_(ll_templates_tbl.c.game == game, ll_templates_tbl.c.event_type == event_type, ll_templates_tbl.c.level == level)).order_by(sa.func.rand()).limit(1))
    return result

################################################################################################
######################################## LL Message Functions ##################################
################################################################################################
def save_LL_message(ll_message):
    botdb.exe_Commit(
                ll_messages_tbl.insert()
                    .values(
                        type=ll_message.type, 
                        channel=ll_message.channel,
                        title=ll_message.title, 
                        body=ll_message.body, 
                        added=ll_message.added, 
                        sent=ll_message.sent
                    ))

def get_All_ll_messages():
    result = botdb.exe_Multi(select(
                                ll_messages_tbl.c.id,
                                ll_messages_tbl.c.type,
                                ll_messages_tbl.c.channel,
                                ll_messages_tbl.c.title,
                                ll_messages_tbl.c.body, 
                                ll_messages_tbl.c.added, 
                                ll_messages_tbl.c.sent
                            ))
    return result

def get_All_unsent_ll_messages():
    result = botdb.exe_Multi(select(
                                ll_messages_tbl.c.id,
                                ll_messages_tbl.c.type,
                                ll_messages_tbl.c.channel,
                                ll_messages_tbl.c.title,
                                ll_messages_tbl.c.body, 
                                ll_messages_tbl.c.added, 
                                ll_messages_tbl.c.sent
                            ).where(ll_messages_tbl.c.sent == False)
                        )
    return result

def update_LL_message(ll_message):
    botdb.exe_Commit(ll_messages_tbl.update()
                                        .where(ll_messages_tbl.c.id == ll_message.id)
                                        .values(
                                            type=ll_message.type, 
                                            channel=ll_message.channel,
                                            title=ll_message.title,
                                            body=ll_message.body, 
                                            added=ll_message.added, 
                                            sent=ll_message.sent
                                        ))

def delete_LL_message(ll_message):
    botdb.exe_Commit(ll_messages_tbl.delete().where(ll_messages_tbl.c.id == ll_message.id))

################################################################################################
########################################## LL PZ Functions #####################################
################################################################################################
def get_Pzchar(server_id, username):
    result = pzdb.exe_Lite(select(player.c.server_id, player.c.username).where(and_(player.c.server_id == server_id, player.c.username == username, player.c.died_ingame.is_(None))))
    return result

def get_Pzcharname(server_id, username):
    result = pzdb.exe_Lite(select(player.c.fullname.label('charname')).where(and_(player.c.server_id == server_id, player.c.username == username)).order_by(player.c.player_id.desc()).limit(1))
    return result

def check_Pzchar_exists(server_id, username):
    result = pzdb.exe_Bool(select(player.c.username).where(and_(player.c.username == username, player.c.died_ingame.is_(None), player.c.server_id == server_id)))
    return result

def save_LL_pz_data(ll_pz_data_copy, table):
    if table == "current":
        table = ll_pz_data_tbl
    elif table == "longcopy":
        table = ll_pz_data_longcopy_tbl
    elif table == "shortcopy":
        table = ll_pz_data_shortcopy_tbl
    botdb.exe_Commit(
        insert(table)
        .values(
            discord_id=ll_pz_data_copy.discord_id,
            server_id=ll_pz_data_copy.server_id,
            server_num=ll_pz_data_copy.server_num,
            server_name=ll_pz_data_copy.server_name,
            server_wipe=ll_pz_data_copy.server_wipe,
            username=ll_pz_data_copy.username,
            charname=ll_pz_data_copy.charname,
            alive=ll_pz_data_copy.alive,
            kills=ll_pz_data_copy.kills,
            total_kills=ll_pz_data_copy.total_kills,
            skills=ll_pz_data_copy.skills,
            deaths=ll_pz_data_copy.deaths,
            last_death=ll_pz_data_copy.last_death,
            last_death_rt=ll_pz_data_copy.last_death_rt,
            kdr=ll_pz_data_copy.kdr,
            zbits=ll_pz_data_copy.zbits
        )
    )

def update_LL_pz_data(ll_pz_data_copy, table):
    if table == "current":
        table = ll_pz_data_tbl
    elif table == "longcopy":
        table = ll_pz_data_longcopy_tbl
    elif table == "shortcopy":
        table = ll_pz_data_shortcopy_tbl
    botdb.exe_Commit(
        update(table)
        .where(table.c.discord_id == ll_pz_data_copy.discord_id)
        .values(
            server_id=ll_pz_data_copy.server_id,
            server_num=ll_pz_data_copy.server_num,
            server_name=ll_pz_data_copy.server_name,
            server_wipe=ll_pz_data_copy.server_wipe,
            username=ll_pz_data_copy.username,
            charname=ll_pz_data_copy.charname,
            alive=ll_pz_data_copy.alive,
            kills=ll_pz_data_copy.kills,
            total_kills=ll_pz_data_copy.total_kills,
            skills=ll_pz_data_copy.skills,
            deaths=ll_pz_data_copy.deaths,
            last_death=ll_pz_data_copy.last_death,
            last_death_rt=ll_pz_data_copy.last_death_rt,
            kdr=ll_pz_data_copy.kdr,
            zbits=ll_pz_data_copy.zbits
        )
    )

def get_LL_pz_data_by_did(discord_id: int, table):
    if table == "current":
        selected_table = ll_pz_data_tbl
    elif table == "longcopy":
        selected_table = ll_pz_data_longcopy_tbl
    elif table == "shortcopy":
        selected_table = ll_pz_data_shortcopy_tbl
    result = botdb.exe(
        select(
            selected_table.c.discord_id, 
            selected_table.c.server_id,
            selected_table.c.server_num, 
            selected_table.c.server_name,
            selected_table.c.server_wipe, 
            selected_table.c.username, 
            selected_table.c.charname,
            selected_table.c.alive, 
            selected_table.c.kills, 
            selected_table.c.total_kills, 
            selected_table.c.skills, 
            selected_table.c.deaths, 
            selected_table.c.last_death, 
            selected_table.c.last_death_rt, 
            selected_table.c.kdr, 
            selected_table.c.zbits).where(selected_table.c.discord_id == discord_id))
    return result

def get_LL_pz_data_by_server(server_id: int, table):
    if table == "current":
        selected_table = ll_pz_data_tbl
    elif table == "longcopy":
        selected_table = ll_pz_data_longcopy_tbl
    elif table == "shortcopy":
        selected_table = ll_pz_data_shortcopy_tbl
    result = botdb.exe_Multi(
        select(
            selected_table.c.discord_id, 
            selected_table.c.server_id, 
            selected_table.c.server_num,
            selected_table.c.server_name,
            selected_table.c.server_wipe, 
            selected_table.c.username, 
            selected_table.c.charname,
            selected_table.c.alive, 
            selected_table.c.kills, 
            selected_table.c.total_kills, 
            selected_table.c.skills, 
            selected_table.c.deaths, 
            selected_table.c.last_death, 
            selected_table.c.last_death_rt, 
            selected_table.c.kdr, 
            selected_table.c.zbits).where(selected_table.c.server_id == server_id))
    return result

def save_LL_pz_data_challengecopy(ll_pz_data_challengecopy):
    botdb.exe_Commit(
        insert(ll_pz_data_challengecopy_tbl)
        .values(
            id=ll_pz_data_challengecopy.id,
            discord_id=ll_pz_data_challengecopy.discord_id,
            server_id=ll_pz_data_challengecopy.server_id,
            server_num=ll_pz_data_challengecopy.server_num,
            server_name=ll_pz_data_challengecopy.server_name,
            server_wipe=ll_pz_data_challengecopy.server_wipe,
            username=ll_pz_data_challengecopy.username,
            charname=ll_pz_data_challengecopy.charname,
            alive=ll_pz_data_challengecopy.alive,
            kills=ll_pz_data_challengecopy.kills,
            total_kills=ll_pz_data_challengecopy.total_kills,
            skills=ll_pz_data_challengecopy.skills,
            deaths=ll_pz_data_challengecopy.deaths,
            last_death=ll_pz_data_challengecopy.last_death,
            last_death_rt=ll_pz_data_challengecopy.last_death_rt,
            kdr=ll_pz_data_challengecopy.kdr,
            zbits=ll_pz_data_challengecopy.zbits
        )
    )

def update_LL_pz_data_challengecopy(ll_pz_data_challengecopy):
    botdb.exe_Commit(
        update(ll_pz_data_challengecopy_tbl)
        .where(ll_pz_data_challengecopy_tbl.c.id == ll_pz_data_challengecopy.id)
        .values(
            id=ll_pz_data_challengecopy.id,
            discord_id=ll_pz_data_challengecopy.discord_id,
            server_id=ll_pz_data_challengecopy.server_id,
            server_num=ll_pz_data_challengecopy.server_num,
            server_name=ll_pz_data_challengecopy.server_name,
            server_wipe=ll_pz_data_challengecopy.server_wipe,
            username=ll_pz_data_challengecopy.username,
            charname=ll_pz_data_challengecopy.charname,
            alive=ll_pz_data_challengecopy.alive,
            kills=ll_pz_data_challengecopy.kills,
            total_kills=ll_pz_data_challengecopy.total_kills,
            skills=ll_pz_data_challengecopy.skills,
            deaths=ll_pz_data_challengecopy.deaths,
            last_death=ll_pz_data_challengecopy.last_death,
            last_death_rt=ll_pz_data_challengecopy.last_death_rt,
            kdr=ll_pz_data_challengecopy.kdr,
            zbits=ll_pz_data_challengecopy.zbits
        )
    )

def get_LL_pz_challengecopy_by_id(challenge_id: int):
    result = botdb.exe(
        select(
            ll_pz_data_challengecopy_tbl.c.id,
            ll_pz_data_challengecopy_tbl.c.discord_id,
            ll_pz_data_challengecopy_tbl.c.server_id,
            ll_pz_data_challengecopy_tbl.c.server_num,
            ll_pz_data_challengecopy_tbl.c.server_name,
            ll_pz_data_challengecopy_tbl.c.server_wipe,
            ll_pz_data_challengecopy_tbl.c.username,
            ll_pz_data_challengecopy_tbl.c.charname,
            ll_pz_data_challengecopy_tbl.c.alive,
            ll_pz_data_challengecopy_tbl.c.kills,
            ll_pz_data_challengecopy_tbl.c.total_kills,
            ll_pz_data_challengecopy_tbl.c.skills,
            ll_pz_data_challengecopy_tbl.c.deaths,
            ll_pz_data_challengecopy_tbl.c.last_death,
            ll_pz_data_challengecopy_tbl.c.last_death_rt,
            ll_pz_data_challengecopy_tbl.c.kdr,
            ll_pz_data_challengecopy_tbl.c.zbits
        )
        .where(ll_pz_data_challengecopy_tbl.c.id == challenge_id)
    )
    return result

def get_all_challengecopy_data_by_server(server_id: int):
    result = botdb.exe_Multi(
        select(
            ll_pz_data_challengecopy_tbl.c.id,
            ll_pz_data_challengecopy_tbl.c.discord_id,
            ll_pz_data_challengecopy_tbl.c.server_id,
            ll_pz_data_challengecopy_tbl.c.server_num,
            ll_pz_data_challengecopy_tbl.c.server_name,
            ll_pz_data_challengecopy_tbl.c.server_wipe,
            ll_pz_data_challengecopy_tbl.c.username,
            ll_pz_data_challengecopy_tbl.c.charname,
            ll_pz_data_challengecopy_tbl.c.alive,
            ll_pz_data_challengecopy_tbl.c.kills,
            ll_pz_data_challengecopy_tbl.c.total_kills,
            ll_pz_data_challengecopy_tbl.c.skills,
            ll_pz_data_challengecopy_tbl.c.deaths,
            ll_pz_data_challengecopy_tbl.c.last_death,
            ll_pz_data_challengecopy_tbl.c.last_death_rt,
            ll_pz_data_challengecopy_tbl.c.kdr,
            ll_pz_data_challengecopy_tbl.c.zbits
        )
        .where(ll_pz_data_challengecopy_tbl.c.server_id == server_id)
    )
    return result

def delete_LL_pz_challengecopy_by_id(challenge_id: int):
    botdb.exe_Commit(ll_pz_data_challengecopy_tbl.delete().where(ll_pz_data_challengecopy_tbl.c.id == challenge_id))

def get_Pz_kills(server_id, username):
    result = pzdb.exe_Lite(select(player.c.vp.label('kills')).where(and_(player.c.server_id == server_id, player.c.username == username, player.c.died_ingame.is_(None))))
    return result

def get_Pz_total_kills(server_id, username):
    result = pzdb.exe_Lite(select(sa.func.sum(player.c.vp).label('kills')).where(and_(player.c.server_id == server_id, player.c.username == username)))
    return result

def get_Pz_skill(server_id, username, skill):
    result = pzdb.exe_Lite(select(player_xp.c.current.label(skill)).select_from(player_xp.join(player, player_xp.c.player_id == player.c.player_id))
                            .where(and_(player.c.server_id == server_id,player.c.username == username,player_xp.c.perk_name == skill,player.c.died_ingame.is_(None))).order_by(player_xp.c.perk_name.desc()).limit(1))
    return result

def get_Pz_deaths(server_id, username):
    result = pzdb.exe_Lite_multi(select(player.c.died_ingame.label('deaths')).where(and_(player.c.server_id == server_id, player.c.username == username, player.c.died_ingame.isnot(None))))
    return result

def get_Pz_last_death(server_id, username):
    result = pzdb.exe_Lite(select(player.c.died_ingame.label('last_death')).where(player.c.server_id == server_id)
                            .where(player.c.username == username).where(player.c.died_ingame.isnot(None)).order_by(player.c.died_ingame.desc()).limit(1))
    return result

def get_Pz_last_death_rt(server_id, username):
    result = pzdb.exe_Lite(select(player.c.died_time.label('last_death_rt')).where(player.c.server_id == server_id)
                            .where(player.c.username == username).where(player.c.died_ingame.isnot(None)).order_by(player.c.died_ingame.desc()).limit(1))
    return result

################################################################################################
###################################### LL Challenge Functions ##################################
################################################################################################
def get_Pz_challenge(id: int):
    result = botdb.exe(
        select(
            ll_pz_challenges_tbl.c.id, 
            ll_pz_challenges_tbl.c.discord_id, 
            ll_pz_challenges_tbl.c.assigned, 
            ll_pz_challenges_tbl.c.name, 
            ll_pz_challenges_tbl.c.description, 
            ll_pz_challenges_tbl.c.time_limit, 
            ll_pz_challenges_tbl.c.targets, 
            ll_pz_challenges_tbl.c.targets_completed, 
            ll_pz_challenges_tbl.c.reward,
            ll_pz_challenges_tbl.c.warned, 
            ll_pz_challenges_tbl.c.completed
        )
        .where(ll_pz_challenges_tbl.c.id == id)
    )
    return result

def get_Random_pz_challenge():
    result = botdb.exe(select(
        ll_pz_challenges_tbl.c.id, 
        ll_pz_challenges_tbl.c.discord_id, 
        ll_pz_challenges_tbl.c.assigned, 
        ll_pz_challenges_tbl.c.name, 
        ll_pz_challenges_tbl.c.description, 
        ll_pz_challenges_tbl.c.time_limit,
        ll_pz_challenges_tbl.c.targets,
        ll_pz_challenges_tbl.c.targets_completed, 
        ll_pz_challenges_tbl.c.reward,
        ll_pz_challenges_tbl.c.warned, 
        ll_pz_challenges_tbl.c.completed
        )
        .where(ll_pz_challenges_tbl.c.discord_id.is_(None))
        .order_by(sa.func.rand()).limit(1)
    )
    return result

def get_all_available():
    result = botdb.exe_Multi(select(
        ll_pz_challenges_tbl.c.id, 
        ll_pz_challenges_tbl.c.discord_id, 
        ll_pz_challenges_tbl.c.assigned, 
        ll_pz_challenges_tbl.c.name, 
        ll_pz_challenges_tbl.c.description, 
        ll_pz_challenges_tbl.c.time_limit, 
        ll_pz_challenges_tbl.c.targets,
        ll_pz_challenges_tbl.c.targets_completed, 
        ll_pz_challenges_tbl.c.reward,
        ll_pz_challenges_tbl.c.warned, 
        ll_pz_challenges_tbl.c.completed
        )
        .where(ll_pz_challenges_tbl.c.discord_id.is_(None))
    )
    return result

def get_all_by_did(discord_id: int):
    result = botdb.exe_Multi(select(
        ll_pz_challenges_tbl.c.id, 
        ll_pz_challenges_tbl.c.discord_id, 
        ll_pz_challenges_tbl.c.assigned, 
        ll_pz_challenges_tbl.c.name, 
        ll_pz_challenges_tbl.c.description, 
        ll_pz_challenges_tbl.c.time_limit, 
        ll_pz_challenges_tbl.c.targets,
        ll_pz_challenges_tbl.c.targets_completed, 
        ll_pz_challenges_tbl.c.reward,
        ll_pz_challenges_tbl.c.warned, 
        ll_pz_challenges_tbl.c.completed
        )
        .where(ll_pz_challenges_tbl.c.discord_id == discord_id)
    )
    return result

def get_all_active(discord_id: int):
    result = botdb.exe_Multi(select(
        ll_pz_challenges_tbl.c.id, 
        ll_pz_challenges_tbl.c.discord_id, 
        ll_pz_challenges_tbl.c.assigned, 
        ll_pz_challenges_tbl.c.name, 
        ll_pz_challenges_tbl.c.description, 
        ll_pz_challenges_tbl.c.time_limit, 
        ll_pz_challenges_tbl.c.targets,
        ll_pz_challenges_tbl.c.targets_completed, 
        ll_pz_challenges_tbl.c.reward,
        ll_pz_challenges_tbl.c.warned, 
        ll_pz_challenges_tbl.c.completed
        )
        .where(and_(
                ll_pz_challenges_tbl.c.discord_id == discord_id, 
                ll_pz_challenges_tbl.c.completed.is_(None)
        )
    ))
    return result

def get_all_comp_by_did(discord_id: int):
    result = botdb.exe_Multi(select(
        ll_pz_challenges_tbl.c.id, 
        ll_pz_challenges_tbl.c.discord_id, 
        ll_pz_challenges_tbl.c.assigned, 
        ll_pz_challenges_tbl.c.name, 
        ll_pz_challenges_tbl.c.description, 
        ll_pz_challenges_tbl.c.time_limit, 
        ll_pz_challenges_tbl.c.targets,
        ll_pz_challenges_tbl.c.targets_completed, 
        ll_pz_challenges_tbl.c.reward,
        ll_pz_challenges_tbl.c.warned, 
        ll_pz_challenges_tbl.c.completed
        )
        .where(and_(
                ll_pz_challenges_tbl.c.discord_id == discord_id, 
                ll_pz_challenges_tbl.c.completed.isnot(None)
                )
            )
        )
    return result

def save_Pz_challenge(self):
    botdb.exe_Commit(ll_pz_challenges_tbl.insert()
        .values(
            name=self.name, 
            description=self.description, 
            time_limit=self.time_limit, 
            targets=self.targets,
            targets_completed=self.targets_completed, 
            reward=self.reward
            )
        )

def update_Pz_challenge(self):
    botdb.exe_Commit(ll_pz_challenges_tbl.update()
        .where(ll_pz_challenges_tbl.c.id == self.id)
            .values(
                id=self.id,
                discord_id=self.discord_id,
                assigned=self.assigned,
                name=self.name, 
                description=self.description, 
                time_limit=self.time_limit, 
                targets=self.targets,
                targets_completed=self.targets_completed, 
                reward=self.reward,
                warned=self.warned,
                completed=self.completed
            )
        )

def delete_Pz_challenge(self):
    botdb.exe_Commit(ll_pz_challenges_tbl.delete().where(ll_pz_challenges_tbl.c.id == self.id))

################################################################################################
######################################## LL SDrop Functions ####################################
################################################################################################
def save_sdrop_order(self):
    result = botdb.exe_Commit(
        ll_pz_sdrop_orders_tbl.insert().values(
            discord_id=self.discord_id, 
            charname=self.charname, 
            cost=self.cost,
            paid=self.paid,
            status=self.status, 
            type=self.type.name, 
            city=self.city.name, 
            zone=self.zone.name,
            delivery_method=self.delivery_method.name, 
            placed=self.placed,
            delivered=self.delivered
        )
    )
    return result.inserted_primary_key[0]

def update_sdrop_order(self):
    botdb.exe_Commit(
        ll_pz_sdrop_orders_tbl.update().where(
            ll_pz_sdrop_orders_tbl.c.id == self.id
        ).values(
            discord_id=self.discord_id, 
            charname=self.charname, 
            cost=self.cost,
            paid=self.paid,
            status=self.status, 
            type=self.type.name, 
            city=self.city.name, 
            zone=self.zone.name,
            delivery_method=self.delivery_method.name, 
            placed=self.placed,
            delivered=self.delivered
        )
    )

def get_sdrop_order_by_id(order_id: int):
    result = botdb.exe(
        select(
            ll_pz_sdrop_orders_tbl.c.id, 
            ll_pz_sdrop_orders_tbl.c.discord_id, 
            ll_pz_sdrop_orders_tbl.c.charname, 
            ll_pz_sdrop_orders_tbl.c.cost, 
            ll_pz_sdrop_orders_tbl.c.paid, 
            ll_pz_sdrop_orders_tbl.c.status,
            ll_pz_sdrop_orders_tbl.c.type,
            ll_pz_sdrop_orders_tbl.c.city,
            ll_pz_sdrop_orders_tbl.c.zone,
            ll_pz_sdrop_orders_tbl.c.delivery_method,
            ll_pz_sdrop_orders_tbl.c.placed,
            ll_pz_sdrop_orders_tbl.c.delivered
        )
        .where(ll_pz_sdrop_orders_tbl.c.id == order_id)
    )
    return result

def delete_sdrop_order(self):
    botdb.exe_Commit(ll_pz_sdrop_orders_tbl.delete().where(ll_pz_sdrop_orders_tbl.c.id == self.id))

def save_sdrop_type(self):
    botdb.exe_Commit(
        ll_pz_sdrop_tbl.insert().values(
            name=self.name, 
            original_cost=self.original_cost, 
            variation=self.variation, 
            current_cost=self.current_cost, 
            availability=self.availability
        )
    )

def update_sdrop_type(self):
    botdb.exe_Commit(
        ll_pz_sdrop_tbl.update().where(
            ll_pz_sdrop_tbl.c.name == self.name
        ).values(
            original_cost=self.original_cost, 
            variation=self.variation, 
            current_cost=self.current_cost, 
            availability=self.availability
        )
    )

def get_all_sdrop_types():
    result = botdb.exe_Multi(
        select(
            ll_pz_sdrop_tbl.c.name, 
            ll_pz_sdrop_tbl.c.original_cost, 
            ll_pz_sdrop_tbl.c.variation, 
            ll_pz_sdrop_tbl.c.current_cost, 
            ll_pz_sdrop_tbl.c.availability
        )
    )
    return result

def get_sdrop_type_by_name(name: str):
    result = botdb.exe(
        select(
            ll_pz_sdrop_tbl.c.name, 
            ll_pz_sdrop_tbl.c.original_cost, 
            ll_pz_sdrop_tbl.c.variation, 
            ll_pz_sdrop_tbl.c.current_cost, 
            ll_pz_sdrop_tbl.c.availability
        )
        .where(ll_pz_sdrop_tbl.c.name == name)
    )
    return result


# L4D2 Functions

####### MISC Functions #######
