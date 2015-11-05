from dbco import *
from collections import defaultdict
import wikidata as wd

def find_entity_ids_from_qdocs(limit=10):
	'''Returns a set with all the entities used in discovered articles'''

	articles = db.qdoc.find(
		{ "$query": { "entities": { "$exists": True } },  # Find all articles that have an entities field
		"$orderby": { '_id' : -1 } },  # Sort by latest entries
		{ "entities": 1}  # Only want to get back the entities fields for these articles
		).limit(limit)

	# Map articles to sets of their entities
	entitySets = map(lambda article: set(article['entities']), articles)

	# Union all the sets of entities togeter, get one set of all entities found
	entities = set().union(*entitySets)

	# Ensure no None values in our entities
	entities.discard(None)

	# Converts each entity from unicode to str
	cleaned_entity_ids = {str(entity) for entity in entities}

	return cleaned_entity_ids

def storeEntities(entities):
	desiredProperties = [wd.PROP_INSTANCEOF, wd.PROP_INSTANCEOF]
	for entity in entities:
		if db.entities.find({"_id": entity}).count() == 0:
		    properties = wd.propertyLookup(entity, desiredProperties)
		    nonNullProperties = []
		    for key, value in properties:
		        if value is not None:
		            nonNullProperties[key] = value
		    db.entities.insert_one({"_id": entity, "Title": wd.getTitle(entity), "Aliases": wd.getAliases(entity), "Properties": nonNullProperties})


def find_wikidata_entity_info(entityIds):

	desiredProperties = [
	wd.PROP_CONTAINEDBY,
	# wd.PROP_INSTANCEOF,
	# wd.PROP_HEADOFSTATE,
	# wd.PROP_LEGISLATIVEBODY,
	wd.PROP_GEOLOCATION,
	]

	entries = {}

	wd_lookup = wd.WikidataEntityLookup()

	entities = []

	for entityId in entityIds:
		properties = wd_lookup.find_properties(entityId, desiredProperties)
		useful_properties = [prop for prop in properties if prop]

		entity = {}
		entity['properties'] = useful_properties
		entity['description'] = ''
		entity['$id'] = entityId

		entities.append(entity)

	return entities


def main():
	entity_ids = find_entity_ids_from_qdocs(1)
	updated_entities = find_wikidata_entity_info(entity_ids)


if __name__ == "__main__":
    main()