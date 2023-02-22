"""Sync data."""
# -*- coding: utf-8 -*-

import logging
from datetime import datetime,timezone
from typing import Callable, Optional

import singer
from singer.catalog import Catalog, CatalogEntry

from tap_wincher import tools
from tap_wincher.wincher import Wincher
from tap_wincher.streams import STREAMS
LOGGER: logging.RootLogger = singer.get_logger()



def sync(
    wincher: Wincher,
    state: dict,
    catalog: Catalog,
    start_date: str,
    ) -> None:
    """ Sync data from tap source.
    
    Arguments:
        wincher {Wincher} -- Wincher client
        state {dict} -- Tap state
        catalog {Catalog} -- Stream catalog
        start_date {str} -- Start date
     """
    LOGGER.info('Sync')
    LOGGER.debug('Current state: \n{state}')

    # Loop over selected streams in catalog
    for stream in catalog.get_selected_streams(state):
        LOGGER.info("Syncing stream:" + stream.tap_stream_id)

        #Update the current stream as active syncing in the state
        singer.set_currently_syncing(state, stream.tap_stream_id)

        stream_state: dict = tools.get_stream_state(
            state,
            stream.tap_stream_id,
        )

        LOGGER.debug(f'Stream state: {stream_state}')

        #Wrtie the schema
        singer.write_schema(
            stream_name = stream.tap_stream_id,
            schema = stream.schema.to_dict(),
            key_properties = stream.key_properties,
        )

        #Every stream has a corresponding method
        tap_data: Callable = getattr(wincher, stream.tap_stream_id)

        for row in tap_data(**stream_state):
            sync_record(stream, row, state)

def sync_record(stream: CatalogEntry, row: dict, state: dict) -> None:
    """Sync the record.
    Arguments:
        stream {CatalogEntry} -- Stream catalog
        row {dict} -- Record
        state {dict} -- State
    """

    # Retrieve the value of the bookmark
    bookmark: Optional[str] = tools.retrieve_bookmark_with_path(
        stream.replication_key,
        row,
    )

    
    #create new bookmark
    new_bookmark: str = tools.create_bookmark(stream.tap_stream_id, bookmark)

    #Write a row to the stream
    singer.write_record(
        stream.tap_stream_id,
        row,
        time_extracted = datetime.now(timezone.utc),
    )

    if new_bookmark:
        #save the bookmark to the state
        singer.write_bookmark(
            state,
            stream.tap_stream_id,
            STREAMS[stream.tap_stream_id]['bookmark'],
            new_bookmark,
        )

        #clear currently syncing
        tools.clear_currently_syncing(state)

        #write the bookmark
        singer.write_state(state)

