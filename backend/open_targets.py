import requests

GRAPHQL_URL = "https://api.platform.opentargets.org/api/v4/graphql"

def search_disease(query: str):
    query_str = """
    query searchDisease($queryString: String!) {
      search(queryString: $queryString, entityNames: ["disease"], page: {index: 0, size: 5}) {
        hits {
          id
          name
          description
        }
      }
    }
    """
    
    variables = {"queryString": query}
    try:
        response = requests.post(GRAPHQL_URL, json={"query": query_str, "variables": variables}, timeout=10)
        data = response.json()
        return data.get("data", {}).get("search", {}).get("hits", [])
    except Exception as e:
        print(f"Error searching disease: {e}")
        return []

def get_targets_for_disease(efo_id: str, size: int = 50):
    query_str = """
    query diseaseTargets($efoId: String!, $size: Int!) {
      disease(efoId: $efoId) {
        id
        name
        associatedTargets(page: {index: 0, size: $size}) {
          rows {
            target {
              id
              approvedSymbol
            }
            score
          }
        }
      }
    }
    """
    variables = {"efoId": efo_id, "size": size}
    try:
        response = requests.post(GRAPHQL_URL, json={"query": query_str, "variables": variables}, timeout=10)
        data = response.json()
        disease_data = data.get("data", {}).get("disease", {})
        if not disease_data:
            return None
        
        targets = []
        for row in disease_data.get("associatedTargets", {}).get("rows", []):
            targets.append({
                "id": row["target"]["id"],
                "symbol": row["target"]["approvedSymbol"],
                "score": row["score"]
            })
        return targets
    except Exception as e:
        print(f"Error fetching targets: {e}")
        return []

def get_drugs_for_targets(ensembl_ids: list[str]):
    query_str = """
    query targetsDrugs($ensemblIds: [String!]!) {
      targets(ensemblIds: $ensemblIds) {
        id
        approvedSymbol
        knownDrugs(page: {size: 100}) {
          rows {
            drug {
              id
              name
            }
          }
        }
      }
    }
    """
    # Note: GraphQL limits might apply if we send 50 IDs and each has many drugs.
    # The platform API usually handles this well, but we'll monitor.
    variables = {"ensemblIds": ensembl_ids}
    try:
        response = requests.post(GRAPHQL_URL, json={"query": query_str, "variables": variables}, timeout=20)
        data = response.json()
        targets_data = data.get("data", {}).get("targets", [])
        
        result = {}
        for target in targets_data:
            symbol = target["approvedSymbol"]
            drugs = target.get("knownDrugs", {}).get("rows", [])
            for row in drugs:
                d = row["drug"]
                drug_id = d["id"]
                drug_name = d["name"]
                if drug_id not in result:
                    result[drug_id] = {
                        "name": drug_name,
                        "targets": set()
                    }
                result[drug_id]["targets"].add(symbol)
                
        return result
    except Exception as e:
        print(f"Error fetching drugs: {e}")
        return {}
