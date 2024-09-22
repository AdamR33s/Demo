PYTHON
The file "old_db_manager.py" is the first version of this created over the first 9 - 12 months of the project. The second file " new_db_manager.py" is the re-write I recently completed after getting a thorough understanding of Sync vs ASync. These both use SQL Alchemy, although the new module demonstrates full and correct usage of the ORM layer and DAO's. This also uses a config parser to hide sensitive strings.

GRAPHQL
A large Graph QL Query project for serving data and services to users over discord. This is a work in progress and complicated by bad data all over the sets. The ll_tarkov_api.py file has the queries and DSL objects etc. The tarkov_caches file shows the amount of structured text data being handled which is actually around 2mb with the current inline fragments.