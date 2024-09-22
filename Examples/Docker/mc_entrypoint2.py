import os
import sys
import shutil
import json
import asyncio
import aioconsole
import aiohttp
from aiohttp import web
import mc_settings as settings

sv_ref = os.environ["sv_ref"]
sv_port = os.environ["sv_port"]
if sv_ref in settings.server_cvars:
    cvars = settings.server_cvars[sv_ref]

sv_passwd = ""
rcon_passwd = ""
apiport = ""
apipasswd = ""
running_str = "Query running on 0.0.0.0:"
forge_install_str = "You can delete this installer file now if you wish"

try:
    shutil.copy("/mc/server/apiadmin.json", "/mc/setup/apiadmin.json")
except Exception as e:
    print("Error Copying API Admin File", e)
    sys.exit(1)
try:
    with open("/mc/setup/apiadmin.json", "r") as f:
        json_string = f.read()
        data_dict = json.loads(json_string)
        sv_passwd = data_dict["sv_passwd"]
        rcon_passwd = data_dict["rcon_passwd"]
        apiport = data_dict["apiport"]
        apipasswd = data_dict["apipasswd"]
except Exception as e:
    print("Error Reading API Admin File", e)
    sys.exit(1)

cvars["rcon_passwd"] = rcon_passwd
cvars["sv_port"] = sv_port

jvm_memory_args = [
    "-Xmx4G",
    "-Xms1G",
    "-XX:SoftMaxHeapSize=3G",
    "-XX:+UnlockExperimentalVMOptions",
    "-XX:+UseZGC",
]
forge_install_command = [
    "java",
    "-jar",
    "forge-1.21.1-52.0.16-installer.jar",
    "--installServer",
]
run_forge_command = [
    "/bin/sh",
    "run.sh",
    "--port",
    sv_port,
    "--nogui",
]


async def run_server():
    await copy_gamefiles()
    await format_eula_file()
    await format_settings_file()
    await format_user_jvm_args_file()
    await forge_install()
    await copy_forgefiles()
    print("Waiting for 5 seconds...")
    await asyncio.sleep(5)
    print("Starting server")
    await running_game_server()


async def copy_gamefiles():
    try:
        shutil.copy("/mc/setup/server.jar", "/mc/server/server.jar")
        shutil.copy(
            "/mc/setup/forge-1.21.1-52.0.16-installer.jar",
            "/mc/server/forge-1.21.1-52.0.16-installer.jar",
        )
    except Exception as e:
        print("Game Files error. Awaiting 3 mins to explore container: ")
        print("Error: ", e)
        await asyncio.sleep(180)
        sys.exit(1)


async def copy_forgefiles():
    try:
        shutil.copy(
            "/mc/server/./libraries/net/minecraftforge/forge/1.21.1-52.0.16/forge-1.21.1-52.0.16-server.jar",
            "/mc/server/forge-1.21.1-52.0.16-server.jar",
        )
        print("Forge Server Copied")
    except Exception as e:
        print("Forge Files error. Awaiting 3 mins to explore container: ")
        print("Error: ", e)
        await asyncio.sleep(180)
        sys.exit(1)


async def format_eula_file():
    try:
        with open("/mc/setup/eula.txt", "r") as e:
            eula_content = e.read()
        with open("/mc/server/eula.txt", "w") as ne:
            ne.write(eula_content)
    except Exception as e:
        print("Server eula File error. Awaiting 3 mins to explore container: ")
        print("Error: ", e)
        await asyncio.sleep(180)
        sys.exit(1)


async def format_settings_file():
    try:
        with open("/mc/setup/server.properties", "r") as f:
            settings_content = f.read()
        formatted_settings = settings_content.format(**cvars)
        with open("/mc/server/server.properties", "w") as g:
            g.write(formatted_settings)
    except Exception as e:
        print("Server CFG File error. Awaiting 3 mins to explore container: ")
        print("Error: ", e)
        await asyncio.sleep(180)
        sys.exit(1)


async def format_user_jvm_args_file():
    try:
        formatted_args = " ".join(jvm_memory_args) + "\n"
        with open("/mc/server/user_jvm_args.txt", "w") as f:
            f.write(formatted_args)
    except Exception as e:
        print(
            "Server user_jvm_args.txt File error. Awaiting 3 mins to explore container: "
        )
        print("Error: ", e)
        await asyncio.sleep(180)
        sys.exit(1)


async def forge_install():
    os.chdir("/mc/server/")
    forge_install_instance = await asyncio.create_subprocess_exec(
        *forge_install_command,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
        stdin=asyncio.subprocess.PIPE,
    )
    async for forge_install_out_line in forge_install_instance.stdout:
        print(
            "Forge Install Says: "
            + forge_install_out_line.decode("utf-8", "replace").strip()
        )


async def running_game_server():  # CHANGE TO FORGE SERVER RUNNING
    os.chdir("/mc/server/")
    game_server = await asyncio.create_subprocess_exec(
        *run_forge_command,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
        stdin=asyncio.subprocess.PIPE,
    )
    async with asyncio.TaskGroup() as tg:
        in_task = tg.create_task(running_server_inpipe(game_server))
        out_task = tg.create_task(running_server_outpipe(game_server))
        err_task = tg.create_task(running_server_errpipe(game_server))
        remote_control = tg.create_task(remote_http_controller(game_server))
        retcode = await game_server.wait()
        if retcode == 0:
            print("Server exited normally")
        else:
            print(f"Error: server exited with code {retcode}")
        in_task.cancel()
        out_task.cancel()
        err_task.cancel()
        remote_control.cancel()
    sys.exit(0 if retcode == 0 else 1)


async def running_server_inpipe(game_server: asyncio.subprocess.Process):
    while True:
        line = await aioconsole.ainput("Enter Command: ")
        game_server.stdin.write(line.encode("utf-8") + b"\n")
        await game_server.stdin.drain()
        print("INPIPE - Command Sent: " + line)


async def running_server_outpipe(game_server: asyncio.subprocess.Process):
    async for out_line in game_server.stdout:
        print("OUTPIPE - Server Says: " + out_line.decode("utf-8", "replace"))


async def running_server_errpipe(game_server: asyncio.subprocess.Process):
    async for err_line in game_server.stderr:
        print("ERRORPIPE - Server Error: " + err_line.decode("utf-8", "replace"))


async def remote_http_controller(game_server: asyncio.subprocess.Process):
    app = aiohttp.web.Application()

    async def command(request):
        data = await request.text()
        password, command = data.split(":", 1)
        if password != apipasswd:
            return aiohttp.web.Response(text="Invalid Password", status=401)
        game_server.stdin.write(command.encode("utf-8") + b"\n")
        await game_server.stdin.drain()
        print("INPIPE - Command Sent: " + command)
        return aiohttp.web.Response(
            text=f"Command Received and Successfully Executed", status=200
        )

    app.router.add_post("/command", command)
    runner = aiohttp.web.AppRunner(app)
    await runner.setup()
    site = aiohttp.web.TCPSite(runner, "0.0.0.0", f"{apiport}")
    print(f"Remote Control API Running on Port {apiport}")
    await site.start()


asyncio.run(run_server())
