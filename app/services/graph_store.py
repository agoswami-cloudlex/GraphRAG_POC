
import yaml
from graphrag.api.index import build_index
from graphrag.config.create_graphrag_config import create_graphrag_config
import os
from dotenv import load_dotenv
load_dotenv()
class GraphStore:
	async def query(
		self,
		query: str,
		config_path: str = "./ragtest/settings.yaml",
		output_dir: str = "output",
		community_level: int = 1,
		response_type: str = "default",
		dynamic_community_selection: bool = True
	) -> dict:
		"""
		Route query to global, local, or drift search based on query type.
		"""
		import pandas as pd
		from graphrag.api.query import global_search, local_search, drift_search

		with open(config_path, "r") as f:
			config_dict = f.read()
		config_dict = os.path.expandvars(config_dict)
		config_dict = yaml.safe_load(config_dict)
		print(config_dict)
		config = create_graphrag_config(config_dict)

		entities = pd.read_parquet(f"{output_dir}/entities.parquet")
		communities = pd.read_parquet(f"{output_dir}/communities.parquet")
		community_reports = pd.read_parquet(f"{output_dir}/community_reports.parquet")
		text_units = pd.read_parquet(f"{output_dir}/text_units.parquet")
		relationships = pd.read_parquet(f"{output_dir}/relationships.parquet")
		covariates_path = f"{output_dir}/covariates.parquet"
		if os.path.exists(covariates_path):
			covariates = pd.read_parquet(covariates_path)
		else:
			covariates = None

		# Routing logic
		global_keywords = ["summary", "theme", "overall", "corpus", "dataset", "all documents"]
		drift_keywords = ["community", "cluster", "drift", "insight", "expand"]

		query_lower = query.lower()
		if any(kw in query_lower for kw in global_keywords):
			response, context = await global_search(
				config,
				entities,
				communities,
				community_reports,
				community_level,
				dynamic_community_selection,
				response_type,
				query
			)
			return {"mode": "global", "response": response, "context": context}
		elif any(kw in query_lower for kw in drift_keywords):
			response, context = await drift_search(
				config,
				entities,
				communities,
				community_reports,
				text_units,
				relationships,
				covariates,
				community_level,
				response_type,
				query
			)
			return {"mode": "drift", "response": response, "context": context}
		else:
			response, context = await local_search(
				config,
				entities,
				communities,
				community_reports,
				text_units,
				relationships,
				covariates,
				community_level,
				response_type,
				query
			)
			return {"mode": "local", "response": response, "context": context}
	async def run_indexing(self, config_path: str = "./ragtest/settings.yaml") -> None:
		"""
		Run the GraphRAG indexing pipeline using the provided config file.
		"""
		with open(config_path, "r") as f:
			config_dict = f.read()
		config_dict = os.path.expandvars(config_dict)
		config_dict = yaml.safe_load(config_dict)
		print(config_dict)
		config = create_graphrag_config(config_dict)
		results = await build_index(config)
		print("Indexing complete. Results:", results)

graph_store = GraphStore()


