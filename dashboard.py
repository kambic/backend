import json
import os
from datetime import datetime
from pathlib import Path

import django
from loguru import logger
from tqdm import tqdm

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.settings")

django.setup()
from vod.models import Stream, Offer

mtcms = Path("mtcms-stag-response.json")

data = json.loads(mtcms.read_text())

logger.info(f"{len(data)} videos found")
logger.info(f"Processing offers...")
logger.info(f"{Offer.objects.count()} Exists in DB")
offers = []
streams_updated = []
streams_created = []

env = 'prod' if 'prod' in mtcms.name else 'stag'


for item in tqdm(data, desc="Processing offers", unit="offer"):


    expired = item['expired']

    videoUrls = item['videoURLs']

    try:

        offerId = item['mappedOfferId']
    except KeyError:
        logger.warning(f"No mappedOfferId for {item}")
        continue

    expired = datetime.fromisoformat(expired)

    _offer = Offer.objects.filter(offer_id=offerId, env=env)

    if _offer.exists():
        _offer = _offer.get()
    else:
        _offer = Offer(offer_id=offerId, expiration_date=expired, env=env)

    _offer.save()


    for uri in videoUrls:
        stream = Stream.objects.filter(uri=uri['videoURL'])
        if stream.exists():
            stream = stream.get()
            stream.offer = _offer
            stream.save()
        else:

            stream = Stream(uri=uri['videoURL'], offer=_offer)
            stream.save()
1
