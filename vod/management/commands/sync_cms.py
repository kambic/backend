import loguru
from asgiref.sync import sync_to_async

logger = loguru.logger

from ...models import Edge, Provider

import asyncio
import aiohttp

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Fetch data from API and update Django model asynchronously'

    api_stag = {
        'url': 'https://mtcms-stag.telekom.si/api/output/offer',
        'headers': {
            'Accept': 'application/json',
            'Authorization': 'MTCMS-API-TOK eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODk234324wIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.PxnqfjHUk0MTwlL9t7EYWPT3AsfgzwCa_5v038hOoMk',
        },
    }

    api_prod = {
        'url': 'https://mtcms.telekom.si/api/output/offer',
        'headers': {
            'Accept': 'application/json',
            'Authorization': 'MTCMS-API-TOK eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0c2RhNTY3ODkwIiwibmFtZSI6IkpvaGRzYXNhZG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.KRj7Nv_a2Q4O4029fYXmn_oLQYwBRFaa3CyJ28ZORGk',
        },
    }

    api = api_stag

    async def fetch_data(self, url, session):
        """Fetch data from a given URL using aiohttp."""
        try:
            async with session.get(url, ssl=False) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    logger.error(f"Failed to fetch data from {url}: Status {response.status}")
                    return None
        except Exception as e:
            logger.error(f"Error fetching data from {url}: {e}")
            return None

    async def update_item(self, item, session):
        """Fetch and update a single Item using its ID."""
        base_url = self.api['url']
        api_url = f'{base_url}?mappedOfferId={item.offer_id}'
        item_data = await self.fetch_data(api_url, session)
        if not item_data:
            logger.error(f"No data received for item {item.id}")
            return

        if not item_data or not isinstance(item_data, dict) or 'offers' not in item_data:
            logger.error(f"No valid data received for item {item.id} (offer_id: {item.offer_id})")
            return

        if not item_data['offers']:
            logger.error(f"No offers found in data for item {item.id} (offer_id: {item.offer_id})")
            return

        try:
            # Update the item with fetched data
            offer = item_data['offers'][0]
            provider = offer['provider']['name']
            # Fetch provider asynchronously
            try:
                provider = await sync_to_async(Provider.objects.get)(name=provider)
            except:
                logger.error(f"Provider with username '{provider}' not found for item {item.id} (offer_id: {item.offer_id})")
                return

            item.provider = provider
            await sync_to_async(item.save)()

            logger.info(f"Successfully updated item with id {item.id}")
        except Exception as e:
            logger.error(f"Error updating item {item.id}: {e}")

    async def main(self):
        """Main async function to fetch and update each item separately."""
        # Get all existing items from the database
        items = await sync_to_async(lambda: list(Edge.objects.filter(provider_id=None)[:10050]))()

        if not items:
            logger.info("No items found in the database to update.")
            return

        headers = self.api['headers'].copy()

        async with aiohttp.ClientSession(headers=headers) as session:
            # Create tasks for each item update
            tasks = [self.update_item(item, session) for item in items]
            await asyncio.gather(*tasks, return_exceptions=True)

    def handle(self, env, *args, **options):
        """Django command entry point."""
        if env == 'prod':
            self.api = self.api_prod

        try:
            # Run the async main function
            asyncio.run(self.main())
            self.stdout.write(self.style.SUCCESS('Successfully updated items'))
        except Exception as e:
            logger.error(f"Error in command: {e}")
            self.stdout.write(self.style.ERROR('Failed to update items'))

    def add_arguments(self, parser):
        # parser.add_argument('--limit', type=int, help='Limit the number of items to update')
        parser.add_argument('env', type=str, help='Environment to run the command in')
