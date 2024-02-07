from fastapi import APIRouter, Request, Response, status
from mysql.connector.conversion import MySQLConverter

from utils.database_connector import cursor, db
from utils.authentication import get_session_token_from_request

router = APIRouter()

@router.get("/")
async def get_properties():
    cursor.execute("SELECT * FROM Properties ORDER BY id asc;")
    properties = cursor.fetchall()

    cursor.execute("SELECT property_id, alt_description FROM Images WHERE image_number=1 ORDER BY property_id asc;")
    images = cursor.fetchall()

    for i in range(len(properties)):
        properties[i]["alt_description"] = images[i]["alt_description"]

    return properties

@router.get("/{property_id}/is_saved")
async def is_property_saved(property_id: str, request: Request, response: Response):
    session_token = get_session_token_from_request(request)

    if session_token == "":
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return

    # Gets a list of properties with the property_id and session_token
    cursor.execute("SELECT property_id FROM SavedProperties sp JOIN Users u ON sp.user_id = u.id WHERE sp.property_id=%s AND u.session_token=%s", (property_id, session_token))
    properties = cursor.fetchall()

    # Length = 0 if the property isn't saved
    if len(properties) == 0:
        return False

    else:
        return True
    
@router.get("/search")
async def search_properties(sort_by: str = "", property_type: str = "", min_bedrooms: int = 0, min_showers: int = 0, noise_level: int = 0, name: str = ""):
    query = "SELECT * FROM Properties WHERE 1=1"
    placeholders = []

    if property_type != "":
        query = query + " AND property_type = %s"
        placeholders.append(property_type)
    
    if min_bedrooms != 0:
        query = query + " AND bedrooms >= %s"
        placeholders.append(min_bedrooms)

    if min_showers != 0:
        query = query + " AND showers >= %s"
        placeholders.append(min_showers)

    if noise_level != 0:

        # noise_level will be either 1, 4 or 7:
        # 1 - Quiet (noise level of 1-3)
        # 4 - Moderate (noise level of 4-6)
        # 7 - Loud (noise level of 7-10)
        if noise_level == 1:
            query = query + " AND noise_level BETWEEN 1 AND 3"
        
        elif noise_level == 4:
            query = query + " AND noise_level BETWEEN 4 AND 6"

        else:
            query = query + " AND noise_level BETWEEN 7 AND 10"

    
    if name != "":
        query = query + " AND name LIKE %s"
        placeholders.append("%" + name + "%")

    # Sorts the properties
    if sort_by != "":
        
        sort_by_split = sort_by.split()
        sort_by_split[0] = MySQLConverter().escape(sort_by_split[0])
        sort_by_split[1] = MySQLConverter().escape(sort_by_split[1]).upper()

        query = query + " ORDER BY {} {}".format(sort_by_split[0], sort_by_split[1])


    properties = []

    # If no placeholders (%s) were used, just run the query
    if len(placeholders) == 0:
        cursor.execute(query)
        properties = cursor.fetchall()
    else:
        cursor.execute(query, tuple(placeholders))
        properties = cursor.fetchall()
    
    return properties

@router.get("/{property_id}")
async def get_property(property_id: str):
    # Gets all the information about a property
    cursor.execute("SELECT * FROM Properties WHERE id=%s;", (property_id,))
    return cursor.fetchone()
