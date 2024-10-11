def query_db(db, collection, queryBy, queryValue, queryLimit):
    results = {"data": []}
    print(f"COLLECTION OBJECT: {collection}")
    try:
        rsp = db.get_collection(collection).find({queryBy: queryValue}).limit(int(queryLimit))
    except Exception as e:
        return print(e)
    
    for data in rsp:
        data = {str(key): str(value) for key, value in data.items()}
        results["data"].append(data)
    
    return results


