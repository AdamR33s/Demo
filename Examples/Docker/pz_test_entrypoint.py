#!/usr/bin/env python3
import os
import sys
import asyncio
import aioconsole
import shutil
import aiohttp
import json
from aiohttp import web
from jinja2 import Environment, FileSystemLoader
import pz_settings as settings

sv_passwd = ""
rcon_passwd = ""
apiport = ""
apipasswd = ""
mod_install = False

try:
    shutil.copy("/home/pz/Zomboid/apiadmin.json", "/pz/setup/apiadmin.json")
    os.remove("/home/pz/Zomboid/apiadmin.json")
except Exception as e:
    print("Error Copying and Removing API Admin File", e)
    sys.exit(1)

try:
    with open("/pz/setup/apiadmin.json", "r") as f:
        json_string = f.read()
        data_dict = json.loads(json_string)
        sv_passwd = data_dict["sv_passwd"]
        rcon_passwd = data_dict["rcon_passwd"]
        apiport = data_dict["apiport"]
        apipasswd = data_dict["apipasswd"]
except Exception as e:
    print("Error Reading API Admin File", e)
    sys.exit(1)

sv_ref = os.environ["sv_ref"]
ini = settings.server_inis[sv_ref]
cvars = settings.server_cvars[sv_ref]
ini["rcon_passwd"] = rcon_passwd
ini["sv_passwd"] = sv_passwd

password_prompt_string = "Enter new administrator password:"
confirm_prompt_string = "Confirm the password:"
setup_complete_string = "LOADING ASSETS: FINISH"
server_first_start_string = "Zomboid Server is VAC Secure"
server_start_string = "RCON: listening on port"
install_command = [
    "/steamcmd/steamcmd.sh",
    "+force_install_dir",
    "/pz/server/",
    "+login",
    "anonymous",
    "+app_update",
    "380870",
    "validate",
    "+quit",
]
run_command = ["/pz/server/start-server.sh", "-servername", "{}".format(sv_ref)]


def console_print(text):
    print(text.strip())


async def server_start():
    global mod_install
    # INSTALL PROJECT ZOMBOID
    installer = await asyncio.create_subprocess_exec(*install_command)
    await installer.wait()
    if installer.returncode == 0:
        print("Install Complete")
    else:
        print(f"Error: installer exited with code {installer.returncode}")

    if os.path.isfile(f"/home/pz/Zomboid/Server/{sv_ref}.ini") and mod_install:
        print("Mod Install Detected... Templating...")
        await server_cvars_template()
        print("Templating Complete... Launching Main Server")
        await run_server()
    elif os.path.isfile(f"/home/pz/Zomboid/Server/{sv_ref}.ini"):
        print("Base Game Detected... Running Mod Install...")
        await server_cfg_template()
        await run_mod_install_server()
        print("Mod Install Complete")
        mod_install = True
        print("Mod Install Set TRUE")
        await server_start()
    else:
        print("Config Files Not Found... Proceeding with First Boot...")
        await run_base_install_server()
        await server_start()


async def run_base_install_server():
    first_game_server = await asyncio.create_subprocess_exec(
        *run_command,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
        stdin=asyncio.subprocess.PIPE,
    )
    async for startup_out_line in first_game_server.stdout:
        console_print(startup_out_line.decode())
        if password_prompt_string in startup_out_line.decode("utf-8", "replace"):
            first_game_server.stdin.write(f"{ini['rcon_passwd']}\n".encode("utf-8"))
            await first_game_server.stdin.drain()
            print("Password Entered")
            continue
        if confirm_prompt_string in startup_out_line.decode("utf-8", "replace"):
            first_game_server.stdin.write(f"{ini['rcon_passwd']}\n".encode("utf-8"))
            await first_game_server.stdin.drain()
            print("Password Confirmed")
            continue
        if server_first_start_string in startup_out_line.decode("utf-8", "replace"):
            print("First Start Complete")
            print("Rebooting Server...")
            await first_game_server.communicate(input=b"quit\n")
            await first_game_server.wait()
            break


async def run_mod_install_server():
    mod_game_server = await asyncio.create_subprocess_exec(
        *run_command,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
        stdin=asyncio.subprocess.PIPE,
    )
    async for startup_out_line in mod_game_server.stdout:
        console_print(startup_out_line.decode())
        if server_start_string in startup_out_line.decode("utf-8", "replace"):
            try:
                shutil.copy(
                    f"/home/pz/Zomboid/Server/{sv_ref}_SandboxVars.lua",
                    f"/home/pz/Zomboid/{sv_ref}_SandboxVarsNew.lua",
                )
            except Exception as e:
                console_print("Error Backing up new LUA CVars File to main Dir")
                sys.exit(1)
            print("Mod Start Complete")
            print("Rebooting Server...")
            await mod_game_server.communicate(input=b"quit\n")
            await mod_game_server.wait()
            break


async def run_server():
    game_server = await asyncio.create_subprocess_exec(
        *run_command,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
        stdin=asyncio.subprocess.PIPE,
    )
    async for startup_out_line in game_server.stdout:
        console_print(startup_out_line.decode())
        if server_start_string in startup_out_line.decode("utf-8", "replace"):
            print("Server Started")
            break

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
        console_print("INPIPE - Command Sent: " + line)


async def running_server_outpipe(game_server: asyncio.subprocess.Process):
    async for out_line in game_server.stdout:
        console_print("OUTPIPE - Server Says: " + out_line.decode("utf-8", "replace"))


async def running_server_errpipe(game_server: asyncio.subprocess.Process):
    async for err_line in game_server.stderr:
        console_print(
            "ERRORPIPE - Server Error: " + err_line.decode("utf-8", "replace")
        )


async def remote_http_controller(game_server: asyncio.subprocess.Process):
    app = aiohttp.web.Application()

    async def command(request):
        data = await request.text()
        password, command = data.split(":", 1)
        if password != apipasswd:
            return aiohttp.web.Response(text="Invalid Password", status=401)
        game_server.stdin.write(command.encode("utf-8") + b"\n")
        await game_server.stdin.drain()
        console_print("INPIPE - Command Recieved and Executed: " + command)
        return aiohttp.web.Response(
            text=f"PZ Command Received and Executed", status=200
        )

    app.router.add_post("/command", command)
    runner = aiohttp.web.AppRunner(app)
    await runner.setup()
    site = aiohttp.web.TCPSite(runner, "0.0.0.0", f"{apiport}")
    console_print(f"Remote Control API Running on Port {apiport}")
    await site.start()


async def server_cfg_template():
    try:
        env = Environment(loader=FileSystemLoader("/pz/setup/"))
        ini_template = env.get_template("server.ini")
        cvars_template = env.get_template("servercvars.lua")
    except:
        console_print("Error loading Jinja2 Templates. Exiting.")
        sys.exit(1)
    try:
        with open("/home/pz/Zomboid/Server/" + sv_ref + ".ini", "w") as f:
            f.write(ini_template.render(**ini))
    except:
        console_print("Formatting 'ini' File Error")
        sys.exit(1)
    try:
        with open("/home/pz/Zomboid/Server/" + sv_ref + "_SandboxVars.lua", "w") as g:
            g.write(cvars_template.render(**cvars))
    except:
        console_print("Formatting 'cvars' File Error")
        sys.exit(1)
    try:
        shutil.copy(
            "/pz/setup/ProjectZomboid64.json", "/pz/server/ProjectZomboid64.json"
        )
    except:
        console_print("Copying 'ProjectZomboid64.json' File Error")
        sys.exit(1)


async def server_cvars_template():
    try:
        env = Environment(loader=FileSystemLoader("/pz/setup/"))
        cvars_template = env.get_template("servercvars.lua")
    except:
        console_print("Error loading Jinja2 Templates. Exiting.")
        sys.exit(1)
    try:
        with open("/home/pz/Zomboid/Server/" + sv_ref + "_SandboxVars.lua", "w") as g:
            g.write(cvars_template.render(**cvars))
    except:
        console_print("Formatting 'cvars' File Error")
        sys.exit(1)


# RUN SERVER
asyncio.run(server_start())
