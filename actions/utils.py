def extract_text_from_bio(entities):
    """
    Extracts text for LOCATION and ORGANIZATION entities from a list of entities in BIO format.

    Args:
    entities (list): List of entities, where each entity is a dictionary containing:
        - 'entity' (str): The BIO tag (e.g., 'B-LOCATION', 'I-LOCATION', 'B-ORGANIZATION', 'I-ORGANIZATION').
        - 'word' (str): The word corresponding to the entity.
        - 'start' (int): The start character index of the word.
        - 'end' (int): The end character index of the word.

    Returns:
    str: Concatenated text of LOCATION and ORGANIZATION entities.
    """
    text = []
    current_entity = None
    current_type = None

    for entity in entities:
        entity_tag = entity['entity']
        word = entity['word']

        if entity_tag.startswith('B-'):
            entity_type = entity_tag[2:]
            if entity_type in ['LOCATION', 'ORGANIZATION']:
                # If we encounter a B- tag for LOCATION or ORGANIZATION, we start a new entity
                if current_entity is not None:
                    # If there is an ongoing entity, append it to the text
                    text.append(current_entity)
                current_entity = word
                current_type = entity_type
            else:
                # If it's a different entity type, reset the current entity
                if current_entity is not None:
                    text.append(current_entity)
                current_entity = None
                current_type = None
        elif entity_tag.startswith('I-') and current_entity is not None:
            entity_type = entity_tag[2:]
            if entity_type == current_type:
                # If we encounter an I- tag and it matches the ongoing entity type, continue it
                current_entity += " " + word
            else:
                # If it's a different entity type, reset the current entity
                text.append(current_entity)
                current_entity = None
                current_type = None
        else:
            # If we encounter an O tag or something unexpected, reset the current entity
            if current_entity is not None:
                text.append(current_entity)
                current_entity = None
                current_type = None

    # Append any remaining entity
    if current_entity is not None:
        text.append(current_entity)

    return text