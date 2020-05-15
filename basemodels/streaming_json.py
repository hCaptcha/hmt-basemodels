import ijson
from typing import Callable
from urllib.request import urlopen


def traverse_json_uri(uri: str, callback: Callable) -> int:
  """
    Traverse remote json using streaming api & callback for each top-level entry
  """

  builder = ijson.common.ObjectBuilder()
  depth = -1
  entry_key = None
  entries_count = 0

  for event, value in ijson.basic_parse(urlopen(uri)):
      if event == 'start_map' or event == 'start_array':
          # Skip top level json container
          if depth == -1:
              depth += 1
              continue

          depth += 1

      if event == 'end_map' or event == 'end_array':
          depth -= 1

          # End of top-level entry, callback
          if depth == 0:
              callback(builder.value, entry_key)
              entries_count += 1

      if event == 'map_key':
          # Save entry's key for key-value json
          if depth == 0:
              entry_key = value

      # Consume parsing event
      builder.event(event, value)

  return entries_count
