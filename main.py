import re
import sys
import random
import asyncio

from config import api_id, api_hash

from telethon.sync import TelegramClient

technologies = [
    # Programming Languages
    "Python", "JavaScript", "Java", "C++", "C#", "Ruby", "Swift", "Kotlin",
    "PHP", "TypeScript", "Go", "Rust", "Scala", "Perl", "R", "Objective-C",
    "Dart", "Haskell", "Lua", "Julia",

    # Web Frameworks
    "Django", "Flask", "Express", "React", "Angular", "Vue", "Spring Boot",
    "Ruby on Rails", "Laravel", "Symfony", "ASP.NET Core", "Svelte", "Meteor",
    "Next", "Nuxt", "NestJS", "Phoenix", "Play Framework", "Ember",
    "Backbone",

    # Databases
    "MySQL", "PostgreSQL", "SQLite", "MongoDB", "Redis", "Cassandra", "MariaDB",
    "Oracle Database", "Microsoft SQL Server", "CouchDB", "DynamoDB",
    "Firebase Realtime Database", "Elasticsearch", "Neo4j", "InfluxDB",
    "CockroachDB", "RethinkDB", "ArangoDB", "FaunaDB", "ClickHouse",

    # Other Popular Technologies
    "Docker", "Kubernetes", "Jenkins", "Git", "GitHub", "GitLab", "Bitbucket",
    "Terraform", "Ansible", "Puppet", "Chef", "Vagrant", "AWS", "Azure",
    "Google Cloud Platform", "Heroku", "DigitalOcean", "Apache Kafka",
    "RabbitMQ", "Apache Hadoop", "Spark", "TensorFlow", "PyTorch",
    "scikit-learn", "OpenCV", "Selenium", "Cypress", "Jupyter", "Visual Studio Code",
    "IntelliJ IDEA"
]

ADDITIONS = ["talk", "group", "comm", "community", "club"]
COUNTRIES = ["UA", "RU", "IN", "Україна", "Украина", "Россия", "India"]

OTHER_STUFF = ["мафія", "мафия"]

def create_telegram_client(telegram_client, api_id, api_hash):
    """Creates and starts a Telegram client."""
    client = telegram_client(
        session='tg',
        api_id=api_id,
        api_hash=api_hash,
        timeout=7000,
        device_model='scriptgram',
        lang_code='es-ES',
    )
    client.start()
    return client


def parse_bot_response(bot_response):
    pattern = re.compile(r'(@[^\s]+) \*\*([\d\.K]+)\*\*')
    matches = pattern.findall(bot_response)

    results = []
    for username, members in matches:
        if 'K' in members:
            members = int(float(members.replace('K', '')) * 1000)
        else:
            members = int(members)

        results.append({'username': username, 'members': members})

    return results


def build_queries():
    technologies_with_additions = []
    technologies_with_countries = []

    for tech in technologies:
        for addition in ADDITIONS:
            technologies_with_additions.append(f"{tech} {addition}")

    for tech in technologies:
        for country in COUNTRIES:
            technologies_with_countries.append(f"{tech} {country}")

    combined_list = technologies + technologies_with_additions + technologies_with_countries + OTHER_STUFF

    return combined_list


async def send_message_to_bot(client, bot_username, message):
    bot = await client.get_entity(bot_username)
    sent_message = await client.send_message(bot, message)

    while True:
        messages = await client.get_messages(bot, limit=1)
        if messages:
            msg = messages[0]
            if msg.id != sent_message.id:
                return msg.text

        await asyncio.sleep(1.0)


async def search_and_submit(client, query):
    tgdb = 'tgdb_bot'
    telesint = 'telesint_bot'
    message = f'/groups {query}'

    tgdb_response = await send_message_to_bot(client, tgdb, message)
    if tgdb_response == "Sorry, your search returned no results.":
        print(f"[-] no results for {query}")
        return
    elif tgdb_response == "You have reached the daily search limit. Contact support with /support for more information or try again tomorrow.":
        print("[-] you have hit a daily rate limit in tgdb_bot. exiting...")
        sys.exit()

    results = parse_bot_response(tgdb_response)
    print(f"[+] got {len(results)} results for {query}")
    for result in results:
        if result['members'] >= 15:
            username = result['username']
            print(f"[*] submiting {username}...")
            telesint_response = await send_message_to_bot(client, telesint, username)
            if "🗃 Наличие в базе: ✅" not in telesint_response:
                print(f"[+] {username} is not in the database. +3 requests")
            elif telesint_response == "Вы отправляете запросы слишком часто. Пожалуйста, подождите немного.":
                print("[-] got rate limited")
            elif telesint_response == "Не существует Telegram аккаунта с таким именем":
                print("[-] invalid link")
            else:
                print(f"[-] {username} already in database")

        await asyncio.sleep(2.1)


async def main(client):
    built_queries = build_queries()
    used_queries = []

    for _ in range(50):
        query = random.choice(built_queries)
        if query in used_queries:
            print("[*] query was already used. getting a new query")
            query = random.choise(built_queries)
        await search_and_submit(client, query)
        used_queries.append(query)


if __name__ == "__main__":
    client = create_telegram_client(TelegramClient, api_id, api_hash)
    client.loop.run_until_complete(main(client))
