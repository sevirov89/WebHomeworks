import aiohttp
import asyncpg
import asyncio
from config import DB_CONFIG


async def fetch_character(session, character_id):
    url = f"https://www.swapi.tech/api/people/{character_id}"
    async with session.get(url) as response:
        if response.status == 200:
            data = await response.json()
            return data.get('result', {}).get('properties')
        return None


async def insert_character(conn, character_data, character_id):
    if not character_data:
        return

    await conn.execute('''
        INSERT INTO star_wars_people (
            id, birth_year, eye_color, gender, hair_color, 
            homeworld, mass, name, skin_color
        ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
        ON CONFLICT (id) DO NOTHING
    ''',
                       character_id,
                       character_data.get('birth_year'),
                       character_data.get('eye_color'),
                       character_data.get('gender'),
                       character_data.get('hair_color'),
                       character_data.get('homeworld'),
                       character_data.get('mass'),
                       character_data.get('name'),
                       character_data.get('skin_color'))


async def process_character(session, conn, character_id):
    try:
        character_data = await fetch_character(session, character_id)
        if character_data:
            await insert_character(conn, character_data, character_id)
            print(f"Processed character {character_id}")
        else:
            print(f"Character {character_id} not found")
    except Exception as e:
        print(f"Error processing character {character_id}: {e}")


async def main():
    conn = await asyncpg.connect(**DB_CONFIG)
    async with aiohttp.ClientSession() as session:
        tasks = []
        for character_id in range(1, 101):
            task = asyncio.create_task(process_character(session, conn, character_id))
            tasks.append(task)

        await asyncio.gather(*tasks)

    await conn.close()


if __name__ == '__main__':
    asyncio.run(main())