**SUMMARY**
    > Welcome to my Demonstration Repo (The KYR Project - An International Online Community for ND Developers and Gamers). 
    This Repo is designed to give a cross-section of the wider KYR Community Project, giving some examples of the languages, data structures and software produced.

**OVERVIEW**
- Documents 
    My CV - ("Adam Rees - CV - 280424.docx") && Covering Letter ("Covering Letter.docx")
- Examples
    Folders Containing Chunks of Example Code && Readme's to give context

**PROJECT TECH**
- OS:
    - Ubuntu LTS 18.04 | 22.04
    - UFW
- CONTAINERS:
    - Docker (24.0.7)

- LANGUAGES:
    - Python (3.11)
    - TypeScript (5.2.2) 
    - C# (10 - 12) & dotnet (8.0.301)
    - LUA (5.1)
    - GraphQL (API)

- ORM:
    - SQL Alchemy
    - Prisma

- DATABASES:
    - SQLlite
    - MySQL
    - DBM

- STRUCTURED DATA:
    - Yaml
    - Json
    - GraphQL

- EXPERIMENTAL LANGUAGES:
    - Java (Kahlua)
    - Haskell
    - GoLang

**CONTACT DETAILS**
- Personal
    Adam Rees, 07368 604934, Adzz.GSAU@Gmail.com

**OVERVIEW**
    > Please feel free to explore, I hope you'll find this interesting and informative in terms of my skills and understanding.
    If you have any queries or questions, or any issues accessing these files, please reach out to me on the details above!
    Many Thanks, Adam









Project Examples:

PYTHON - DB Manager - The Database Manager for on of my Community Bots. Overview - The file "old_db_manager.py" is the first version of this created over the first 9 - 12 months of the project. The second file " new_db_manager.py" is the re-write I recently completed after getting a thorough understanding of Sync vs ASync. These both use SQL Alchemy, although the new module demonstrates full and correct usage of the ORM layer and DAO's. This also uses a config parser to hide sensitive strings.

PYTHON - Tarkov_api - A large Graph QL Query project for serving data and services to users over discord. This is a work in progress and complicated by bad data all over the sets. The ll_tarkov_api.py file has the queries and DSL objects etc. The tarkov_caches file shows the amount of structured text data being handled which is actually around 2mb with the current inline fragments.

C# - Godot 2D Video Game - I've started building my own 2D Video Game using the Godot Engine and C#. This is quite a complicated way to learn C# but learning quickly and already have something running. The files "PlayerShip.cs" and "SpaceUI.cs" demonstrate some of the C# Code I've been writing for this project.

Docker/Docker Compose - Containers - I've used Docker across the project for security and convenience. I've also used some config for setup in an entrypoint script (python) which I've also included under the Docker Examples Folder. Files "pz_test_entrypoint.py" and "pz_test_dockerfile" will give some insight into how I've been using containers on my Dedicated Server.

TypeScript - Bot and ORM - I also wrote a discord bot in Typescript and again used an ORM layer (PRISMA). Typescript I've spent less time on than other languages but love some of it's features. I've not spent as much time on the environmental elements of JavaScript/Typescript either. I had some assistance in getting ESBuilder up and running to make the TS project happen. I've included files "cm.ts", "cmAdverts.ts", "cmDb.ts" and "schema.prisma" to demonstrate some of the basic functionality and intial API hook in this has. Functionality for this is still quite basic at the moment.

LUA Script - Video Game Modifications - A very interesting project undertaken to modify a piece of Software originally written in Java, using a KHLUA, with a top level of LUA Script. This presented a whole range of crazy challenges like the iteration of objects returned from Java crashing due to the difference in Indexing! I've included some of the base Modules I wrote as part of this project (community request). Amazingly when released to the general public I achieved over 100,000 public subcribers for these projects: Steam Workshop::[KYR] Real Weather Mod (steamcommunity.com) Steam Workshop::[KYR] Meds, Cures and Delays (steamcommunity.com) Steam Workshop::[KYR] Survival & Crafting (steamcommunity.com) I've included files "kyrMCDmedeffects.lua", "kyrMCDsetup.lua" and "kyrMCDvaccine.lua" to give a taste of what these projects included.