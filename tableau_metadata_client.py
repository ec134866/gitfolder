import requests
import json

class TableauMetadataClient:
    def __init__(self, server_name, api_version, site_content_url=""):
        """Initialize the Tableau Metadata API client"""
        self.server_name = server_name
        self.api_version = api_version
        self.site_content_url = site_content_url
        self.auth_token = None
        
        # API endpoints
        self.signin_url = f"https://{server_name}/api/{api_version}/auth/signin"
        self.signout_url = f"https://{server_name}/api/{api_version}/auth/signout"
        self.metadata_url = f"https://{server_name}/api/metadata/graphql"
    
    def sign_in(self, pat_name, pat_secret):
        """Sign in using Personal Access Token"""
        payload = {
            "credentials": {
                "personalAccessTokenName": pat_name,
                "personalAccessTokenSecret": pat_secret,
                "site": {
                    "contentUrl": self.site_content_url
                }
            }
        }
        
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }
        
        try:
            response = requests.post(self.signin_url, json=payload, headers=headers)
            response.raise_for_status()
            
            data = response.json()
            self.auth_token = data["credentials"]["token"]
            
            print("Sign in successful!")
            return True
            
        except requests.exceptions.RequestException as e:
            print(f"Sign in failed: {e}")
            return False
    
    def query_metadata(self, graphql_query, output_filename):
        """Execute a GraphQL query and save to JSON file"""
        if not self.auth_token:
            print("Not authenticated. Please sign in first.")
            return None
        
        headers = {
            'X-Tableau-Auth': self.auth_token,
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        
        payload = {
            "query": graphql_query
        }
        
        try:
            response = requests.post(self.metadata_url, json=payload, headers=headers)
            response.raise_for_status()
            
            result = response.json()
            
            # Save to JSON file
            with open(f"{output_filename}.json", 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            
            print(f"Query result saved to: {output_filename}.json")
            return result
            
        except requests.exceptions.RequestException as e:
            print(f"Metadata query failed: {e}")
            return None
        except IOError as e:
            print(f"Failed to save file: {e}")
            return None
    
    def sign_out(self):
        """Sign out and invalidate the auth token"""
        if not self.auth_token:
            print("Not signed in")
            return
        
        headers = {
            'X-Tableau-Auth': self.auth_token,
            'Content-Type': 'application/json'
        }
        
        try:
            response = requests.post(self.signout_url, headers=headers, data=b'')
            response.raise_for_status()
            
            self.auth_token = None
            print("Sign out successful!")
            
        except requests.exceptions.RequestException as e:
            print(f"Sign out failed: {e}")

# Example usage
if __name__ == "__main__":
    # Configuration - REPLACE WITH YOUR VALUES
    SERVER_NAME = "your-server.com"  # For Tableau Cloud: "tableau.byu.edu"
    API_VERSION = "3.23" # or whatever API version 
    SITE_CONTENT_URL = ""  # Empty for default site, or "YourSiteName"
    PAT_NAME = "your-pat-name"
    PAT_SECRET = "your-pat-secret"

    # Tableau Cloud/Server version	REST API version	Schema version
    # 2025.1	3.25	3.25
    # 2024.2	3.23	3.23
    # 2023.3	3.21	3.21
    # 2023.1	3.19	3.19
    # 2022.3	3.17	3.17
    # 2022.1	3.15	3.15
    # 2021.4	3.14	3.14
    # 2021.3	3.13	3.13
    # 2021.2	3.12	3.12
    # 2021.1	3.11	3.11
    # 2020.4	3.10	3.10
    # 2020.3	3.9	3.9
    # 2020.2	3.8	3.8
    # 2020.1	3.7	3.7
    
    # Initialize client
    client = TableauMetadataClient(SERVER_NAME, API_VERSION, SITE_CONTENT_URL)
    
    # Sign in
    if client.sign_in(PAT_NAME, PAT_SECRET):
        
        # Example GraphQL query - get all databases
        all_databases = """
        query getDatabases {
            databases {
                name
                id
                connectionType
                tables {
                    name
                    id
                }
            }
        }
        """

        # Get specific database by name
        specific_database = """
        query getSpecificDatabase {
            databases(filter: {name: "your-database-name"}) {
                name
                tables {
                    name
                    columns {
                        name
                        remoteType
                    }
                }
            }
        }
        """

        # Get all data sources
        all_datasources = """
        query getDataSources {
            publishedDatasources {
                name
                id
                hasExtracts
                extractLastRefreshTime
                owner {
                    name
                }
            }
        }
        """

        # Get workbook details
        workbook_details = """
        query getWorkbookDetails {
            workbooks {
                name
                sheets {
                    name
                }
                embeddedDatasources {
                    name
                    upstreamTables {
                        name
                        database {
                            name
                        }
                    }
                }
                upstreamDatasources {
                    name
                    upstreamTables {
                        name
                        database {
                            name
                        }
                    }
                }
            }
        }
        """


        # Get embedded and server data sources, their fields, and derived calculated fields with assosciated formulas
        workbook_details = """
        query superstoreMap {
            workbooks(filter: { name: "Superstore map" }) {
                name
                owner {
                id
                username
                }
                embeddedDatasources {
                name
                fields {
                    name
                    referencedByCalculations {
                    name
                    dataType
                    formula
                    }
                }
                }
                upstreamDatasources {
                name
                fields {
                    name
                    referencedByCalculations {
                    name
                    dataType
                    formula
                    }
                }
                }
            }
            }
        """   

        # Get any custom sql queries written in Tableau
        workbook_details = """
        query customSql {
            customSQLTables {
                name
                isCertified
                query
            }
            }  
         """  
        


        ## unique field usage by data source  - how much of our written data is used vs not used?
        ## number of calculated fields by user? 
        ## number of calculated fields by data source? - can this identify that should write something for before it hits tableau?


        # Execute query
        print("Querying workbooks...")
        client.query_metadata(workbook_details, "workbook_details")
        
        # Sign out when done
        client.sign_out()


